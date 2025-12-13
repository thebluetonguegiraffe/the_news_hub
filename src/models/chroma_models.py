import hashlib
from datetime import datetime, time
from typing import List, Optional
from pydantic import BaseModel, model_validator


class Metadata(BaseModel):
    url: str
    topic: Optional[str] = None
    title: str
    title_es: str
    title_ca: str
    excerpt: str
    excerpt_es: str
    excerpt_ca: str
    image: List[str]
    source: str
    published_date: Optional[datetime] = None
    ingestion_date: datetime = None
    modification_date: Optional[datetime] = None
    timestamp: Optional[float] = None

    def to_dict(self) -> dict:
        modification_date = datetime.combine(datetime.today().date(), time(23, 55, 0))
        data = {
            "url": self.url,
            "topic": self.topic or "",  # API articles do not contain topic
            "title": self.title.strip(),
            "title_es": self.title_es.strip(),
            "title_ca": self.title_ca.strip(),
            "excerpt": self.excerpt.strip(),
            "excerpt_es": self.excerpt_es.strip(),
            "excerpt_ca": self.excerpt_ca.strip(),
            "image": ", ".join(self.image),
            "source": self.source.lower(),
            "published_date": (
                self.published_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                if self.published_date
                else modification_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            ),
            "modification_date": modification_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "ingestion_date": (
                self.ingestion_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                if self.ingestion_date
                else modification_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            ),
            "timestamp": (
                self.ingestion_date.timestamp()
                if self.ingestion_date
                else modification_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            ),
        }
        return data


class ChromaDoc(BaseModel):
    id: str | None = None
    document: str
    metadata: Metadata

    @model_validator(mode="after")
    def set_id(self):
        raw = f"{self.document}".encode()
        self.id = hashlib.sha256(raw).hexdigest()
        return self
