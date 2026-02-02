import logging
import random
from typing import Dict, List

from api.models.articles import ArticleResponse, ArticleSearchRequest
from src.core.chroma_database import ChromaDatabase

from config import chroma_configuration

logger = logging.getLogger("articles_retriever")
logger.setLevel(logging.INFO)


class ArticlesRetriever:
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
        items.sort(key=lambda x: x["metadata"].get("timestamp", ""), reverse=True)
        return items

    def search(self, request: ArticleSearchRequest) -> ArticleResponse:
        generic_conditions = []
        if request.topic:
            generic_conditions.append({"topic": request.topic})

        if request.date_range.from_date and request.date_range.to_date:
            generic_conditions.append(
                {"timestamp": {"$gte": request.date_range.from_date.timestamp()}}
            )
            generic_conditions.append(
                {"timestamp": {"$lte": request.date_range.to_date.timestamp()}}
            )

        all_parsed_results = []

        if not request.sources:
            chroma_filter = {}
            if len(generic_conditions) > 1:
                chroma_filter = {"$and": generic_conditions}
            elif len(generic_conditions) == 1:
                chroma_filter = generic_conditions[0]

            results = self.chroma_db.search_with_filter(
                chroma_filter=chroma_filter,
                limit=request.limit,
            )
            all_parsed_results = self.parse_chroma_results(results)

        # distributed search across specified sources
        else:
            num_sources = len(request.sources)
            limit_per_source = request.limit // num_sources

            for source in request.sources:
                source_conditions = list(generic_conditions)
                source_conditions.append({"source": source})

                if len(source_conditions) > 1:
                    chroma_filter = {"$and": source_conditions}
                else:
                    chroma_filter = source_conditions[0]

                results = self.chroma_db.search_with_filter(
                    chroma_filter=chroma_filter,
                    limit=limit_per_source,
                )
                source_results = self.parse_chroma_results(results)
                all_parsed_results.extend(source_results)

        random.shuffle(all_parsed_results)

        return ArticleResponse(
            num_articles=len(all_parsed_results),
            articles=all_parsed_results,
            topic=request.topic,
            source=request.sources,
            from_date=request.date_range.from_date,
            to_date=request.date_range.to_date,
        )
