from datetime import datetime, timedelta

from dotenv import load_dotenv
from src.core.chroma_database import ChromaDatabase

from config import chroma_configuration, mongo_configuration
from src.core.mongo_client import CustomMongoClient

if __name__ == "__main__":
    load_dotenv()
    chroma_db = ChromaDatabase(collection_name=chroma_configuration["collection_name"])

    start_date = datetime(2025, 10, 27)
    end_date = datetime(2025, 12, 4)

    with CustomMongoClient() as client:
        db = client[mongo_configuration["db"]]
        mongo_collection = db[mongo_configuration["collection"]]

        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%dT23:55:00.000Z")
            try:
                documents = chroma_db.search_with_filter({"ingestion_date": date_str})

                if not documents or not documents.get("metadatas"):
                    print(f"  -> No documents found for {date_str}")
                else:
                    topic_counts = {}
                    for md in documents["metadatas"]:
                        topic = md.get("topic", "Unknown")
                        if topic in topic_counts:
                            topic_counts[topic] += 1
                        else:
                            topic_counts[topic] = 1

                    for topic, count in topic_counts.items():
                        mongo_collection.update_one(
                            filter={"_id": topic},
                            update={
                                "$addToSet": {
                                    "topics_per_day": {"date": date_str, "docs_number": count},
                                }
                            },
                            upsert=True,
                        )
                    print(f"  -> Updated {len(topic_counts)} topics for {date_str}")

            except Exception as e:
                print(f"  -> Error processing {date_str}: {e}")

            # --- End of Logic ---

            # 4. Move to the next day
            current_date += timedelta(days=1)

    print("Batch processing complete.")
