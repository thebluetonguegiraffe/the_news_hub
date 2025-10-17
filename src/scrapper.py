import asyncio
from typing import Dict, List
from crawl4ai import AsyncWebCrawler

from abc import ABC


class BaseScrapper(ABC):
    METADATA_KEYS = ["title", "description", "author", "article:modified_time", "og:image"]

    async def __aenter__(self):
        self.crawler = AsyncWebCrawler()
        return self

    async def scrape_homepage(self, url: str):
        result = await self.crawler.arun(url=url)
        parsed_result = self.parse_homepage(result)
        return parsed_result

    def parse_homepage(self, result) -> List:
        homepage_articles = result.links["internal"]
        valid_articles = [
            article["href"] for article in homepage_articles if self._is_valid_url(article["href"])
        ]
        return valid_articles

    @classmethod
    def _is_valid_url(cls, url: str):
        """
        Determine if homepage URL is valid based on stop words and token count
        """
        if any(word in url for word in cls.STOP_WORDS):
            return False
        tokens = [s for s in url.split("/") if s]
        return len(tokens) > cls.VALID_URL_MAX_TOKENS

    def _get_topic(self, url: str):
        tokens = [s for s in url.split("/") if s]
        return tokens[2]

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.crawler.close()

    async def scrape_article(self, url):
        result = await self.crawler.arun(url=url)
        parsed_result = self.parse_article(result)
        return parsed_result

    async def scrape_image(self, url):
        result = await self.crawler.arun(url=url)
        return result.metadata.get("og:image")

    def scrape_image_sync(self, url):
        """Synchronous wrapper for scrape_image"""

        async def _scrape():
            async with self:
                return await self.scrape_image(url)

        return asyncio.run(_scrape())

    def parse_article(self, result) -> Dict:
        metadata = result.metadata
        filtered_metadata = {k: metadata[k] for k in self.METADATA_KEYS if k in metadata}
        filtered_metadata[f"title_{self.LANGUAGE}"] = filtered_metadata.pop("title")
        filtered_metadata[f"description_{self.LANGUAGE}"] = filtered_metadata.pop("description")
        filtered_metadata["topic"] = self._get_topic(url=result.url)
        return filtered_metadata


class AraScrapper(BaseScrapper):
    STOP_WORDS = ["usuari", "privacitat", "firmes", "api", "publicitat"]
    VALID_URL_MAX_TOKENS = 4
    LANGUAGE = "ca"


class VanguardiaScrapper(BaseScrapper):
    STOP_WORDS = ["calculadoras", "videos", "juegos", "comprar", "sorteos"]
    VALID_URL_MAX_TOKENS = 4
    LANGUAGE = "ca"


SCRAPPER_MAPPER = {
    "diari_ara": ("https://www.ara.cat/", AraScrapper),
    "la_vanguardia": ("https://www.lavanguardia.com/", VanguardiaScrapper),
}
