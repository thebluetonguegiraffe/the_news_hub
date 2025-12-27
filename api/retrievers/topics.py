from datetime import timedelta, timezone
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime

from src.core.mongo_client import CustomMongoClient
from config import mongo_configuration


class TopicResponse(BaseModel):
    topics: List[Dict]
    from_date: datetime
    to_date: datetime


class TopicsRetriever:

    PROJECTION_FIELDS = {
        "_id": 1,
        "description": 1,
        "topics_per_day": 1,
        "topic_ca": 1,
        "topic_es": 1,
        "description_ca": 1,
        "description_es": 1,
    }

    def __init__(self):
        self.mongo = CustomMongoClient

    def parse_mongo_results(self, mongo_results: List) -> List[Dict]:
        period_topics = []
        for doc in mongo_results:
            topics_per_day = doc["topics_per_day"]
            matched_topics_per_day = {}
            for registry in topics_per_day:
                registry_date = datetime.fromisoformat(
                    registry["date"].replace("Z", "+00:00")
                ).replace(tzinfo=None)
                if self.from_date <= registry_date <= self.to_date and registry["docs_number"] > 0:
                    date_only = registry_date.date()

                    if date_only in matched_topics_per_day:
                        matched_topics_per_day[date_only] += registry["docs_number"]
                    else:
                        matched_topics_per_day[date_only] = registry["docs_number"]

            if doc["_id"] != "no_topic":
                topic = {
                    "name": doc["_id"],
                    "description": doc.get("description"),
                    "topics_per_day": matched_topics_per_day,
                    "topic_ca": doc.get("topic_ca"),
                    "topic_es": doc.get("topic_es"),
                    "description_ca": doc.get("description_ca"),
                    "description_es": doc.get("description_es"),
                }
                period_topics.append(topic)
        return period_topics

    def get_topics_by_date_range(self, from_date: datetime, to_date: datetime) -> TopicResponse:

        if not from_date and not to_date:
            today = datetime.now(timezone.utc)
            yesterday = today - timedelta(days=1)

            start_point = yesterday.replace(hour=23, minute=55, second=0, microsecond=0)
            self.from_date = start_point
            self.to_date = start_point + timedelta(days=1)
        else:
            self.from_date = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
            self.to_date = to_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        with self.mongo() as client:
            db = client[mongo_configuration["db"]]
            mongo_collection = db[mongo_configuration["collection"]]
            results = mongo_collection.find(
                filter={
                    "topics_per_day": {
                        "$elemMatch": {
                            "date": {
                                "$gte": self.from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                "$lte": self.to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                            },
                            "docs_number": {"$gt": 0},
                        }
                    }
                },
                projection=self.PROJECTION_FIELDS,
            )
            mongo_results = list(results)
        parsed_topics = self.parse_mongo_results(mongo_results=mongo_results)
        return TopicResponse(topics=parsed_topics, from_date=from_date, to_date=to_date)

    def get_description_by_id(self, topic_id: str) -> Dict:
        with self.mongo() as client:
            db = client[mongo_configuration["db"]]
            collection = db[mongo_configuration["collection"]]
            result = collection.find_one({"_id": topic_id}, self.PROJECTION_FIELDS)

            return {
                "topic": result["_id"],
                "description": result.get("description"),
                "topic_ca": result.get("topic_ca"),
                "topic_es": result.get("topic_es"),
                "description_ca": result.get("description_ca"),
                "description_es": result.get("description_es"),
            }
