from abc import ABC
import logging
from typing import Dict
from src.core.chroma_database import ChromaDatabase
from src.core.translator import GoogleTranslator
from langgraph.graph import END

from config import chroma_configuration


logger = logging.getLogger("base_ingestor")
logger.setLevel(logging.INFO)


class BaseIngestor(ABC):

    def __init__(self):
        self.chroma_db = ChromaDatabase(collection_name=chroma_configuration["collection_name"])
        self.translator = GoogleTranslator(self.LANGUAGE)

    def _is_url_scraped(self, url: str) -> bool:
        try:
            result = self.chroma_db.search_with_filter(chroma_filter={"url": url}, limit=1)
            return len(result["ids"]) > 0
        except Exception:
            return False

    def translate_documents_node(self, state: Dict) -> Dict:
        """
        Translate title and description fields of the documents.

        All articles are translated in one batch per field and language, so the
        whole run costs a handful of requests instead of one per field. An
        article whose translation fails keeps its original-language text rather
        than bringing the whole ingestion down.
        """
        articles_md = state["articles_md"]

        translatable = []
        for md in articles_md:
            if md.get(f"title_{self.LANGUAGE}") and md.get(f"description_{self.LANGUAGE}"):
                translatable.append(md)
            else:
                logger.info("Missing title or description in metadata, skipping translation.")

        for language in self.dest_lang:
            for field in ("title", "description"):
                originals = [md[f"{field}_{self.LANGUAGE}"] for md in translatable]
                translations = self.translator.translate_batch(originals, target_lang=language)

                for md, original, translated in zip(translatable, originals, translations):
                    if not translated:
                        logger.warning(
                            f"Falling back to untranslated {field}_{language} "
                            f"for {md.get('url')}"
                        )
                        translated = original
                    md[f"{field}_{language}"] = translated

        return {"articles_md": articles_md}

    def finish_graph(self, state: Dict) -> Dict:
        articles_md = state["articles_md"]
        if not articles_md:
            logger.info(f"No new documents to ingest in {self.source}, ending workflow.")
            return END
        logger.info(f"{len(articles_md)} new documents to ingest for {self.source}")
        return "articles_translator"
