from datetime import datetime, timedelta, timezone
import os
from typing import Tuple
from chromadb import PersistentClient
from langchain_chroma import Chroma

from config import embeddings_configuration
from src.custom_modules.custom_embedder import CustomEmbedder


class VectorizedDatabase:

    def __init__(self, persist_directory: str, collection_name: str, time_window: Tuple[int, int]):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.time_window = time_window
        self.embedding_function = CustomEmbedder(
            model=embeddings_configuration["model"],
            endpoint=embeddings_configuration["endpoint"],
            token=os.getenv("GITHUB_TOKEN"),
        )

        self.client = PersistentClient(path=self.persist_directory)

    def get_collection(self):
        collection = self.client.get_or_create_collection(
            name=self.collection_name, embedding_function=self.embedding_function
        )

        return collection

    def get_retriever(self):
        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_function,
            collection_name=self.collection_name,
        )

        today = datetime.now(timezone.utc).replace(hour=23, minute=55, second=0, microsecond=0)
        
        start = today + timedelta(days=self.time_window[0])
        start_iso = start.isoformat().replace('+00:00', '.000000')
        start_ts = datetime.fromisoformat(start_iso).timestamp()

        end = today + timedelta(days=self.time_window[1])
        end_iso = end.isoformat().replace('+00:00', '.000000')
        end_ts = datetime.fromisoformat(end_iso).timestamp()

        retriever = vectorstore.as_retriever(
            search_type="similarity", 
            search_kwargs={
                "k": 3,
                "filter": {
                    "$and": [
                        {"timestamp": {"$gte": start_ts}},
                        {"timestamp": {"$lte": end_ts}}
                    ]
                }
            }
        )
        return retriever

    @classmethod
    def from_config(cls, persist_directory: str, collection_name: str, time_window:int):
        instance = cls(persist_directory, collection_name, time_window)
        return instance.get_retriever()
