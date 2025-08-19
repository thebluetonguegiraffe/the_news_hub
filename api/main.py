from collections import defaultdict
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Dict, Any
import sys
import os
from pathlib import Path

from dotenv import load_dotenv

# Add the parent directory to sys.path so 'src' can be imported
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from scripts.recomender_system import RecommenderSystem
from src.sql_client import TopicsDBClient
from src.vectorized_database import VectorizedDatabase
from src.config import db_configuration
from src.get_news_info_by_link import NewsScrapper

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

# Initialize SQL client
sql_client = TopicsDBClient(sql_db_path)

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
        start = datetime.fromisoformat(from_date).date()
        end = datetime.fromisoformat(to_date).date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    if start > end:
        raise HTTPException(status_code=400, detail="'from' date must be before or equal to 'to' date")

    try:
        all_topics = sql_client.get_all_topics()
        period_topics = []
        for topic, topic_date, description in all_topics:
            try:
                topic_datetime = datetime.fromisoformat(topic_date).date()
                if start <= topic_datetime <= end:
                    results = collection.get(
                        where={"topic": topic},
                    )
                    topic = {
                        "name": topic,
                        "count": len(results['ids']),
                        "description": description,
                    }   
                    period_topics.append(topic)

            except ValueError:
                # Skip topics with invalid date format
                continue
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
        scrapper = NewsScrapper()
        articles = []
        for i, result in enumerate(results['metadatas']):
            if result.get("source") in ["www.nytimes.com", "www.washingtonpost.com"]:  # TODO: filter sources
                continue
            article = defaultdict(dict)
            article["date"] = result.get("date")
            article["topic"] = result.get("topic")
            article["topic"] = result.get("topic")
            article["source"] = result.get("source")
            article["url"] = result.get("url")
            print(article["url"])
            
            scrapped_data = scrapper.extract(article["url"])
            article["image"] = scrapped_data.get("image", None)
            article["excerpt"] = scrapped_data.get("excerpt", "")
            article["title"] = scrapped_data.get("title", None)
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
        scrapper = NewsScrapper()
        for i, article in enumerate(articles):
            url = article.get("url")
            scrapped_data = scrapper.extract(url)
            article["image"] = scrapped_data.get("image", None)
            article["excerpt"] = scrapped_data.get("excerpt", "")
            article["title"] = scrapped_data.get("title", None)
            article["id"] = i


    return {
        "summary": response.get("summary", ""),
        "articles": articles
    }


@app.get("/latest_news")
async def get_latest_news():
    """Retrieves 6 random articles from the database"""
    results = collection.get(limit=6)
    scrapper = NewsScrapper()
    articles = []
    for i, result in enumerate(results['metadatas']):
        if result.get("source") == "www.nytimes.com": # TODO
            continue
        article = defaultdict(dict)
        article["date"] = result.get("date")
        article["topic"] = result.get("topic")
        article["topic"] = result.get("topic")
        article["source"] = result.get("source")
        article["url"] = result.get("url")
        
        scrapped_data = scrapper.extract(article["url"])
        article["image"] = scrapped_data.get("image", None)
        article["excerpt"] = scrapped_data.get("excerpt", "")
        article["title"] = scrapped_data.get("title", None)
        article["id"] = i
        articles.append(article)


    return {
        "articles": articles
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000) 