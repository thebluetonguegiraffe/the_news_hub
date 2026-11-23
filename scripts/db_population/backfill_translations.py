"""
Fill in the translations the blocked endpoint never delivered.

Every document ingested while translate.google.com/m was answering this server
with an abuse redirect kept the original headline in all three language fields,
so the API served Catalan to Spanish readers and Spanish to English ones. The
translator now talks to the JSON endpoint instead, but that only fixes new
ingestions: this walks the recent buckets and translates what is already there.

A field counts as untranslated when it is empty or still identical to the text
in the document's own language.

    python scripts/db_population/backfill_translations.py --days 7 --dry-run
    python scripts/db_population/backfill_translations.py --days 7
"""

import argparse
from collections import defaultdict
import logging

from dotenv import load_dotenv

from config import chroma_configuration, mongo_configuration
from src.core.chroma_database import ChromaDatabase
from src.core.mongo_client import CustomMongoClient
from src.core.translator import GoogleTranslator
from src.taxonomy import CATEGORY_LABELS, CATEGORY_NAMES, UNCLASSIFIED_CATEGORY
from scripts.db_population.backfill_topics import recent_buckets


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("backfill_translations")
logger.setLevel(logging.INFO)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

PAGE_SIZE = 300
LANGUAGES = ("en", "es", "ca")
FIELDS = ("title", "excerpt")

# Which language each publisher writes in. The scrapers know this at ingestion
# time through their LANGUAGE attribute, but the stored document only carries
# the source, so the mapping has to be repeated here.
SOURCE_LANGUAGES = {
    "https://www.ara.cat/": "ca",
    "https://www.lavanguardia.com/": "es",
    "https://elpais.com/": "es",
    "https://www.elperiodico.com/es/": "es",
    "www.theguardian.com": "en",
    "www.bbc.com": "en",
}


def field_key(field: str, language: str) -> str:
    """Metadata key for a field in a language; English carries no suffix."""
    return field if language == "en" else f"{field}_{language}"


def fetch_bucket(collection, date: str) -> list:
    """Every document in a bucket, paged around the per-request row cap."""
    records = []
    offset = 0
    while True:
        batch = collection.get(
            where={"ingestion_date": date},
            include=["metadatas"],
            limit=PAGE_SIZE,
            offset=offset,
        )
        ids = batch.get("ids") or []
        if not ids:
            break
        records.extend(zip(ids, batch["metadatas"]))
        if len(ids) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return records


def collect_work(records: list) -> tuple:
    """
    Group everything that needs translating by language pair and field.

    One batch per (source language, target language, field) keeps the number of
    requests down: a bucket of 300 articles costs a handful of requests rather
    than hundreds.
    """
    work = defaultdict(list)
    unknown_sources = set()
    for doc_id, md in records:
        source_language = SOURCE_LANGUAGES.get(md.get("source"))
        if not source_language:
            unknown_sources.add(md.get("source"))
            continue
        for field in FIELDS:
            original = (md.get(field_key(field, source_language)) or "").strip()
            if not original:
                continue
            for language in LANGUAGES:
                if language == source_language:
                    continue
                current = (md.get(field_key(field, language)) or "").strip()
                if current and current != original:
                    continue  # already translated
                work[(source_language, language, field)].append((doc_id, original))
    return work, unknown_sources


def backfill_categories(dry_run: bool) -> None:
    """
    Re-translate the canonical category labels and descriptions.

    The enricher writes these with $setOnInsert, so the categories first stored
    while the endpoint was refusing us kept the English name as their Catalan
    and Spanish label and would never be corrected by a later run. This sets
    them unconditionally, which is safe because the labels come from the
    taxonomy and the English description is the source of truth.
    """
    wanted = sorted(list(CATEGORY_LABELS) + [UNCLASSIFIED_CATEGORY])
    translator = GoogleTranslator(source_lang="en")

    with CustomMongoClient() as client:
        collection = client[mongo_configuration["db"]][mongo_configuration["collection"]]
        stored = list(collection.find({"_id": {"$in": wanted}}))

        pending = []
        for document in stored:
            label = document["_id"]
            description = document.get("description") or ""
            names = CATEGORY_NAMES.get(label, {})
            needs_label = any(
                document.get(f"topic_{language}") != names.get(language)
                for language in ("ca", "es")
            )
            needs_description = bool(description) and any(
                not document.get(f"description_{language}")
                or document.get(f"description_{language}") == description
                for language in ("ca", "es")
            )
            if needs_label or needs_description:
                pending.append((label, description))

        if not pending:
            logger.info("categories: nothing to translate")
            return

        logger.info(f"categories: {len(pending)} to translate")
        if dry_run:
            logger.info(f"categories: would translate {[label for label, _ in pending]}")
            return

        descriptions = [description for _, description in pending]
        translations = {}
        for language in ("ca", "es"):
            # Only the descriptions are translated: they are full sentences,
            # which is what the endpoint is good at.
            translations["description", language] = translator.translate_batch(
                descriptions, target_lang=language
            )

        written = 0
        for index, (label, description) in enumerate(pending):
            update = {}
            names = CATEGORY_NAMES.get(label, {})
            for language in ("ca", "es"):
                if names.get(language):
                    update[f"topic_{language}"] = names[language]
                translated_description = translations["description", language][index]
                if translated_description:
                    update[f"description_{language}"] = translated_description
            if not update:
                continue
            collection.update_one({"_id": label}, {"$set": update})
            written += 1
            logger.info(
                f"   {label}: ca={update.get('topic_ca')!r} es={update.get('topic_es')!r}"
            )
        logger.info(f"categories: {written} updated")
    translator.log_stats()


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=7, help="How many days back to scan.")
    parser.add_argument(
        "--scope",
        choices=("all", "documents", "categories"),
        default="all",
        help="Translate the articles, the category labels, or both.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Report what would change without writing to the database.",
    )
    args = parser.parse_args()

    if args.scope in ("all", "categories"):
        backfill_categories(dry_run=args.dry_run)
    if args.scope == "categories":
        return

    chroma_db = ChromaDatabase(collection_name=chroma_configuration["collection_name"])
    collection = chroma_db.collection
    buckets = recent_buckets(args.days)
    logger.info(f"scanning {len(buckets)} buckets over the last {args.days} days")

    grand_total = grand_written = 0
    for bucket in buckets:
        records = fetch_bucket(collection, bucket)
        if not records:
            logger.info(f"{bucket}: no documents")
            continue

        work, unknown_sources = collect_work(records)
        pending = sum(len(items) for items in work.values())
        if unknown_sources:
            logger.warning(f"{bucket}: unknown source language for {unknown_sources}")
        if not pending:
            logger.info(f"{bucket}: {len(records)} documents, nothing to translate")
            continue

        grand_total += pending
        logger.info(
            f"{bucket}: {len(records)} documents, {pending} fields to translate "
            f"in {len(work)} batches"
        )
        if args.dry_run:
            continue

        # Collect every change for the bucket first, then write once per
        # document: the metadata update merges keys, but one call per field
        # would multiply the requests for no gain.
        updates = defaultdict(dict)
        for (source_language, language, field), items in sorted(work.items()):
            translator = GoogleTranslator(source_lang=source_language)
            originals = [text for _, text in items]
            translations = translator.translate_batch(originals, target_lang=language)
            done = 0
            for (doc_id, _), translated in zip(items, translations):
                if not translated:
                    continue
                updates[doc_id][field_key(field, language)] = translated
                done += 1
            logger.info(
                f"   {field} {source_language}->{language}: "
                f"{done}/{len(items)} translated"
            )

        if not updates:
            logger.warning(f"{bucket}: nothing came back translated")
            continue

        doc_ids = list(updates)
        for start in range(0, len(doc_ids), PAGE_SIZE):
            page = doc_ids[start:start + PAGE_SIZE]
            collection.update(ids=page, metadatas=[updates[i] for i in page])
        grand_written += sum(len(fields) for fields in updates.values())
        logger.info(f"{bucket}: wrote {len(updates)} documents")

    verb = "would be" if args.dry_run else "were"
    logger.info(
        f"done: {grand_total} fields {verb} translated, {grand_written} written"
    )


if __name__ == "__main__":
    main()
