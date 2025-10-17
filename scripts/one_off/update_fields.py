import argparse
import json
import logging

from dotenv import load_dotenv

from config import db_configuration, project_root
from src.vectorized_database import VectorizedDatabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_filter(value: str) -> dict:
    """Parses --filter argument into a dict."""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        if ":" in value:
            key, val = value.split(":", 1)
            return {key.strip(): val.strip()}
        raise argparse.ArgumentTypeError(
            f"Invalid filter format: {value}. Expected JSON or key:value."
        )


if __name__ == "__main__":

    load_dotenv()
    parser = argparse.ArgumentParser(description="Ask a question to the news recommender system.")
    parser.add_argument(
        "--field",
        required=True,
    )
    parser.add_argument(
        "--new-field",
    )
    parser.add_argument(
        "--runnable",
        required=False,
    )

    parser.add_argument(
        "--value",
        required=False,
    )
    parser.add_argument(
        "--filter",
        required=False,
        type=parse_filter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the script without updating the database.",
        default=False,
    )

    args = parser.parse_args()
    filter_dict = args.filter if args.filter else {}
    runnable = eval(args.runnable) if args.runnable else None
    field = args.new_field or args.field

    db_path = db_configuration["db_path"]
    collection_name = db_configuration["collection_name"]

    logger.info("Initializing vectorized database")
    db_client = VectorizedDatabase(
        persist_directory=f"{project_root}/db/{db_path}", collection_name=collection_name
    )

    collection = db_client.get_collection()
    docs = collection.get(
        include=["metadatas"],
        where=filter_dict,
        # limit=1
    )

    n_docs = len(docs["metadatas"])

    for i, metadata in enumerate(docs["metadatas"]):
        field_to_modify = metadata[args.field]
        result = runnable(field_to_modify) if runnable else args.value
        docs["metadatas"][i][field] = result
        logger.info(f"Updated {field} from {field_to_modify} to {result}")

    if not args.dry_run:
        collection.update(
            ids=docs["ids"],
            metadatas=docs["metadatas"],
        )
        logger.info(f"{n_docs} updated in Chroma DB.")
