from collections import defaultdict
from typing import Dict, List
from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel

from api.retrievers.articles import ArticlesRetriever
from src.chroma_rag import ChromaRAG


router = APIRouter(prefix="/ask_hub", tags=["ask_hub"])


class QuestionPayload(BaseModel):
    question: str


class RAGResponse(BaseModel):
    summary: str
    articles: List[Dict]


def get_articles_retriever():
    return ArticlesRetriever()


@router.post("/")
async def news_rs_by_question(
    payload: QuestionPayload,
    retriever: ArticlesRetriever = Depends(get_articles_retriever),
    # token_data: dict = Depends(verify_token)
):
    rag = ChromaRAG()
    response = rag.run(input_question=payload.question)

    results = defaultdict(list)
    for context in response["context"]:
        results["ids"].append(context.id)
        results["documents"].append(context.document)
        results["metadatas"].append(context.metadata)

    parsed_articles = retriever.parse_chroma_results(results)

    return RAGResponse(summary=response["answer"], articles=parsed_articles)
