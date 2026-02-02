from fastapi import APIRouter, Depends, HTTPException

from api.models.articles import ArticleResponse, ArticleSearchRequest
from api.retrievers.articles import ArticlesRetriever
from api.security import verify_token

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("", response_model=ArticleResponse)
async def search_articles(request: ArticleSearchRequest, token_data: dict = Depends(verify_token)):
    try:
        results = ArticlesRetriever().search(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
