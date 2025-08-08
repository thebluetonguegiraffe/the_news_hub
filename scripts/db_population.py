
import os
from pathlib import Path

from chromadb import PersistentClient
from dotenv import load_dotenv

from src.api_client import APIClient
from src.vectorized_database import VectorizedDatabase
from src.custom_embedder import CustomEmbedder
from src.utils import parse_finlight
from src.config import news_api_configuration, db_configuration, embeddings_configuration



if __name__=="__main__":

    load_dotenv()

    api_client = APIClient(
        base_url=news_api_configuration["url"],
        headers={
            "X-API-KEY": os.getenv("FINLIGHT_API_TOKEN")
        }
    )

    response = api_client.post(
        endpoint=news_api_configuration["endpoint"],
        json={
            "sources": ["www.bbc.com", "www.nytimes.com", "www.theguardian.com", "www.washingtonpost.com"],
            "from": "2025-07-31T00:00",
	        "to": "2025-08-01T00:00",
            "pageSize": "100"
        }
    )

    articles = response["articles"]

    documents, ids, metadatas = map(list, zip(*(parse_finlight(article) for article in articles)))

    project_root = Path(__file__).resolve().parent.parent
    db_path = db_configuration["db_path"]
    collection_name = db_configuration["collection_name"]

    chroma = VectorizedDatabase(
        persist_directory=f"{project_root}/db/{db_path}",
        collection_name=collection_name
    )

    collection = chroma.get_collection()

    collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas,
    )
