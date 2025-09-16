import argparse
import json
from dotenv import load_dotenv

import re
from typing import  Tuple

from config import db_configuration, project_root
from scripts.recomender_system.constants import NUMERIC_TIME_PATTERNS, TIME_EXPRESSIONS
from src.vectorized_database import VectorizedDatabase
from src.llm_engine import create_prompt_template, create_llm
from templates.news_templates import rag_rs_template


class RecommenderSystem:
    TIME_WINDOW = (-4,0)

    def __init__(self, vectorized_db: VectorizedDatabase):
        self.vectorized_db=vectorized_db

    def serialize_docs_json(self, docs):
        return json.dumps(
            [
                {
                    "chroma_id": d.id,
                    "publish_date": d.metadata.get("publish_date"),
                    "topic": d.metadata.get("topic"),
                    "source": d.metadata.get("source"),
                    "url": d.metadata.get("url"),
                    "image": d.metadata.get("image"),
                    "excerpt": d.metadata.get("excerpt"),
                    "title": d.metadata.get("title"),
                }
                for d in docs
            ],
            ensure_ascii=False,
        )

    def ask_by_query(self, question: str):
        # db_path = db_configuration["db_path"]
        # collection_name = db_configuration["collection_name"]

        time_window = self.get_time_window(question)

        llm = create_llm()
        prompt_template = create_prompt_template(rag_rs_template)
        retriever = self.vectorized_db.get_retriever(time_window=time_window)

        rag_chain = (
            {
                "context": lambda x: self.serialize_docs_json(retriever.invoke(x["question"])),
                "question": lambda x: x["question"],
            }
            | prompt_template
            | llm
        )

        response = rag_chain.invoke({"question": question})
        parsed_response = json.loads(response.content)
        return parsed_response

    def get_time_window(self, text: str) -> Tuple[int, int]:
        results = []
        text_lower = text.lower()
        
        # Search for exact matches from dictionary
        for expression, days_offset in TIME_EXPRESSIONS.items():
            pattern = r'\b' + re.escape(expression) + r'\b'
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                results.append(days_offset)
        
        # Search for numeric patterns
        for pattern, offset_func in NUMERIC_TIME_PATTERNS.items():
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                number = match.group(1)
                days_offset = offset_func(number)
                results.append(days_offset)
        
        return results[0] if results else self.TIME_WINDOW
    

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Ask a question to the news recommender system.")
    parser.add_argument("--question", nargs="*", help="The question to ask")
    args = parser.parse_args()
    
    chroma_db_path = f"{project_root}db/{db_configuration['db_path']}"
    rs = RecommenderSystem(
        vectorized_db=VectorizedDatabase(
            persist_directory=chroma_db_path,
            collection_name=db_configuration["collection_name"],
        )
    )
    response = rs.ask_by_query(question="What has happened this week in EEUU")
    print(response)
