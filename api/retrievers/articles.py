import logging
from typing import Dict, List

from api.models.articles import ArticleResponse, ArticleSearchRequest
from src.core.chroma_database import ChromaDatabase

from config import chroma_configuration

logger = logging.getLogger("articles_retriever")
logger.setLevel(logging.INFO)


class ArticlesRetriever:
    LANGUAGE_SOURCES = {
        "en": {
            "www.bbc.com",
            "www.nytimes.com",
            "www.theguardian.com",
            "www.thewashingtonpost.com",
        },
        "ca": {"https://www.ara.cat/", "https://www.lavanguardia.com/"},
        "es": {"https://www.lavanguardia.com/"},
    }

    def __init__(self):
        self.chroma_db = ChromaDatabase(collection_name=chroma_configuration["collection_name"])

    def parse_chroma_results(self, results: Dict) -> List[Dict]:
        if not results or not results.get("ids"):
            return []

        items = []
        for _id, doc, metadata in zip(results["ids"], results["documents"], results["metadatas"]):
            items.append(
                {
                    "id": _id,
                    "document": doc,
                    "metadata": metadata,
                }
            )
        return items

    def search(self, request: ArticleSearchRequest) -> ArticleResponse:

        conditions = []
        if request.topic:
            conditions.append({"topic": request.topic})

        allowed_sources = set()
        if request.language:
            allowed_sources.update(self.LANGUAGE_SOURCES.get(request.language))

        if request.source:
            allowed_sources.update(request.source)

        if allowed_sources:
            conditions.append({"source": {"$in": list(allowed_sources)}})

        if request.date_range.from_date and request.date_range.to_date:
            conditions.append({"timestamp": {"$gte": request.date_range.from_date.timestamp()}})
            conditions.append({"timestamp": {"$lte": request.date_range.to_date.timestamp()}})

        chroma_filter = {}
        if len(conditions) > 1:
            chroma_filter = {"$and": conditions}
        elif len(conditions) == 1:
            chroma_filter = conditions[0]
        results = self.chroma_db.search_with_filter(
            chroma_filter=chroma_filter,
            limit=request.limit,
        )

        parsed_results = self.parse_chroma_results(results)

        return ArticleResponse(
            num_articles=len(parsed_results),
            articles=parsed_results,
            topic=request.topic,
            source=request.source,
            from_date=request.date_range.from_date,
            to_date=request.date_range.to_date,
        )
