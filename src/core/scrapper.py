import asyncio
import logging
from abc import ABC
from typing import Dict, List

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

logger = logging.getLogger("scrapper")
logger.setLevel(logging.INFO)


class BaseScrapper(ABC):
    METADATA_KEYS = ["title", "description", "author", "article:modified_time", "og:image"]

    async def __aenter__(self):
        browser_config = BrowserConfig(
            headless=True,  # Recommended setting for server environments
            verbose=False   # <-- This disables the [INIT] logs
        )
        self.run_config = CrawlerRunConfig(
            verbose=False,        # <-- DISABLES [FETCH], [SCRAPE], [COMPLETE] logs
            log_console=False     # Highly recommended to also disable browser console logs
        )
        self.crawler = AsyncWebCrawler(config=browser_config)
        return self

    async def scrape_homepage(self, url: str):
        result = await self.crawler.arun(url=url, config=self.run_config)
        logger.info(f"Scraped Homepage URL: {url}")
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
        topic = tokens[2]
        return topic if topic in self.VALID_TOPICS else None

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.crawler.close()

    async def scrape_article(self, url):
        result = await self.crawler.arun(url=url, config=self.run_config)
        logger.info(f"Scraped article URL: {url}")
        parsed_result = self.parse_article(result)
        return parsed_result

    async def scrape_image(self, url):
        result = await self.crawler.arun(url=url, config=self.run_config)
        return result.metadata.get("og:image")

    def scrape_image_sync(self, url):
        """Synchronous wrapper for scrape_image"""

        async def _scrape():
            async with self:
                return await self.scrape_image(url)

        return asyncio.run(_scrape())

    def parse_article(self, result) -> Dict:
        metadata = result.metadata
        if not metadata:
            logger.info(f"No metadata found for URL: {result.url}")
            return {}

        filtered_metadata = {k: metadata[k] for k in self.METADATA_KEYS if k in metadata}
        filtered_metadata[f"title_{self.LANGUAGE}"] = filtered_metadata.pop("title")
        filtered_metadata[f"description_{self.LANGUAGE}"] = filtered_metadata.pop("description")
        filtered_metadata["topic"] = self._get_topic(url=result.url)
        return filtered_metadata


class AraScrapper(BaseScrapper):
    STOP_WORDS = [
        "usuari", "privacitat", "firmes", "api", "publicitat", "gent", "famosos", "opinio",
        "estils", "criatures", "media", "videojocs", "series", "blogs", "vins", "promocions",
        "suscripcio", "serveis", "especials", "interactius"
    ]
    VALID_TOPICS = ["esports", "economia", "cultura"]
    VALID_URL_MAX_TOKENS = 4
    LANGUAGE = "ca"


class VanguardiaScrapper(BaseScrapper):
    STOP_WORDS = [
        "participacion", "retos", "concursos", "encuesta", "debates", "las-fotos-de-los-lectores",
        "juegos", "sorteos", "calculadoras",
        "magazine", "comer", "recetas", "vivo", "gente", "neo", "pop", "lacontra", "la-contra",
        "series", "cine", "formacion", "vanguardia-dossier", "bolsillo", "natural", "longevity",
        "mkt-roi", "club", "suscriptores", "horario-donde-ver", "en-directo", "vanguardia-eventos",
        "comprar", "suscripciones", "ofertas",
        "ctx", "epm", "brl", "asd", "home-lv", "home-vanguardia"
    ]
    STOP_WORDS = [
        "calculadoras", "videos", "juegos", "comprar", "sorteos", "suscripciones", "ofertas"
    ]
    VALID_URL_MAX_TOKENS = 4
    LANGUAGE = "es"
    VALID_TOPICS = ["deportes", "economia", "cultura"]


class ElPeriodicoScrapper(BaseScrapper):
    STOP_WORDS = [
        "-bc-", "-rm/", "sh-", "dv-", "shopping", "comprar", "ofertas", "sorteos", "mkt-roi",
        "gente", "tele", "gastronomia", "gourmets", "restaurantes", "motor", "sucesos", "videos",
        "vida-y-estilo", "ser-feliz", "que-hacer", "entre-todos", "podcast", "juegos", "series",
        "servicios", "suscripciones", "calculadoras", "club", "horario-donde-ver", "en-directo",
        "tarragona", "cerdanyola", "granollers", "badalona", "hospitalet", "santa-coloma",
        "index.html", "ctx", "epm", "brl", "asd", "home-lv"
    ]
    VALID_URL_MAX_TOKENS = 5
    LANGUAGE = "es"
    VALID_TOPICS = ["deportes", "economía"]


class ElPaisScrapper(BaseScrapper):
    STOP_WORDS = [
        "icon", "smoda", "elviajero", "eps", "ideas", "resultados", "suscripciones",
        "estilo-de-vida", "aniversario", "comunicacion", "carta-del-corresponsal",
        "historias-de-corresponsal", "el-roto", "peridis", "planeta-futuro", "materia-gris",
        "videos", "gastronomia", "ofertas"
    ]
    VALID_URL_MAX_TOKENS = 4
    LANGUAGE = "es"
    VALID_TOPICS = ["deportes", "economía", "cultura", "educación", "tecnologia"]

    @classmethod
    def _is_valid_url(cls, url: str):
        if any(word.lower() in url.lower() for word in cls.STOP_WORDS):
            return False
        path_only = url.split('?')[0].split('#')[0]
        if not path_only.endswith('.html'):
            return False
        tokens = [s for s in url.split("/") if s]
        return len(tokens) > cls.VALID_URL_MAX_TOKENS

    def parse_article(self, result) -> Dict:
        filtered_metadata = super().parse_article(result)
        title = filtered_metadata[f"title_{self.LANGUAGE}"]
        tokens = title.split("|")
        if len(tokens) > 1:
            filtered_metadata[f"title_{self.LANGUAGE}"] = tokens[0].strip()
        return filtered_metadata


SCRAPPER_MAPPER = {
    "diari_ara": ("https://www.ara.cat/", AraScrapper),
    "la_vanguardia": ("https://www.lavanguardia.com/", VanguardiaScrapper),
    "el_pais": ("https://elpais.com/", ElPaisScrapper),
    "el_periodico": ("https://www.elperiodico.com/es/", ElPeriodicoScrapper),
}
