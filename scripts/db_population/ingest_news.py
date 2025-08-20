import argparse
from datetime import timedelta, datetime
import logging
import os

from dotenv import load_dotenv
import requests

from src.finlight_api_client import FinlightAPIClient
from src.vectorized_database import VectorizedDatabase
from config import news_api_configuration, db_configuration, project_root

PAGE_SIZE = 100

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    load_dotenv()

    parser = argparse.ArgumentParser(description="Ask a question to the news recommender system.")
    parser.add_argument(
        "-s",
        "--source",
        required=True,
        nargs="+",
        help="Source(s) of the news articles (e.g., 'www.bbc.com', 'www.cnn.com').",
    )
    parser.add_argument(
        "-d", "--date", required=True, help="Date for the news articles in format YYYY-MM-DDTHH:MM"
    )

    args = parser.parse_args()

    db_path = db_configuration["db_path"]
    collection_name = db_configuration["collection_name"]

    logger.info("Initializing FinlightAPIClient")

    # initialize script clients
    news_api_client = FinlightAPIClient(
        base_url=news_api_configuration["url"],
        headers={"X-API-KEY": os.getenv("FINLIGHT_API_TOKEN")},
    )

    logger.info("Initializing vectorized database")
    db_client = VectorizedDatabase(
        persist_directory=f"{project_root}/db/{db_path}", collection_name=collection_name
    )

    # Query news API
    start_date = datetime.strptime(args.date, "%Y-%m-%dT%H:%M")
    end_date = start_date + timedelta(days=1)
    try:
        response = news_api_client.post(
            endpoint=news_api_configuration["endpoint"],
            json={
                "sources": args.source,
                "from": start_date.strftime("%Y-%m-%dT%H:%M"),
                "to": end_date.strftime("%Y-%m-%dT%H:%M"),
                "pageSize": PAGE_SIZE,
            },
        )

        articles = response.get("articles", [])
        if not articles:
            raise ValueError(f"No articles found for source {args.source} on {args.date}.")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"HTTP error occurred: {e}")

    unique_articles = {}
    for article in articles:
        title = article.get("title")
        if title and title not in unique_articles:
            unique_articles[title] = article

    documents, ids, metadatas = map(
        list,
        zip(
            *(
                news_api_client.parse_finlight_article(article, start_date)
                for article in list(unique_articles.values())
            )
        ),
    )

    # add documents to the vectorized database
    collection = db_client.get_collection()
    logger.info(f"Adding {len(documents)} documents to the collection: {collection.name}")
    collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas,
    )

    logger.info("Documents added successfully.")
