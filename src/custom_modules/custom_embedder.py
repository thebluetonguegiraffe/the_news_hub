from typing import List

from openai import OpenAI
from chromadb import EmbeddingFunction


class CustomEmbedder(EmbeddingFunction):
    def __init__(self, model: str, endpoint: str, token: str):
        self.model = model
        self.endpoint = endpoint
        self.open_ai_client = OpenAI(base_url=self.endpoint, api_key=token)

    def __call__(self, docs: List[str]) -> List[List[float]]:
        response = self.open_ai_client.embeddings.create(input=docs, model=self.model)
        return [d.embedding for d in response.data]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.__call__(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]
