from fastapi import APIRouter
from fastapi.params import Depends, Query

from api.models.range_date import RangeDate
from api.retrievers.articles import ArticlesRetriever


router = APIRouter(prefix="/articles", tags=["articles"])


def get_articles_retriever():
    return ArticlesRetriever()


@router.get("/")
async def get_articles(
    range_date: RangeDate = Depends(),
    limit: int = Query(default=100, ge=1, le=100, description="Number of articles to return"),
    retriever: ArticlesRetriever = Depends(get_articles_retriever),
    # token_data: dict = Depends(verify_token)
):
    articles = retriever.get_articles(
        from_date=range_date.from_date,
        to_date=range_date.to_date,
        limit=limit
    )

    return articles


@router.get("/{topic}")
async def get_articles_by_topic(
    topic: str,
    range_date: RangeDate = Depends(),
    limit: int = Query(default=10, ge=1, le=100, description="Number of articles to return"),
    retriever: ArticlesRetriever = Depends(get_articles_retriever),
    # token_data: dict = Depends(verify_token),
):

    return retriever.get_articles_by_topic(
        topic=topic, from_date=range_date.from_date, to_date=range_date.to_date, limit=limit
    )
