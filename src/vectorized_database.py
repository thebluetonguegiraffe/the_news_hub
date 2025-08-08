

import os
from pathlib import Path
from typing import List
from chromadb import PersistentClient
from langchain_chroma import Chroma

from src.config import embeddings_configuration
from src.custom_embedder import CustomEmbedder
from src.config import db_configuration, embeddings_configuration


class VectorizedDatabase:

    def __init__(self, persist_directory: str, collection_name: str):
        self.persist_directory=persist_directory
        self.collection_name=collection_name
        self.embedding_function=CustomEmbedder(
            model=embeddings_configuration["model"],
            endpoint=embeddings_configuration["endpoint"],
            token=os.getenv("GITHUB_TOKEN")
        )

        self.client = PersistentClient(
            path=self.persist_directory
        )


    def get_collection(self):        
        collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )

        return collection

    # def add(collection, documents: List, ids :List, metadatas: List):
    #     collection.add(
    #         documents=documents,
    #         ids=ids,
    #         metadatas=metadatas,
    #     )

    # def get_docs(collection):
    #     return collection.get()

    def get_retriever(self):
        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_function,
            collection_name=self.collection_name
        )

        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        return retriever
    
    @classmethod
    def from_config(cls, persist_directory: str, collection_name: str):
        instance = cls(persist_directory, collection_name)
        return instance.get_retriever()
    
