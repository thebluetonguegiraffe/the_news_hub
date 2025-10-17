import asyncio

from ingestors.scrapper_ingestor import ScrapperIngestor
from src.scrapper import SCRAPPER_MAPPER


if __name__ == "__main__":
    for source in SCRAPPER_MAPPER.keys():
        asyncio.run(ScrapperIngestor(source).run())
