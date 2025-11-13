from datetime import datetime, timedelta
import logging
from typing import Dict, List

from pydantic import BaseModel

from src.core.chroma_database import ChromaDatabase

from config import chroma_configuration

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("api_ingestor")


class ArticleResponse(BaseModel):
    articles: List[Dict]
    from_date: datetime
    to_date: datetime


class ArticlesRetriever:

    def __init__(self):
        self.chroma_db = ChromaDatabase(collection_name=chroma_configuration["collection_name"])

    def parse_chroma_results(self, results: Dict) -> List[Dict]:
        items = []
        for _id, doc, metadata in zip(results["ids"], results["documents"], results["metadatas"]):
            item = {
                "id": _id,
                "document": doc,
                "metadata": metadata,
            }
            items.append(item)
        return items

    def get_articles(self, from_date: datetime, to_date: datetime, limit: int) -> ArticleResponse:
        if not to_date:
            chroma_filter = {"ingestion_date": from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")}
            to_date = from_date + timedelta(days=1)

        else:
            from_date_ts = from_date.timestamp()
            to_date_ts = to_date.timestamp()
            chroma_filter = {
                "$and": [
                    {"timestamp": {"$gte": from_date_ts}},
                    {"timestamp": {"$lte": to_date_ts}},
                ]
            }

        results = self.chroma_db.search_with_filter(
            chroma_filter=chroma_filter,
            limit=limit,
        )

        return ArticleResponse(
            articles=self.parse_chroma_results(results),
            from_date=from_date,
            to_date=to_date,
        )

    def get_articles_by_topic(
        self, topic: str, from_date: datetime, to_date: datetime, limit: int
    ) -> ArticleResponse:

        if not to_date:
            chroma_filter = {
                "$and": [
                    {"topic": topic},
                    {"ingestion_date": from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")}
                ]
            }
            to_date = from_date + timedelta(days=1)

        else:
            from_date_ts = from_date.timestamp()
            to_date_ts = to_date.timestamp()
            chroma_filter = {
                "$and": [
                    {"topic": topic},
                    {"timestamp": {"$gte": from_date_ts}},
                    {"timestamp": {"$lte": to_date_ts}},
                ]
            }
        results = self.chroma_db.search_with_filter(
            chroma_filter=chroma_filter,
        )
        return ArticleResponse(
            articles=self.parse_chroma_results(results),
            from_date=from_date,
            to_date=to_date,
        )
