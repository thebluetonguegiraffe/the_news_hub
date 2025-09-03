


import logging
from typing import List, Optional, Tuple

from src.news_scrapper import NewsScrapper

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def filter_image_url_list(image_urls: List[str], url: str) -> Tuple[List[str], Optional[str]]:
    scrapper = NewsScrapper()
    filtered_list = [url for url in image_urls if "author" not in url]
    
    if filtered_list:
        return filtered_list, None
    
    logger.info("Scrapping image...")
    image = scrapper.extract_image(url)
    return filtered_list, image


if __name__ == "__main__":
    image_urls =   [
        "https://static01.nyt.com/images/2021/08/10/business/author-lauren-hirsch/author-lauren-hirsch-thumbLarge-v3.png",
        "https://static01.nyt.com/images/2023/11/20/reader-center/author-julie-creswell/author-julie-creswell-thumbLarge.png"
    ]
    url = 'https://www.nytimes.com/2025/09/02/business/kraft-heinz-break-up.html'

    filtered_list, extra_images = filter_image_url_list([], url)