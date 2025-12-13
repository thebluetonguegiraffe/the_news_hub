import argparse
from datetime import datetime
import logging
from dotenv import load_dotenv

from src.ingestors.api_ingestor import APIIngestor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("api_ingestor_script")
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

    parser = argparse.ArgumentParser(description="API news ingestion script")
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

    args = parser.parse_args()

API_SOURCES = [
    "www.washingtonpost.com",
    "www.theguardian.com",
    "www.bbc.com",
    "www.nytimes.com",
]

if __name__ == "__main__":
    for source in API_SOURCES:
        logger.info(f"Processing source: {source}")
        try:
            APIIngestor(source=source, date=args.date, dry_run=args.dry_run).run()
        except Exception as e:
            logger.error(f"Error processing source {source}: {e}")
            continue
