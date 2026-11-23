"""Read the concrete day-to-day story labels produced by the enrichment DAG.

Distinct from `/topics`, which serves the canonical categories: a category is a
stable axis to compare across days, a trend names one specific story on one day.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel

from src.core.mongo_client import CustomMongoClient
from config import mongo_configuration


class TrendResponse(BaseModel):
    trends: List[Dict]
    from_date: datetime
    to_date: datetime


class TrendsRetriever:
    DEFAULT_WINDOW_DAYS = 1
    MAX_TRENDS = 200

    def __init__(self):
        self.mongo = CustomMongoClient

    def get_trends_by_date_range(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        category: Optional[str] = None,
    ) -> TrendResponse:
        if not from_date or not to_date:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            to_date = now
            from_date = now - timedelta(days=self.DEFAULT_WINDOW_DAYS)
        else:
            from_date = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
            to_date = to_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        query: Dict = {
            "date": {
                "$gte": from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "$lte": to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            }
        }
        if category:
            query["category"] = category

        with self.mongo() as client:
            collection = client[mongo_configuration["db"]][
                mongo_configuration["trends_collection"]
            ]
            results = list(
                collection.find(query, {"_id": 0})
                .sort("docs_number", -1)
                .limit(self.MAX_TRENDS)
            )

        return TrendResponse(trends=results, from_date=from_date, to_date=to_date)
