
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict

from api.models.range_date import RangeDate


class ArticleSearchRequest(BaseModel):
    topic: Optional[str] = None
    source: Optional[str] = None
    language: Literal["es", "en", "ca"] = "en"
    date_range: RangeDate = Field(default_factory=RangeDate)
    limit: int = Field(100, ge=1, le=100)


class ArticleResponse(BaseModel):
    num_articles: int
    articles: List[Dict]
    topic: Optional[str]
    source: Optional[str]
    from_date: Optional[datetime]
    to_date: Optional[datetime]
