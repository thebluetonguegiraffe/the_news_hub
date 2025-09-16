import logging
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import sys
import os

from dotenv import load_dotenv
from pymongo import MongoClient

# Add the parent directory to sys.path so 'src' can be imported
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from api.api_utils import parse_chroma_results, parse_dict_results
from scripts.recomender_system.recomender_system import RecommenderSystem
from src.vectorized_database import VectorizedDatabase
from config import db_configuration, mongo_configuration, project_root

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="News RS API",
    description="API for querying topics and news articles",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "https://the_news_hub.thebluetonguegiraffe.online",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*" ],
)

# Security scheme
security = HTTPBearer()

# Store your API tokens (in production, use database or environment variables)
VALID_API_TOKENS = {
    os.getenv("API_ACCESS_TOKEN"): {
        "name": "Frontend App",
        "permissions": ["read", "write"]
    },
}

# Token validation function
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the API token"""
    token = credentials.credentials
    
    if token not in VALID_API_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return VALID_API_TOKENS[token]

# Initialize database clients
chroma_db_path = f".{project_root}db/{db_configuration['db_path']}"

# Initialize ChromaDB client
chroma_client = VectorizedDatabase(
    persist_directory=chroma_db_path,
    collection_name=db_configuration["collection_name"]
)

collection = chroma_client.get_collection()

class TopicResponse(BaseModel):
    topics: List[Dict]
    date: str


class ArticleResponse(BaseModel):
    documents: List[str]
    metadatas: List[Dict[str, Any]]
    ids: List[str]


@app.get("/health")
async def health_check(token_data: dict = Depends(verify_token)):
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/topics/", response_model=TopicResponse)
async def get_topics_by_date_range(
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    token_data: dict = Depends(verify_token)
):
    """
    Get topics within a date range.

    Args:
        from: Start date in ISO format (YYYY-MM-DD)
        to: End date in ISO format (YYYY-MM-DD)

    Returns:
        List of topics within the specified date range.
    """

    try:
        start = datetime.fromisoformat(from_date).replace(hour=23, minute=55, second=0, microsecond=0)
        end = datetime.fromisoformat(to_date).replace(hour=23, minute=55, second=0, microsecond=0)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    if start > end:
        raise HTTPException(status_code=400, detail="'from' date must be before or equal to 'to' date")

    try:
        period_topics = []
        with MongoClient(
            host=mongo_configuration["host"],
            port=mongo_configuration.get("port", 27017),
            username=os.getenv("MONGO_INITDB_ROOT_USERNAME"),
            password=os.getenv("MONGO_INITDB_ROOT_PASSWORD"),
            authSource=mongo_configuration.get("database", "admin"),
        ) as client:
            db = client[mongo_configuration["db"]]
            mongo_collection = db[mongo_configuration["collection"]]

            results = mongo_collection.find(
                filter={
                    "topics_per_day": {
                        "$elemMatch": {
                            "date": {
                                "$gte": start,
                                "$lte": end
                            }
                        }
                    }
                },
                projection={"_id": 1, "description": 1, "topics_per_day": 1}
            )
            for topic_doc in list(results):
                topics_per_day = topic_doc["topics_per_day"]
                matched_topics_per_day = {}
                for date_entry in topics_per_day:
                    if start <= date_entry['date'] <= end:
                        matched_topics_per_day[date_entry['date']] = date_entry['docs_number']
                if topic_doc["_id"] != "no_topic":
                    topic = {
                        "name": topic_doc["_id"],
                        "description": topic_doc["description"],
                        "topics_per_day": matched_topics_per_day,
                    }
                    period_topics.append(topic) 
        return TopicResponse(topics=period_topics, date=f"{start.isoformat()} to {end.isoformat()}")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/articles/{topic}")
async def get_articles_by_topic(
    topic: str,
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    token_data: dict = Depends(verify_token)
):
    try:
        from_date = datetime.fromisoformat(from_date).replace(hour=23, minute=55, second=0, microsecond=0)
        to_date = datetime.fromisoformat(to_date).replace(hour=23, minute=55, second=0, microsecond=0)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    try:
        from_date_ts = from_date.timestamp()
        to_date_ts = to_date.timestamp()

        results = collection.get(
            where={
                "$and": [
                    {"topic": topic},
                    {"timestamp": {"$gte": from_date_ts}},
                    {"timestamp": {"$lte": to_date_ts}}
                ]
            },
            include=["metadatas"]
        )
        articles, enriched_metadata = parse_chroma_results(results)
        if enriched_metadata:
            collection.update(
                ids=list(enriched_metadata.keys()),                 
                metadatas=list(enriched_metadata.values()),     
            )
            logger.info(f"{len(enriched_metadata)} updated in Chroma DB.")

        return {"articles": articles}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


class QuestionPayload(BaseModel):
    question: str

@app.post("/question")
async def news_rs_by_question(
    payload: QuestionPayload,
    token_data: dict = Depends(verify_token)
):
    """Recommends articles based on input query"""
    rs = RecommenderSystem(
        vectorized_db=chroma_client
    )

    response = rs.ask_by_query(question=payload.question)
    results = response.get("articles", [])
    if not results:
        return {}
    articles = parse_dict_results(results)
    
    return {
        "summary": response.get("summary", ""),
        "articles": articles
    }


@app.get("/latest_news")
async def get_latest_news(
    token_data: dict = Depends(verify_token)
):
    """Retrieves 6 random articles from the database"""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    dt = yesterday.replace(hour=23, minute=55, second=0, microsecond=0)
    date = dt.isoformat().replace('+00:00', '.000000Z')
    results = collection.get(
        where={"date": date},
        limit=6
    )
    articles, enriched_metadata = parse_chroma_results(results)
    if enriched_metadata:
        collection.update(
            ids=list(enriched_metadata.keys()),                 
            metadatas=list(enriched_metadata.values()),     
        )
        logger.info(f"{len(enriched_metadata)} updated in Chroma DB.")

    return {"articles": articles}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000) 