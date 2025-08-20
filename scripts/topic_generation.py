

import json
import logging

from collections import defaultdict
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from scripts.constants import TOPICS
from news_rs.src.custom_chatmodel import CustomChatModel
from src.config import db_configuration, sql_db_configuration
from src.sql_client import TopicsDBClient
from src.vectorized_database import VectorizedDatabase

from templates.news_templates import topic_generation_template, topic_description_template
import argparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate topics for clustered news articles.")
    parser.add_argument("--dry-run", action="store_true", help="Run the script without updating the database.", default=False)

    args = parser.parse_args()
    dry_run = args.dry_run

    project_root = Path(__file__).resolve().parent.parent
    db_path = db_configuration["db_path"]
    collection_name = db_configuration["collection_name"]

    chroma = VectorizedDatabase(
        persist_directory=f"{project_root}/db/{db_path}",
        collection_name=collection_name
    )

    collection = chroma.get_collection()

    documents_dict = collection.get(include=["embeddings", "metadatas", "documents"])

    documents = documents_dict["documents"]
    ids = documents_dict["ids"]
    embeddings = documents_dict["embeddings"]

    date = documents_dict["metadatas"][0]["date"]

    logger.info('Documents retrieved from Chroma DB')

    n_components = 90
    pca = PCA(n_components=n_components)
    embeddings_reduced = pca.fit_transform(embeddings)

    n_clusters = 15
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings_reduced)

    clusters = defaultdict(list)
    for doc, _id, label in zip(documents, ids, labels):
        clusters[label].append({"document": doc, "id": _id})

    logger.info('Clusters Generated')

    prompt = CustomChatModel.create_prompt_template(topic_generation_template)
    llm = CustomChatModel.from_config()

    chain = prompt | llm

    label_map =  {}
    for cluster_id, cluster_content in clusters.items():
        documents = [content["document"] for content in cluster_content]
        ids = [content["id"] for content in cluster_content]

        topic = chain.invoke(
            {   
                "documents": ", ".join(documents),
                "initial_topics": ", ".join(TOPICS.keys()),
            }
        )

        if not dry_run:
            collection.update(
                ids=ids,
                metadatas=[{"topic": topic.content}] * len(ids)
            )
            logger.info(f'Topic updated for cluster {cluster_id}: {topic.content}')
        label_map[int(cluster_id)] = topic.content

    clusters_named = {
        label_map[cluster_id]: docs
        for cluster_id, docs in clusters.items()
    }