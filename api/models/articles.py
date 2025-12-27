
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict

from api.models.range_date import RangeDate


class ArticleSearchRequest(BaseModel):
    topic: Optional[str] = None
    sources: Optional[List[str]] = Field(default_factory=list) 
    date_range: RangeDate = Field(default_factory=RangeDate)
    limit: int = Field(100, ge=1, le=300)

    @field_validator('sources', mode='before')
    @classmethod
    def split_sources(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(',') if s.strip()]
        return v


class ArticleResponse(BaseModel):
    num_articles: int
    articles: List[Dict]
    topic: Optional[str]
    source: List[str]
    from_date: Optional[datetime]
    to_date: Optional[datetime]
