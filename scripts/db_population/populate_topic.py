import logging
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from collections import defaultdict
from pymongo import MongoClient
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from config import db_configuration, project_root, mongo_configuration

from src.vectorized_database import VectorizedDatabase
from src.llm_engine import create_prompt_template, create_llm

from templates.news_templates import topic_generation_template
import argparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PCA_COMPONENTS = 50
KMEANS_CLUSTERS = 15
if __name__ == "__main__":

    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Generate topics for clustered news articles.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the script without updating the database.",
        default=False,
    )
    parser.add_argument(
        "-d", "--date", required=True, help="Date for the news articles in format YYYY-MM-DDTHH:MM"
    )
    parser.add_argument(
        "--topics-history", required=True, choices=["LATEST", "DEFAULT"],
    )
    args = parser.parse_args()
    dry_run = args.dry_run

    db_path = db_configuration["db_path"]
    collection_name = db_configuration["collection_name"]

    logger.info("Initializing vectorized database")
    chroma = VectorizedDatabase(
        persist_directory=f"{project_root}/db/{db_path}", collection_name=collection_name
    )

    chroma_collection = chroma.get_collection()

    start_date = args.date + ":00.000000Z"

    documents_dict = chroma_collection.get(
        where={"date": start_date}, include=["embeddings", "metadatas", "documents"]
    )

    if not documents_dict["documents"]:
        raise ValueError(f"No documents found for date {start_date}.")

    documents = documents_dict["documents"]
    ids = documents_dict["ids"]
    embeddings = documents_dict["embeddings"]
    metadatas = documents_dict["metadatas"]

    logger.info("Documents retrieved from Chroma DB")

    n_components = PCA_COMPONENTS
    pca = PCA(n_components=n_components)
    embeddings_reduced = pca.fit_transform(embeddings)

    n_clusters = KMEANS_CLUSTERS
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings_reduced)

    logger.info("PCA computed and KMeans clustering applied")

    clusters = defaultdict(list)
    for doc, _id, metadata, label in zip(documents, ids, metadatas, labels):
        clusters[label].append({"document": doc, "id": _id, "metadatas": metadata})

    logger.info("Clusters Generated")

    prompt = create_prompt_template(topic_generation_template)
    llm = create_llm()

    chain = prompt | llm

    label_map = {}

    with MongoClient(
            host=mongo_configuration["host"],
            port=mongo_configuration.get("port", 27017),
            username=os.getenv("MONGO_INITDB_ROOT_USERNAME"),
            password=os.getenv("MONGO_INITDB_ROOT_PASSWORD"),
            authSource=mongo_configuration.get("database", "admin"),
        ) as client:
        db = client[mongo_configuration["db"]]
        mongo_collection = db[mongo_configuration["collection"]]

        if args.topics_history == "DEFAULT":
            result = mongo_collection.find({"default": True}, {"_id": 1})
        elif args.topics_history == "LATEST":
            previous_date = datetime.strptime(args.date, "%Y-%m-%dT%H:%M") + timedelta(days=-1)
            if mongo_collection.count_documents({"dates": previous_date}, limit=1) > 0:
                result = mongo_collection.find({"dates": previous_date}, {"_id": 1})
            else:
                result = mongo_collection.find({"default": True}, {"_id": 1})
        else:
            raise ValueError("Invalid TOPICS_HISTORY_CONFIG. Use 'LATEST' or 'DEFAULT'.")

        topics = [topic["_id"] for topic in result]

    for cluster_id, cluster_content in clusters.items():
        documents = [content["document"] for content in cluster_content]
        ids = [content["id"] for content in cluster_content]
        metadatas = [content["metadatas"] for content in cluster_content]

        if metadatas[0].get("topic"):
            logger.info(f"Cluster {cluster_id} already has a topic assigned: {metadatas[0].get('topic')}. Skipping...")
            label_map[int(cluster_id)] = metadatas[0].get("topic")
            continue

        topic = chain.invoke(
            {
                "documents": ", ".join(documents),
                "initial_topics": ", ".join(topics),
            }
        )
        logger.info(f"Topic updated for cluster {cluster_id}: {topic.content.lower()}")

        if not dry_run:
            chroma_collection.update(ids=ids, metadatas=[{"topic": topic.content.lower()}] * len(ids))
        label_map[int(cluster_id)] = topic.content.lower()

