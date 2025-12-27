import argparse
import logging
from flask.cli import load_dotenv
from src.core.mongo_client import CustomMongoClient
from config import mongo_configuration
from src.core.translator import GoogleTranslator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("topics_translation")
logger.setLevel(logging.INFO)


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(description="API news ingestion script")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the script without updating the database.",
        default=False,
    )

    args = parser.parse_args()

    translator = GoogleTranslator(source_lang="en")

    with CustomMongoClient() as client:
        db = client[mongo_configuration["db"]]
        collection = db[mongo_configuration["collection"]]
        documents = collection.find()

        for doc in documents:
            topic = doc.get("_id", "")
            description = doc.get("description", "")

            topic_ca = translator.translate(topic, target_lang="ca")
            description_ca = translator.translate(description, target_lang="ca")

            topic_es = translator.translate(topic, target_lang="es")
            description_es = translator.translate(description, target_lang="es")

            if not args.dry_run:
                collection.update_one(
                    {"_id": doc["_id"]},
                    {
                        "$set": {
                            "topic_ca": topic_ca,
                            "topic_es": topic_es,
                            "description_ca": description_ca,
                            "description_es": description_es,
                        }
                    },
                )

            logger.info(f"Updated: {doc['_id']}")
