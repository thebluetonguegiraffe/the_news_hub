


import argparse
import logging
from pathlib import Path

from src.config import db_configuration, sql_db_configuration
from src.llm_resources import LLMResources
from src.sql_client import TopicsDBClient
from src.vectorized_database import VectorizedDatabase
from templates.news_templates import topic_description_template
from scripts.constants import TOPICS

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

    metadatas = collection.get(include=["metadatas"])['metadatas']
    topics = set([metadata["topic"] for metadata in metadatas])

    if not dry_run:

        db_path = sql_db_configuration["db_path"]
        sql_client = TopicsDBClient(
            db_path=f"{project_root}/db/{db_path}"
        )
        
        llm_description = LLMResources.create_llm()
        description_prompt = LLMResources.create_prompt_template(topic_description_template)
        description_chain = description_prompt | llm_description
        
        for topic in topics:
            logger.info(f'Retrieving description for: {topic}')
            description = TOPICS.get(topic, None)
            if not description:
                logger.info(f'Generating description for: {topic}')
                description = description_chain.invoke(
                    {
                        "topic": topic,
                    }
                ).content

            sql_client.upsert_topic(topic, description, "2025-07-31T19:32:05.000Z")
        
