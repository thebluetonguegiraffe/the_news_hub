import os
from typing import Dict, List
from dotenv import load_dotenv

from openai import OpenAI
from chromadb import Documents, EmbeddingFunction, HttpClient, Embeddings, CloudClient

from src.models.chroma_models import ChromaDoc
from config import chroma_configuration


class CustomEmbedder(EmbeddingFunction):

    def __init__(self):
        """Initialize the OpenAI client with GitHub AI endpoint."""
        self.open_ai_client = OpenAI(
            base_url="https://models.github.ai/inference", api_key=os.getenv("GITHUB_TOKEN")
        )
        self.model = "openai/text-embedding-3-small"

    def __call__(self, texts: Documents) -> Embeddings:
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return []

        response = self.open_ai_client.embeddings.create(input=texts, model=self.model)

        embeddings = []
        for data in response.data:
            emb = data.embedding
            if hasattr(emb, "tolist"):
                embeddings.append(emb.tolist())
            elif isinstance(emb, list):
                embeddings.append(emb)
            else:
                embeddings.append(list(emb))
        return embeddings


class ChromaDatabase:
    def __init__(self, collection_name: str):
        if chroma_configuration.get("host") == "localhost":
            self.client = HttpClient(
                host=chroma_configuration["host"], port=chroma_configuration["port"]
            )
        else:
            self.client = CloudClient(
                tenant="9afc23b2-89c9-463c-b136-cf99ce4b7853",
                database=chroma_configuration["database"],
                api_key=os.getenv("CHROMA_DB_TOKEN"),
            )

        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=CustomEmbedder()
        )

    def get_collection(self):
        return self.collection

    def add_documents(self, documents: List[ChromaDoc]):
        self.collection.add(
            documents=[d.document for d in documents],
            ids=[str(d.id) for d in documents],
            metadatas=[d.metadata.to_dict() for d in documents],
        )

    def add_document(self, d: ChromaDoc):
        self.collection.add(
            documents=d.document,
            ids=str(d.id),
            metadatas=d.metadata.to_dict(),
        )

    def update_documents(self, documents: Dict):
        self.collection.update(
            ids=documents["ids"],
            metadatas=documents["metadatas"],
        )

    def search(self, query: str, top_k: int = 5, chroma_filter: Dict = None) -> List[Dict]:
        query_results = self.collection.query(
            query_texts=[query],  # ChromaDB will embed this using CustomEmbedder
            n_results=top_k,
            where=chroma_filter,
        )
        results = []
        for _id, doc, metadata in zip(
            query_results["ids"][0], query_results["documents"][0], query_results["metadatas"][0]
        ):
            doc = {"id": _id, "document": doc, "metadata": metadata}
            results.append(doc)
        return results

    def search_with_filter(
        self,
        chroma_filter: Dict,
        limit: int = None,
        include: List = ["documents", "metadatas"],
        offset: int = 0,
    ) -> List[Dict]:
        if chroma_filter and any(chroma_filter.values()):
            result = self.collection.get(
                where=chroma_filter, limit=limit, include=include, offset=offset
            )
        else:
            result = self.collection.get(limit=limit, include=include, offset=offset)
        return result

    def list_collections(self) -> list:
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            print(f"Failed to list collections: {e}")
            return []

    def delete_collection(self, collection_name: str):
        """Delete the current collection from the Chroma database."""
        try:
            self.client.delete_collection(name=collection_name)
            print(f"Collection '{collection_name}' deleted successfully.")
        except Exception as e:
            print(f"Failed to delete collection '{collection_name}': {e}")


if __name__ == "__main__":
    load_dotenv()
    db = ChromaDatabase(collection_name=chroma_configuration["collection_name"])
    print(db.list_collections())
    # db.delete_collection(collection_name="news")  # Deletes the collection
