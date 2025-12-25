import argparse
import json
import logging

from dotenv import load_dotenv

from config import chroma_configuration
from src.core.chroma_database import ChromaDatabase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("update_fields_script")
logger.setLevel(logging.INFO)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


def parse_filter(value: str) -> dict:
    """Parses --filter argument into a dict."""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        if "," in value:
            items = value.split(",")
            conditions = []
            for item in items:
                if ":" in item:
                    key, val = item.split(":", 1)
                    conditions.append({key.strip(): val.strip()})
                else:
                    raise argparse.ArgumentTypeError(
                        f"Invalid filter format: {item}. Expected key:value."
                    )

            if len(conditions) > 1:
                chroma_filter = {"$and": conditions}
            else:
                chroma_filter = conditions[0]

            return chroma_filter


if __name__ == "__main__":

    load_dotenv()
    parser = argparse.ArgumentParser(description="Run script tp modify ChromaDB fields")
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
        "--limit",
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

    chroma_db = ChromaDatabase(collection_name=chroma_configuration["collection_name"])

    docs = chroma_db.search_with_filter(
        include=["metadatas"], chroma_filter=filter_dict, limit=args.limit if args.limit else None
    )

    n_docs = len(docs["metadatas"])

    for i, metadata in enumerate(docs["metadatas"]):
        old_field_value = metadata[args.field]
        # modify runnable(field to get data) if necessary
        result = runnable(metadata) if runnable else args.value
        docs["metadatas"][i][field] = result
        logger.info(f"Updated {field} from {old_field_value} to {result}")

    if not args.dry_run:
        chroma_db.update_documents(docs)
        logger.info(f"{n_docs} updated in Chroma DB.")
