from datetime import datetime
from typing import Dict, List, Union
import requests
import uuid


class FinlightAPIClient:
    def __init__(self, base_url: str, headers: Dict = None, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)
        self.timeout = timeout

    def get(self, endpoint: str, params: Dict = None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: Dict = None, json: Dict = None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, data=data, json=json, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def parse_finlight_article(input_data: Dict, date: datetime) -> Union[str, str, List]:
        document = input_data.get("summary")
        doc_id = str(uuid.uuid4())
        metadata = {
            "publish_date": input_data.get("publishDate"),
            "date": date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "source": input_data.get("source"),
            "url": input_data.get("link"),
            "title": input_data.get("title"),
            "excerpt": input_data.get("summary"),
            "image": " ".join(input_data.get("images")),
        }
        return document, doc_id, metadata
