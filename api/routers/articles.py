from http.client import HTTPException
from fastapi import APIRouter

from api.models.articles import ArticleResponse, ArticleSearchRequest
from api.retrievers.articles import ArticlesRetriever

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("", response_model=ArticleResponse)
async def search_articles(request: ArticleSearchRequest):
    try:
        results = ArticlesRetriever().search(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
