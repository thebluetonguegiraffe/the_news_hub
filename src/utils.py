

from typing import Dict, List, Union
import uuid


def parse_news_api(input_data: Dict) -> Union[str, str, List]:
    document = input_data.get("description")
    doc_id = str(uuid.uuid4())
    metadata =  {
            "title": input_data.get("title"),
            "author": input_data.get("author"),
            "url": input_data.get("url"),
        }
    return document, doc_id, metadata

def parse_finlight(input_data: Dict) -> Union[str, str, List]:
    document = input_data.get("summary")
    doc_id = str(uuid.uuid4())
    metadata =  {
            "date": input_data.get("publishDate"),
            "source": input_data.get("source"),
            "url": input_data.get("link"),
        }
    return document, doc_id, metadata