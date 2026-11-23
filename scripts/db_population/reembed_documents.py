"""
Re-embed the documents that were indexed in the wrong language.

A document's embedded text is its English title and excerpt. While the
translation endpoint was refusing this server, the English fields held the
publisher's original Catalan or Spanish instead, so the vectors were built from
one language while the category prototypes are written in another, and both the
category assignment and the story clustering ran across that gap.

The translations are fixed in the metadata now, but the stored text and its
vector are not: this rewrites both for every document whose embedded text no
longer matches its English fields. Run it before re-running the enrichment, so
the categories and trends are computed from the corrected vectors.

    python scripts/db_population/reembed_documents.py --days 7 --dry-run
    python scripts/db_population/reembed_documents.py --days 7
"""

import argparse
import logging

from dotenv import load_dotenv

from config import chroma_configuration
from src.core.chroma_database import ChromaDatabase, CustomEmbedder
from src.utils.rate_limit import call_with_retry
from scripts.db_population.backfill_topics import recent_buckets


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("reembed_documents")
logger.setLevel(logging.INFO)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

PAGE_SIZE = 300
# The embedding endpoint takes a list per call; keep the batch modest so one
# failure costs little and the payload stays well inside the request limit.
EMBED_BATCH = 32


def expected_text(metadata: dict) -> str:
    """The text a document should be embedded from: English title and excerpt."""
    title = (metadata.get("title") or "").strip()
    excerpt = (metadata.get("excerpt") or "").strip()
    if not title:
        return ""
    return f"{title}. {excerpt}" if excerpt else title


def fetch_bucket(collection, date: str) -> list:
    """Every document in a bucket with its stored text, paged around the cap."""
    records = []
    offset = 0
    while True:
        batch = collection.get(
            where={"ingestion_date": date},
            include=["metadatas", "documents"],
            limit=PAGE_SIZE,
            offset=offset,
        )
        ids = batch.get("ids") or []
        if not ids:
            break
        records.extend(zip(ids, batch["documents"], batch["metadatas"]))
        if len(ids) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return records


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=7, help="How many days back to scan.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Report what would change without writing to the database.",
    )
    args = parser.parse_args()

    chroma_db = ChromaDatabase(collection_name=chroma_configuration["collection_name"])
    collection = chroma_db.collection
    embedder = CustomEmbedder()
    buckets = recent_buckets(args.days)
    logger.info(f"scanning {len(buckets)} buckets over the last {args.days} days")

    grand_stale = grand_written = 0
    for bucket in buckets:
        records = fetch_bucket(collection, bucket)
        if not records:
            logger.info(f"{bucket}: no documents")
            continue

        stale = []
        for doc_id, stored, metadata in records:
            wanted = expected_text(metadata)
            if not wanted:
                continue
            if (stored or "").strip() != wanted:
                stale.append((doc_id, wanted))

        if not stale:
            logger.info(f"{bucket}: {len(records)} documents, all up to date")
            continue

        grand_stale += len(stale)
        logger.info(f"{bucket}: {len(stale)}/{len(records)} documents to re-embed")
        if args.dry_run:
            continue

        ids = [doc_id for doc_id, _ in stale]
        texts = [text for _, text in stale]
        vectors = []
        for start in range(0, len(texts), EMBED_BATCH):
            chunk = texts[start:start + EMBED_BATCH]
            vectors.extend(
                call_with_retry(
                    lambda chunk=chunk: embedder(chunk), description="document embeddings"
                )
            )

        if len(vectors) != len(texts):
            logger.error(
                f"{bucket}: got {len(vectors)} vectors for {len(texts)} texts; skipping"
            )
            continue

        # Text and vector are written together: leaving one behind would make
        # the stored document disagree with what is actually indexed.
        for start in range(0, len(ids), PAGE_SIZE):
            collection.update(
                ids=ids[start:start + PAGE_SIZE],
                documents=texts[start:start + PAGE_SIZE],
                embeddings=vectors[start:start + PAGE_SIZE],
            )
        grand_written += len(ids)
        logger.info(f"{bucket}: re-embedded {len(ids)} documents")

    verb = "would be" if args.dry_run else "were"
    logger.info(f"done: {grand_stale} documents {verb} re-embedded, {grand_written} written")


if __name__ == "__main__":
    main()
