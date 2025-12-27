from collections import defaultdict
from dotenv import load_dotenv

import logging
from config import chroma_configuration, project_root
from src.core.chroma_database import ChromaDatabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    load_dotenv()
    db_path = chroma_configuration["db_path"]
    collection_name = chroma_configuration["collection_name"]

    logger.info("Initializing vectorized database")
    db_client = ChromaDatabase(
        persist_directory=f"{project_root}/db/{db_path}", collection_name=collection_name
    )

    collection = db_client.get_collection()
    docs = collection.get()

    docs_by_text = defaultdict(list)

    for i, doc_id in enumerate(docs["ids"]):
        document_text = docs["documents"][i] if docs["documents"] else ""
        metadata = docs["metadatas"][i] if docs["metadatas"] else {}
        embedding = docs["embeddings"][i] if docs["embeddings"] else None

        doc_info = {
            "id": doc_id,
            "text": document_text,
            "metadata": metadata,
            "embedding": embedding,
        }

        docs_by_text[document_text].append(doc_info)

    duplicates = {text: docs for text, docs in docs_by_text.items() if len(docs) > 1}

    for doc in duplicates.values():
        for duplicate_doc in doc[1:]:
            doc_id_to_delete = duplicate_doc["id"]
            logger.info(f"Deleting duplicate document with ID: {doc_id_to_delete}")
            collection.delete(ids=[doc_id_to_delete])
