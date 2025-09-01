from collections import defaultdict
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any
import sys
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

# Add the parent directory to sys.path so 'src' can be imported
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from scripts.recomender_system import RecommenderSystem
from src.vectorized_database import VectorizedDatabase
from config import db_configuration, mongo_configuration

load_dotenv()

app = FastAPI(
    title="News RS API",
    description="API for querying topics and news articles",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",  # frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database clients
project_root = Path(__file__).resolve().parent.parent
sql_db_path = f"{project_root}/db/topics.db"
chroma_db_path = f"{project_root}/db/{db_configuration['db_path']}"

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

@app.get("/topics/", response_model=TopicResponse)
async def get_topics_by_date_range(
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
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
                filter={"topics_per_day.date": {"$gte": start, "$lte": end}}, 
                projection={"_id": 1, "description": 1, "topics_per_day": 1}
            )
            for topic_doc in list(results):
                topics_per_day = topic_doc["topics_per_day"]
                matched_topics_per_day = {}
                for date_entry in topics_per_day:
                    if start <= date_entry['date'] <= end:
                        matched_topics_per_day[date_entry['date']] = date_entry['docs_number']
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
async def get_articles_by_topic(topic: str):
    try:
        results = collection.get(
            where={"topic": topic},
            include=["metadatas"]
        )
        # TODO: topics by day
        articles = []
        for i, result in enumerate(results['metadatas']):
            # TODO: filter sources
            article = defaultdict(dict)
            article["date"] = result.get("publish_date")
            article["topic"] = result.get("topic")
            article["source"] = result.get("source")
            article["url"] = result.get("url")
            article["image"] = result.get("image", "").split(' ')
            article["excerpt"] = result.get("excerpt", "")
            article["title"] = result.get("title", None)
            article["id"] = i
            articles.append(article)

        return {
        "articles": articles
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


class QuestionPayload(BaseModel):
    question: str

@app.post("/question")
async def news_rs_by_question(payload: QuestionPayload):
    """Recommends articles based on input query"""
    rs = RecommenderSystem()

    response = rs.ask_by_query(question=payload.question)
    articles = response.get("articles", [])
    if articles:
        for i, article in enumerate(articles):
            article["url"] = article.get("url")
            article["image"] = article.get("image", "").split(' ')
            article["excerpt"] = article.get("excerpt", "")
            article["title"] = article.get("title", None)
            article["id"] = i
    return {
        "summary": response.get("summary", ""),
        "articles": articles
    }


@app.get("/latest_news")
async def get_latest_news():
    """Retrieves 6 random articles from the database"""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    dt = yesterday.replace(hour=23, minute=55, second=0, microsecond=0)
    date = dt.isoformat().replace('+00:00', '.000000Z')
    results = collection.get(
        where={"date": date},
        limit=6
    )
    articles = []
    for i, result in enumerate(results['metadatas']):

        article = defaultdict(dict)
        article["date"] = result.get("date")
        article["topic"] = result.get("topic")
        article["topic"] = result.get("topic")
        article["source"] = result.get("source")
        article["url"] = result.get("url")
        article["image"] = result.get("image", "").split(' ')
        article["excerpt"] = result.get("excerpt", "")
        article["title"] = result.get("title", None)
        article["id"] = i
        articles.append(article)


    return {
        "articles": articles
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000) 