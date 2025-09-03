import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

from config import db_configuration
from src.vectorized_database import VectorizedDatabase
from src.llm_engine import create_prompt_template, create_llm
from templates.news_templates import rag_rs_template, asked_frecuency_template


class RecommenderSystem:

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
        project_root = Path(__file__).resolve().parent.parent
        db_path = db_configuration["db_path"]
        collection_name = db_configuration["collection_name"]

        llm = create_llm()
        preprocessing = create_prompt_template(asked_frecuency_template)

        preprocessing_chain =  preprocessing | llm
        preprocessing_response = preprocessing_chain.invoke(
            {
                "question": question,
            }
        )
        prompt_template = create_prompt_template(rag_rs_template)
        retriever = VectorizedDatabase.from_config(
            persist_directory=f"{project_root}/db/{db_path}", collection_name=collection_name, time_window=preprocessing_response.content
        )

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


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Ask a question to the news recommender system.")
    parser.add_argument("--question", nargs="*", help="The question to ask")
    args = parser.parse_args()

    rs = RecommenderSystem()
    response = rs.ask_by_query(question="What has happened this week in EEUU")
    print(response)
