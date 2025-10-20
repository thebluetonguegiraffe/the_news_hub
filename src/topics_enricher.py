from collections import defaultdict
from datetime import datetime
import logging
import os
from typing import Dict, List
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate

from src.core.chroma_database import ChromaDatabase
from config import chat_configuration, chroma_configuration, mongo_configuration
from src.core.mongo_client import CustomMongoClient
from templates.news_templates import Prompts

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TopicsEnricher:
    PCA_COMPONENTS = 50
    KMEANS_CLUSTERS = 15

    def __init__(self):
        self.llm = init_chat_model(
            model=chat_configuration["model"],
            model_provider="openai",
            api_key=os.getenv("GITHUB_TOKEN"),
            base_url="https://models.github.ai/inference",
        )
        self.chroma_db = ChromaDatabase(collection_name=chroma_configuration["collection_name"])
        self.prompts = Prompts()
        self.mongo = CustomMongoClient
        self.cached_topics = self.retrieve_cached_topics()

    def clusterize_topics(self, date: str, dry_run: bool = False, force: bool = False):
        if force:
            chroma_filter = {"ingestion_date": date}
        else:
            # only docs that have no topic
            chroma_filter = {"$and": [{"ingestion_date": date}, {"topic": ""}]}

        # retrieve chroma docs based on input date
        chroma_results = self.chroma_db.search_with_filter(
            chroma_filter=chroma_filter,
            include=["embeddings", "metadatas", "documents"],
        )
        ids = chroma_results["ids"]
        if not ids:
            raise ValueError(f"No documents found for date {date}.")

        # create clusters using PCA
        clusters = self.create_pca_clusters(chroma_results=chroma_results)

        named_clusters = {}
        for cluster_id, cluster_content in clusters.items():
            cluster_docs = [content["document"] for content in cluster_content]
            cluster_ids = [content["id"] for content in cluster_content]

            topic = self.get_cluster_topic(cluster_docs=cluster_docs)
            named_clusters[topic] = cluster_content

            if not dry_run:
                self.chroma_db.collection.update(
                    ids=cluster_ids, metadatas=[{"topic": topic}] * len(cluster_ids)
                )
                logger.warning(
                    f"Topic updated for cluster {cluster_id}: {topic} - "
                    f"{len(cluster_ids)} docs"
                )

    def populate_topics_database(self, date: str, dry_run: bool = False):
        if dry_run:
            logger.warning("Dry run enabled, skipping MongoDB update.")

        chroma_results = self.chroma_db.search_with_filter(
            chroma_filter={"ingestion_date": date},
            include=["metadatas"],
        )
        topics = [metadata['topic'] for metadata in chroma_results["metadatas"]]
        self.update_mongo_topics_collection(topics=topics, date=date)

    @classmethod
    def create_pca_clusters(cls, chroma_results) -> Dict[str, List]:
        documents = chroma_results["documents"]
        embeddings = chroma_results["embeddings"]
        ids = chroma_results["ids"]
        metadatas = chroma_results["metadatas"]

        n_components = min(cls.PCA_COMPONENTS, len(embeddings))
        pca = PCA(n_components=n_components)
        embeddings_reduced = pca.fit_transform(embeddings)

        n_clusters = cls.KMEANS_CLUSTERS
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings_reduced)

        clusters = defaultdict(list)
        for doc, _id, metadata, label in zip(documents, ids, metadatas, labels):
            clusters[label].append({"document": doc, "id": _id, "metadatas": metadata})
        return clusters

    def get_cluster_topic(self, cluster_docs: List[str]) -> str:
        prompt = ChatPromptTemplate.from_messages(
            [("system", self.prompts.TOPIC_GENERATION_TEMPLATE)]  # system?
        )
        chain = prompt | self.llm
        topic = chain.invoke(
                {
                    "documents": ", ".join(cluster_docs),
                    "cached_topics": ", ".join(self.cached_topics),
                }
            )
        return topic.content.lower()

    def retrieve_cached_topics(self) -> List[str]:
        with self.mongo() as client:
            db = client[mongo_configuration["db"]]
            mongo_collection = db[mongo_configuration["collection"]]
            result = mongo_collection.find({}, {"_id": 1})
            if result:
                retrieved_topics = [topic["_id"] for topic in result]
                logger.warning(
                    f"{len(retrieved_topics)} topics successfully retrieved from Mongo DB"
                )
                return retrieved_topics
            else:
                logger.warning("No cached topics to retrieve.")
                return []

    def update_mongo_topics_collection(self, topics: List[str], date: datetime) -> List[str]:
        non_cached_topics = set(topics) - set(self.cached_topics)

        # create new topics documents for MongoDB
        new_mongo_documents = []
        for topic in non_cached_topics:
            n_docs = topics.count(topic)
            new_mongo_documents.append(
                {
                    "_id": topic,
                    "description": self.get_topic_description(topic=topic),
                    "topics_per_day": [{"date": date, "docs_number": n_docs}],
                }
            )

        with self.mongo() as client:
            db = client[mongo_configuration["db"]]
            mongo_collection = db[mongo_configuration["collection"]]

            # insert new topics
            if new_mongo_documents:
                mongo_collection.insert_many(
                    new_mongo_documents
                )
                logger.warning(f"{len(new_mongo_documents)} new topics updated in MongoDB")

            # update existing topics
            for topic in self.cached_topics:
                n_docs = topics.count(topic)
                mongo_collection.update_one(
                    filter={"_id": topic},
                    update={
                        "$addToSet": {
                            "topics_per_day": {"date": date, "docs_number": n_docs},
                        }
                    },
                    upsert=True,
                )
            logger.warning(f"{len(self.cached_topics)} existing topics updated in MongoDB")

    def get_topic_description(self, topic: str) -> str:
        prompt = ChatPromptTemplate.from_messages(
            [("system", self.prompts.TOPIC_DESCRIPTION_TEMPLATE)]
        )
        chain = prompt | self.llm
        topic_description = chain.invoke({"topic": topic})
        logger.warning(f"Description generated for topic: {topic}")
        return topic_description.content.lower()


if __name__ == "__main__":
    topics_descriptor = TopicsEnricher()
    # topics_descriptor.clusterize_topics(date="2025-10-17T23:55:00.000Z", force=True)
    topics_descriptor.populate_topics_database(date="2025-10-17T23:55:00.000Z")
