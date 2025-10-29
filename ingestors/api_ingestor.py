from datetime import timedelta, datetime
import logging
import os
from typing import Dict, TypedDict, List

import requests
from ingestors.base_ingestor import BaseIngestor
from src.core.finlight_api_client import FinlightAPIClient
from src.models.chroma_models import ChromaDoc, Metadata

from langgraph.graph import StateGraph, START, END

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("api_ingestor")


class State(TypedDict):
    articles_raw: List[Dict]
    articles_md: List[Dict]


class APIIngestor(BaseIngestor):
    API_PAGE_SIZE = 100
    LANGUAGE = "en"
    DEST_LANG = {"es", "ca"}

    def __init__(self, source: str, date: datetime):
        super().__init__()
        self.source = source
        self.end_date = datetime.strptime(date, "%Y-%m-%dT%H:%M")
        self.start_date = self.end_date - timedelta(days=1)
        self.api_client = FinlightAPIClient(
            base_url="https://api.finlight.me/v2/",
            headers={"X-API-KEY": os.getenv("FINLIGHT_API_TOKEN")},
        )
        self.api_endpoint = "articles/"
        self.dest_lang = self.DEST_LANG

    def query_api(self, state: State) -> Dict:
        try:
            response = self.api_client.post(
                endpoint=self.api_endpoint,
                json={
                    "sources": [self.source],
                    "from": self.start_date.strftime("%Y-%m-%dT%H:%M"),
                    "to": self.end_date.strftime("%Y-%m-%dT%H:%M"),
                    "pageSize": self.API_PAGE_SIZE,
                },
            )

            articles = response.get("articles", [])
            if not articles:
                raise ValueError(
                    f"No articles found for source {self.source} on {self.start_date}."
                )
            return {"articles_raw": articles}
        except requests.exceptions.HTTPError as e:
            raise ValueError(f"HTTP error occurred: {e}")

    def parse_articles_node(self, state: State):
        articles_raw = state["articles_raw"]
        articles_md = []
        for article in articles_raw:
            url = article.get("link")
            title = article.get("title")
            summary = article.get("summary")

            if not title or not summary:
                logger.warning(f"Article at {url} is missing title or summary, skipping.")
                continue

            if not self._is_url_scraped(url):
                articles_md.append(self.api_client.parse(article, self.end_date))

        return {"articles_md": articles_md}

    def articles_db_insert_node(self, state: State) -> Dict:
        articles_md = state["articles_md"]

        chroma_docs = {}
        for md in articles_md:
            doc = ChromaDoc(
                document=md.get("title_en") + ". " + md.get("description_en"),
                metadata=Metadata(
                    url=md.get("url"),
                    title=md.get("title_en"),
                    title_es=md.get("title_es"),
                    title_ca=md.get("title_ca"),
                    excerpt=md.get("description_en"),
                    excerpt_es=md.get("description_es"),
                    excerpt_ca=md.get("description_ca"),
                    image=md.get("image"),
                    source=self.source,
                    published_date=md.get("publish_date"),
                    ingestion_date=self.end_date
                ),
            )
            # avoid duplicate docs
            chroma_docs[doc.id] = doc
        self.chroma_db.add_documents(list(chroma_docs.values()))
        logger.warning(
            f"Total of {len(articles_md)} docs queried and stored in ChromaDB from {self.source}"
        )

    def workflow(self):
        graph_builder = StateGraph(State)

        graph_builder.add_node("query_api", self.query_api)
        graph_builder.add_node("articles_parser", self.parse_articles_node)
        graph_builder.add_node("articles_translator", self.translate_documents_node)
        graph_builder.add_node("articles_db_insert", self.articles_db_insert_node)

        graph_builder.add_edge(START, "query_api")
        graph_builder.add_edge("query_api", "articles_parser")
        graph_builder.add_conditional_edges(
            "articles_parser",  # FROM: The source node
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

    def run(self):
        workflow = self.workflow()
        state = workflow.invoke({})
        return state


if __name__ == "__main__":
    APIIngestor(source="www.bbc.com", date="2025-10-01T00:00").run()
