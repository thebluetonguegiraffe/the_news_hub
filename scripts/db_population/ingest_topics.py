import argparse
from collections import Counter
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from pymongo import MongoClient

from config import db_configuration, project_root, mongo_configuration, chat_configuration

from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate

from src.vectorized_database import VectorizedDatabase

from templates.news_templates import topic_description_template

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


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
        "-d",
        "--date",
        required=True,
        help="Date for the news articles in format YYYY-MM-DDTHH:MM",
    )
    args = parser.parse_args()
    dry_run = args.dry_run

    db_path = db_configuration["db_path"]
    collection_name = db_configuration["collection_name"]

    logger.info("Initializing vectorized database")
    chroma = VectorizedDatabase(
        persist_directory=f"{project_root}/db/{db_path}",
        collection_name=collection_name,
    )

    chroma_collection = chroma.get_collection()

    start_date = args.date + ":00.000000Z"
    metadatas = chroma_collection.get(
        where={"date": start_date}, include=["metadatas"]
        )["metadatas"]

    topics = [doc.get('topic', "Others").lower() for doc in metadatas]
    topic_counts = dict(Counter(topics))

    if not topics:
        raise ValueError(f"No topics found for date {args.date}.")

    logger.info(f"{len(topics)} topics retrieved for day {start_date}")

    start_date = datetime.strptime(args.date, "%Y-%m-%dT%H:%M")

    if not dry_run:
        with MongoClient(
                mongo_configuration["host"],
                port=mongo_configuration.get("port", 27017),
                username=os.getenv("MONGO_INITDB_ROOT_USERNAME"),
                password=os.getenv("MONGO_INITDB_ROOT_PASSWORD"),
                authSource=mongo_configuration.get("database", "admin"),
            ) as client:
            db = client[mongo_configuration["db"]]
            mongo_collection = db[mongo_configuration["collection"]]

            llm_description = init_chat_model(
                model=chat_configuration["model"],
                model_provider="openai",
                api_key=os.environ["GITHUB_TOKEN"],
                base_url="https://models.github.ai/inference"
            )
            description_prompt = ChatPromptTemplate.from_messages([("human", topic_description_template)])
            
            description_chain = description_prompt | llm_description

            for topic, n in topic_counts.items():
                results = mongo_collection.find_one(filter={"_id": topic})
                if not results:
                    logger.info(f"Generating description for: {topic}")
                    description = description_chain.invoke(
                        {
                            "topic": topic,
                        }
                    ).content

                    mongo_collection.insert_one(
                        {
                            "_id": topic,
                            "description": description,
                            "topics_per_day": {'date': start_date, "docs_number": n},
                        }
                    )
                else:
                    logger.info(f"Description found for: {topic}")
                    mongo_collection.update_one(
                        filter={"_id": topic},
                        update={"$addToSet": {"topics_per_day": {'date': start_date, "docs_number": n},}},
                        upsert=True,
                    )
