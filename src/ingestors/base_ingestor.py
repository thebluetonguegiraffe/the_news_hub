from abc import ABC
import logging
from typing import Dict
from src.core.chroma_database import ChromaDatabase
from src.core.translator import GoogleTranslator
from langgraph.graph import END

from config import chroma_configuration


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("base_ingestor")


class BaseIngestor(ABC):

    def __init__(self):
        self.chroma_db = ChromaDatabase(collection_name=chroma_configuration["collection_name"])
        self.translator = GoogleTranslator(self.LANGUAGE)

    def _is_url_scraped(self, url):
        try:
            result = self.chroma_db.search_with_filter(chroma_filter={"url": url}, limit=1)
            return len(result["ids"]) > 0
        except Exception:
            return False

    def translate_documents_node(self, state: Dict) -> Dict:
        """
        Translate title and description fields of the documents
        """
        articles_md = state["articles_md"]

        for md in articles_md:
            title = md.get(f"title_{self.LANGUAGE}")
            description = md.get(f"description_{self.LANGUAGE}")

            if not title or not description:
                logger.warning("Missing title or description in metadata, skipping translation.")

            for language in self.dest_lang:
                md[f"title_{language}"] = self.translator.translate(title, target_lang=language)
                md[f"description_{language}"] = self.translator.translate(
                    description, target_lang=language
                )

        return {"articles_md": articles_md}

    def finish_graph(self, state: Dict) -> Dict:
        articles_md = state["articles_md"]
        if not articles_md:
            logger.warning(f"No new documents to ingest in {self.source}, ending workflow.")
            return END
        logger.warning(f"{len(articles_md)} new documents to ingest for {self.source}")
        return "articles_translator"
