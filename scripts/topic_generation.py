

import json

from collections import defaultdict
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from src.llm_resources import LLMResources
from src.config import db_configuration, sql_db_configuration
from src.sql_client import TopicsDBClient
from src.vectorized_database import VectorizedDatabase

from templates.news_templates import topic_generation_template
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate topics for clustered news articles.")
    parser.add_argument("--dry_run", action="store_true", help="Run the script without updating the database.", default=True)
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

    n_components = 90
    pca = PCA(n_components=n_components)
    embeddings_reduced = pca.fit_transform(embeddings)

    n_clusters = 15
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings_reduced)

    clusters = defaultdict(list)
    for doc, _id, label in zip(documents, ids, labels):
        clusters[label].append({"document": doc, "id": _id})


    prompt = LLMResources.create_prompt_template(topic_generation_template)
    llm = LLMResources.create_llm()

    chain = prompt | llm

    label_map =  {}
    for cluster_id, cluster_content in clusters.items():
        documents = [content["document"] for content in cluster_content]
        ids = [content["id"] for content in cluster_content]

        topic = chain.invoke(
            {
                "documents": ", ".join(documents),
            }
        )

        if not dry_run:
            collection.update(
                ids=ids,
                metadatas=[{"topic": topic.content}] * len(ids)
            )

        label_map[int(cluster_id)] = topic.content

    clusters_named = {
        label_map[cluster_id]: docs
        for cluster_id, docs in clusters.items()
    }

    db_path = sql_db_configuration["db_path"]
    sql_client = TopicsDBClient(
        db_path=f"{project_root}/db/{db_path}"
    )

    for topic in clusters_named.keys():
        sql_client.upsert_topic(topic, date)
        

