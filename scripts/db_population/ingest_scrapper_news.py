import asyncio

from src.ingestors.scrapper_ingestor import ScrapperIngestor
from src.core.scrapper import SCRAPPER_MAPPER


if __name__ == "__main__":
    for source in SCRAPPER_MAPPER.keys():
        asyncio.run(ScrapperIngestor(source).run())
