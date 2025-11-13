import argparse
from datetime import datetime
import logging
from dotenv import load_dotenv

from src.ingestors.api_ingestor import APIIngestor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


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
        APIIngestor(source=source, date=args.date).run()
