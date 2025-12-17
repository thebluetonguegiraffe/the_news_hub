
import argparse
from datetime import datetime
import logging
from dotenv import load_dotenv

from src.core.topics_enricher import TopicsEnricher


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("topics_enricher_script")
logger.setLevel(logging.INFO)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


def valid_date(date_str: str) -> datetime:
    """Validate and parse date in format YYYY-MM-DDTHH:MM."""
    try:
        return date_str
    except ValueError:
        msg = f"Invalid date format: '{date_str}'. Expected format: YYYY-MM-DDTHH:MM"
        raise argparse.ArgumentTypeError(msg)


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Generate topics for clustered news articles.")
    parser.add_argument(
        "-d",
        "--date",
        required=True,
        type=valid_date,
        help="Date for the news articles in format YYYY-MM-DDTHH:MM",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the script without updating the database.",
        default=False,
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Run compute topics for all day documents.",
        default=False,
    )

    args = parser.parse_args()
    start_date = args.date + ":00.000Z"

    topics_descriptor = TopicsEnricher()
    topics_descriptor.clusterize_topics(
        date=start_date, dry_run=args.dry_run, overwrite=args.overwrite
    )
    topics_descriptor.populate_topics_database(date=start_date, dry_run=args.dry_run)
