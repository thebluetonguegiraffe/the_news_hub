
from dotenv import load_dotenv
from src.core.chroma_database import ChromaDatabase
from config import chroma_configuration


if __name__ == "__main__":
    load_dotenv()
    chroma_db = ChromaDatabase(collection_name=chroma_configuration["collection_name"])
    collection = chroma_db.client.delete_collection("news")
