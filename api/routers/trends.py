from typing import Optional

from fastapi import APIRouter
from fastapi.params import Depends

from api.models.range_date import RangeDate
from api.retrievers.trends import TrendResponse, TrendsRetriever
from api.security import verify_token


router = APIRouter(prefix="/trends", tags=["trends"])


def get_trends_retriever():
    return TrendsRetriever()


@router.get("/", response_model=TrendResponse)
async def get_trends_by_date_range(
    range_date: RangeDate = Depends(),
    category: Optional[str] = None,
    retriever: TrendsRetriever = Depends(get_trends_retriever),
    token_data: dict = Depends(verify_token),
):
    """Concrete story labels for the period, most covered first."""
    return retriever.get_trends_by_date_range(
        range_date.from_date, range_date.to_date, category
    )
