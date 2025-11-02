from fastapi import APIRouter
from fastapi.params import Depends
from api.models.range_date import RangeDate
from api.retrievers.topics import TopicResponse, TopicsRetriever


router = APIRouter(prefix="/topics", tags=["topics"])


def get_topics_retriever():
    return TopicsRetriever()


@router.get("/", response_model=TopicResponse)
async def get_topics_by_date_range(
    range_date: RangeDate = Depends(),
    retriever: TopicsRetriever = Depends(get_topics_retriever),
    # token_data: dict = Depends(verify_token),
):

    return retriever.get_topics_by_date_range(range_date.from_date, range_date.to_date)
