import logging
from typing import Dict, List, TypedDict
from langgraph.graph import StateGraph, START, END

from ingestors.base_ingestor import BaseIngestor
from src.core.scrapper import SCRAPPER_MAPPER
from src.models.chroma_models import ChromaDoc, Metadata

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("scrapper_ingestor")


class State(TypedDict):
    article_urls: List
    articles_md: List[Dict]


class ScrapperIngestor(BaseIngestor):
    DEST_LANGUAGES = {"en", "es", "ca"}

    def __init__(self, source: str):
        self.source, self.scrapper = SCRAPPER_MAPPER[source]
        self.LANGUAGE = self.scrapper.LANGUAGE
        super().__init__()
        self.dest_lang = self.DEST_LANGUAGES - {self.LANGUAGE}

    async def homepage_scrapper_node(self, state: State) -> Dict:
        async with self.scrapper() as scrapper:
            result = await scrapper.scrape_homepage(self.source)
        return {"article_urls": result}

    async def articles_scrapper_node(self, state: State) -> Dict:
        article_urls = state["article_urls"]
        articles_md = []
        async with self.scrapper() as scrapper:
            for url in article_urls:
                if not self._is_url_scraped(url):
                    scraped_article = await scrapper.scrape_article(url)
                    title = scraped_article.get(f"title_{self.LANGUAGE}")
                    description = scraped_article.get(f"description_{self.LANGUAGE}")
                    if not title or not description:
                        logger.warning(
                            f"Missing title or description in metadata, skipping articleL: {url}"
                        )
                        continue
                    articles_md.append(scraped_article)
        return {"articles_md": articles_md}

    def translate_documents_node(self, state: State) -> Dict:
        """
        Scrapped articles have also topic field that needs to be translated
        """
        super().translate_documents_node(state)
        articles_md = state["articles_md"]

        for md in articles_md:
            topic = md.get("topic")
            md["topic"] = self.translator.translate(topic, target_lang="en")

        return {"articles_md": articles_md}

    def articles_db_insert_node(self, state: State) -> Dict:
        article_urls = state["article_urls"]
        articles_md = state["articles_md"]

        chroma_docs = {}
        for url, md in zip(article_urls, articles_md):
            try:
                doc = ChromaDoc(
                    document=md.get("title_en") + ". " + md.get("description_en"),
                    metadata=Metadata(
                        url=url,
                        topic=md.get("topic"),
                        title=md.get("title_en"),
                        title_es=md.get("title_es"),
                        title_ca=md.get("title_ca"),
                        excerpt=md.get("description_en"),
                        excerpt_es=md.get("description_es"),
                        excerpt_ca=md.get("description_ca"),
                        image=[md.get("og:image")],
                        source=self.source,
                        published_date=md.get("article:modified_time"),
                    ),
                )
                # avoid duplicate docs
                chroma_docs[doc.id] = doc
            except Exception as e:
                logger.error(f"Error creating ChromaDoc for URL {url}: {e}")
                continue
        logger.info(f"Total amount of {len(articles_md)} scrapped and stored in ChromaDB")

    def workflow(self):
        graph_builder = StateGraph(State)

        graph_builder.add_node("homepage_scrapper", self.homepage_scrapper_node)
        graph_builder.add_node("articles_scrapper", self.articles_scrapper_node)
        graph_builder.add_node("articles_translator", self.translate_documents_node)
        graph_builder.add_node("articles_db_insert", self.articles_db_insert_node)

        graph_builder.add_edge(START, "homepage_scrapper")
        graph_builder.add_edge("homepage_scrapper", "articles_scrapper")
        graph_builder.add_conditional_edges(
            "articles_scrapper",  # FROM: The source node
            self.finish_graph,  # ROUTER: Function that decides where to go next
            {  # MAPPING: Possible destinations
                END: END,
                "articles_translator": "articles_translator",
            },
        )
        graph_builder.add_edge("articles_translator", "articles_db_insert")
        graph_builder.add_edge("articles_db_insert", END)

        graph = graph_builder.compile()
        return graph

    async def run(self):
        workflow = self.workflow()
        state = await workflow.ainvoke({})
        return state

