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
    def __init__(self):
        self.mongo = CustomMongoClient

    def parse_mongo_results(self, mongo_results: List):
        period_topics = []
        for doc in list(mongo_results):
            topics_per_day = doc["topics_per_day"]
            matched_topics_per_day = {}

            for registry in topics_per_day:
                registry_date = datetime.fromisoformat(registry["date"].replace("Z", "+00:00"))
                if self.from_date <= registry_date <= self.to_date and registry["docs_number"] > 0:
                    matched_topics_per_day[registry_date] = registry["docs_number"]

            if doc["_id"] != "no_topic":
                topic = {
                    "name": doc["_id"],
                    "description": doc.get("description"),
                    "topics_per_day": matched_topics_per_day,
                }
                period_topics.append(topic)
        return period_topics

    def get_topics_by_date_range(self, from_date: datetime, to_date: datetime) -> TopicResponse:

        if not to_date:
            to_date = from_date + timedelta(days=1)

        self.from_date = from_date.replace(tzinfo=timezone.utc)
        self.to_date = to_date.replace(tzinfo=timezone.utc)

        # get full date range
        self.from_date = self.from_date.replace(hour=0, minute=0, second=0, microsecond=0)
        self.to_date = self.to_date.replace(hour=23, minute=59, second=59, microsecond=999999)

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
                            "docs_number": {"$gt": 0}
                        }
                    }
                },
                projection={"_id": 1, "description": 1, "topics_per_day": 1},
            )
            mongo_results = list(results)
        parsed_topics = self.parse_mongo_results(mongo_results=mongo_results)
        return TopicResponse(topics=parsed_topics, from_date=from_date, to_date=to_date)
