import argparse
import asyncio
import logging

from dotenv import load_dotenv

from src.ingestors.scrapper_ingestor import ScrapperIngestor
from src.core.scrapper import SCRAPPER_MAPPER

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("scrapper_ingestor_script")
logger.setLevel(logging.INFO)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


if __name__ == "__main__":

    load_dotenv()

    parser = argparse.ArgumentParser(description="Scrapper news ingestion script")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the script without updating the database.",
        default=False,
    )

    args = parser.parse_args()
    for source in SCRAPPER_MAPPER.keys():
        asyncio.run(ScrapperIngestor(source=source, dry_run=args.dry_run).run())
