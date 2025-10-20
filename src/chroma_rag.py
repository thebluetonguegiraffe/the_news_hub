from datetime import datetime, timedelta, timezone
import os
import re
from typing import Dict
from langchain_core.runnables import RunnableLambda

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.core.chroma_database import ChromaDatabase

from config import chat_configuration, chroma_configuration
from src.constants import NUMERIC_TIME_PATTERNS, TIME_EXPRESSIONS
from src.core.translator import GoogleTranslator
from templates.news_templates import Prompts


class ChromaRAG:
    TIME_WINDOW = (-4, 0)

    def __init__(self):
        self.llm = init_chat_model(
            model=chat_configuration["ask_hub"],
            model_provider="openai",
            api_key=os.getenv("GITHUB_TOKEN"),
            base_url="https://models.github.ai/inference",
        )
        self.chroma_db = ChromaDatabase(collection_name=chroma_configuration["collection_name"])
        self.translator = GoogleTranslator()

    @classmethod
    def get_query_time_window_filter(cls, text: str) -> Dict:
        results = []
        text_lower = text.lower()

        # Search for exact matches from dictionary
        for expression, days_offset in TIME_EXPRESSIONS.items():
            pattern = r"\b" + re.escape(expression) + r"\b"
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

        time_window = results[0] if results else cls.TIME_WINDOW
        today = datetime.now(timezone.utc).replace(hour=23, minute=55, second=0, microsecond=0)

        start = today + timedelta(days=time_window[0])
        start_iso = start.isoformat().replace("+00:00", ".000000")
        start_ts = datetime.fromisoformat(start_iso).timestamp()

        end = today + timedelta(days=time_window[1])
        end_iso = end.isoformat().replace("+00:00", ".000000")
        end_ts = datetime.fromisoformat(end_iso).timestamp()

        time_window_filter = {
            "$and": [
                {"timestamp": {"$gte": start_ts}},
                {"timestamp": {"$lte": end_ts}},
            ]
        }

        return time_window_filter

    def run_llm_with_context(self, inputs):
        question = inputs["question"]
        context = inputs["context"]
        context_docs = (
            "\n\n".join([f"- {doc.document}" for doc in context])
            if context
            else "No relevant documents found."
        )

        prompt = ChatPromptTemplate.from_template(Prompts.RAG_TEMPLATE)

        llm_response = (prompt | self.llm | StrOutputParser()).invoke(
            {"context": context_docs, "question": question}
        )

        return {"answer": llm_response, "context": context}

    def run(self, input_question: str):
        source_lang = self.translator.detect_language(input_question)
        self.translator.source_lang = source_lang
        translated_question = self.translator.translate(input_question, target_lang="en")

        time_window_filter = self.get_query_time_window_filter(translated_question)

        chain = {
            "context": RunnableLambda(
                lambda q: self.chroma_db.retrieve(q, chroma_filter=time_window_filter)
            ),
            "question": RunnablePassthrough(),
        } | RunnableLambda(self.run_llm_with_context)

        result = chain.invoke(translated_question)
        self.translator.source_lang = "en"
        translated_answer = self.translator.translate(result["answer"], target_lang=source_lang)
        result["answer"] = translated_answer

        return result


if __name__ == "__main__":
    rag = ChromaRAG()
    # answer = rag_pipeline.invoke("What has happened today regarding the BBVA OPA?")
    result = rag.run("Que ha passat avui amb Pfizer?")
    print(result["answer"])
