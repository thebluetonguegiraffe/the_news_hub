

from collections import defaultdict
import logging
from typing import Dict, List, Union

from dotenv import load_dotenv

from src.utils.image_filter import filter_image_url_list
from src.vectorized_database import VectorizedDatabase
from config import db_configuration, project_root

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_chroma_results(
    chroma_results: Dict,
    reverse: bool = True
) -> Union[List[Dict], Dict] :
    articles = []
    enriched_metadata = {}
    
    pairs = list(zip(chroma_results['metadatas'], chroma_results['ids']))
    if reverse:
        pairs = list(reversed(pairs)) 
    
    for i, (metadata, chroma_id) in enumerate(pairs):
        article = defaultdict(dict)
        url = metadata.get("url")
        filtered_images, extra_image = filter_image_url_list(
            image_urls=metadata.get("image", "").split(' '), 
            url = url
        )
        if extra_image:
            metadata['image'] = metadata['image'] + f" {extra_image}"
            enriched_metadata[chroma_id] = metadata

        article["id"] = i
        article["chroma_id"] = chroma_id
        article["date"] = metadata.get("publish_date")
        article["topic"] = metadata.get("topic")
        article["source"] = metadata.get("source")
        article["url"] = url
        article["image"] = filtered_images
        article["excerpt"] = metadata.get("excerpt")
        article["title"] = metadata.get("title")
        articles.append(article)
    
    return articles, enriched_metadata

def parse_dict_results(
    results: List,
) -> Union[List[Dict], Dict] :
    articles = []
    enriched_metadata = {}
        
    for i, item in enumerate(results):
        article = defaultdict(dict)
        url = item.get("url")
        filtered_images, _ = filter_image_url_list(
            image_urls=item.get("image", "").split(' '), 
            url = url
        )

        article["id"] = i
        article["chroma_id"] = item.get('chroma_id')
        article["date"] = item.get("publish_date")
        article["topic"] = item.get("topic")
        article["source"] = item.get("source")
        article["url"] = url
        article["image"] = filtered_images
        article["excerpt"] = item.get("excerpt", "")
        article["title"] = item.get("title", "")
        articles.append(article)
    
    # no enriched images are returned as they are few samples and managing is effordless
    return articles


if __name__== "__main__":

    load_dotenv()
    
    chroma_db_path = f"{project_root}/db/{db_configuration['db_path']}"
    chroma_client = VectorizedDatabase(
    persist_directory=chroma_db_path,
    collection_name=db_configuration["collection_name"]
    )

    collection = chroma_client.get_collection()
    results = collection.get(
        where={"date": "2025-09-01T23:55:00.000000Z"},
        # limit=6,
        include=["metadatas"]
    )
    articles, enriched_metadata = parse_chroma_results(results)
    if enriched_metadata:
        collection.update(
            ids=list(enriched_metadata.keys()),                 
            metadatas=list(enriched_metadata.values()),     
        )
        logger.info(f"{len(enriched_metadata)} updated in Chroma DB.")