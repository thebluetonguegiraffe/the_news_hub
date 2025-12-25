from fastapi import APIRouter
from fastapi.params import Depends
from api.models.range_date import RangeDate
from api.retrievers.topics import TopicResponse, TopicsRetriever
from api.security import verify_token


router = APIRouter(prefix="/topics", tags=["topics"])


def get_topics_retriever():
    return TopicsRetriever()


@router.get("/", response_model=TopicResponse)
async def get_topics_by_date_range(
    range_date: RangeDate = Depends(),
    retriever: TopicsRetriever = Depends(get_topics_retriever),
    token_data: dict = Depends(verify_token),
):

    return retriever.get_topics_by_date_range(range_date.from_date, range_date.to_date)


@router.get("/description/{topic_id}", response_model=str)
async def get_topic_description(
    topic_id: str,
    retriever: TopicsRetriever = Depends(get_topics_retriever),
    token_data: dict = Depends(verify_token),
):
    description = retriever.get_description_by_id(topic_id)
    if description is None:
        return "Description not found."
    return description
