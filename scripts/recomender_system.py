

import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

from src.vectorized_database import VectorizedDatabase
from src.config import db_configuration
from src.custom_chatmodel import CustomChatModel
from templates.news_templates import rag_rs_template

class RecommenderSystem():

    def serialize_docs_json(self, docs):
        return json.dumps([
            {
                "id": d.id,
                "url": d.metadata.get("url"),
                "topic": d.metadata.get("topic"),
                "source": d.metadata.get("source"),
                "date": d.metadata.get("date"),
                "content": d.page_content
            }
            for d in docs
        ], ensure_ascii=False)

    def ask_by_query(self, question: str):
        project_root = Path(__file__).resolve().parent.parent
        db_path = db_configuration["db_path"]
        collection_name = db_configuration["collection_name"]
        
        retriever = VectorizedDatabase.from_config(
        persist_directory= f"{project_root}/db/{db_path}",
        collection_name=collection_name
        )
        
        prompt_template = CustomChatModel.create_prompt_template(rag_rs_template)
        llm = CustomChatModel.from_config()

        rag_chain = (
            {
            "context": lambda x: self.serialize_docs_json(retriever.invoke(x["question"])),
            "question": lambda x: x["question"]
            }
            | prompt_template
            | llm
        )

        response = rag_chain.invoke({"question": question})
        parsed_response = json.loads(response.content)
        return parsed_response

if __name__=="__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Ask a question to the news recommender system.")
    parser.add_argument("--question", nargs="*", help="The question to ask")
    args = parser.parse_args()

    rs = RecommenderSystem()
    response = rs.ask_by_query(question=args.question[0])
    print(response)



   