"""
Catch up on documents that were left without a category.

The scrapers can take many hours to finish a bucket, so documents often land
after the enrichment run for that bucket has already passed. This walks the
recent ingestion buckets and enriches whatever is still unlabelled, which also
serves as the backfill for the gap the earlier rate-limit failures left behind.

    python scripts/db_population/backfill_topics.py --days 7 --dry-run
    python scripts/db_population/backfill_topics.py --days 7
"""

import argparse
from datetime import datetime, timedelta, timezone
import logging

from dotenv import load_dotenv

from src.core.topics_enricher import TopicsEnricher


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("backfill_topics")
logger.setLevel(logging.INFO)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# The ingestion DAGs stamp every document with one of these two daily buckets.
BUCKET_TIMES = ("11:55", "23:55")


def recent_buckets(days: int) -> list:
    """Every ingestion bucket within the last `days`, oldest first."""
    now = datetime.now(timezone.utc)
    buckets = []
    for offset in range(days, -1, -1):
        day = (now - timedelta(days=offset)).strftime("%Y-%m-%d")
        for bucket_time in BUCKET_TIMES:
            stamp = f"{day}T{bucket_time}:00.000Z"
            if datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%S.000Z").replace(
                tzinfo=timezone.utc
            ) <= now:
                buckets.append(stamp)
    return buckets


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=7, help="How many days back to scan.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Report what would change without writing to the databases.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Re-label every document in range, not only the unlabelled ones.",
    )
    args = parser.parse_args()

    enricher = TopicsEnricher()
    buckets = recent_buckets(args.days)
    logger.info(f"scanning {len(buckets)} buckets over the last {args.days} days")

    total_pending = 0
    for bucket in buckets:
        pending = enricher.fetch_documents(
            date=bucket, overwrite=args.overwrite, include=["metadatas"]
        )
        count = len(pending["ids"])
        if not count:
            logger.info(f"{bucket}: nothing pending")
            continue

        total_pending += count
        if args.dry_run:
            logger.info(f"{bucket}: {count} documents would be enriched")
            continue

        logger.info(f"{bucket}: enriching {count} documents")
        enricher.clusterize_topics(date=bucket, dry_run=False, overwrite=args.overwrite)
        enricher.populate_topics_database(date=bucket, dry_run=False)

    verb = "would be" if args.dry_run else "were"
    logger.info(f"done: {total_pending} documents {verb} enriched across {len(buckets)} buckets")
    enricher.translator.log_stats()


if __name__ == "__main__":
    main()
