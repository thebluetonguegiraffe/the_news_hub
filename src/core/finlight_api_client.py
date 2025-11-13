from datetime import datetime
from typing import Dict, List
import requests

from src.core.scrapper import BaseScrapper


class FinlightAPIClient:
    def __init__(self, base_url: str, headers: Dict = None, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)
        self.timeout = timeout

    def get(self, endpoint: str, params: Dict = None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: Dict = None, json: Dict = None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, data=data, json=json, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    @classmethod
    def filter_image_urls(cls, image_urls: List[str], article_url: str) -> List[str]:
        """
        Avoid saving images from the author an scrap image if there are non-author available images.
        """
        non_author_images = [url for url in image_urls if "author" not in url]

        if non_author_images:
            return non_author_images

        scrapper = BaseScrapper()
        image = scrapper.scrape_image_sync(article_url)
        if not image:
            return []
        return [image]

    @classmethod
    def parse(cls, input_data: Dict, creation_date: datetime) -> Dict:
        """
        Parse the article data from Finlight API response to a standardized format.
        """
        valid_image_urls = cls.filter_image_urls(
            image_urls=input_data.get("images", []), article_url=input_data.get("link")
        )
        parsed_document = {
            "publish_date": input_data.get("publishDate"),
            "source": input_data.get("source"),
            "url": input_data.get("link"),
            "title_en": input_data.get("title"),
            "description_en": input_data.get("summary"),
            "image": valid_image_urls,
            "creation_date": creation_date,
        }
        return parsed_document


if __name__ == "__main__":

    client = FinlightAPIClient(
        base_url="https://api.finlight.me/v2/",
        headers={"X-API-KEY": "your_api_key_here"},
    )

    image_urls = [
        "https://static01.nyt.com/images/2021/08/10/business/author-lauren-hirsch/author-lauren-hirsch-thumbLarge-v3.png",  # noqa
        "https://static01.nyt.com/images/2023/11/20/reader-center/author-julie-creswell/author-julie-creswell-thumbLarge.png",  # noqa
    ]
    article_url = "https://www.ara.cat/internacional/proxim-orient/als-israelians-unics-essers-humans-gaza-son-ostatges-soldats_128_5524640.html"  # noqa

    filtered_list = client.filter_image_urls(image_urls, article_url)
    print(filtered_list)
