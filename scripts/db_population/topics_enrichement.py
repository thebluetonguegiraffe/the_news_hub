
import argparse
from datetime import datetime
from dotenv import load_dotenv

from src.topics_enricher import TopicsEnricher


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
    start_date = args.date + ":00.000000Z"

    topics_descriptor = TopicsEnricher()
    topics_descriptor.clusterize_topics(
        date=start_date, dry_run=args.dry_run, overwrite=args.overwrite
    )
    topics_descriptor.populate_topics_database(date="2025-10-17T23:55:00.000Z")
