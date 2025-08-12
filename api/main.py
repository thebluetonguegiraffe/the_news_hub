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

@app.get("/articles/{topic}", response_model=ArticleResponse)
async def get_articles_by_topic(topic: str, limit: int = 10):
    """
    Get articles for a specific topic from ChromaDB.
    
    Args:
        topic: The topic to search for
        limit: Maximum number of articles to return (default: 10)
    
    Returns:
        Articles matching the topic
    """
    try:
        
        results = collection.get(
            where={"topic": topic},
            include=["documents", "metadatas", "ids"]
        )
        return ArticleResponse(
            documents=results.get("documents", []),
            metadatas=results.get("metadatas", []),
            ids=results.get("ids", [])
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/answer-question")
async def news_rs_by_question(
    question: str = Query(
        description="Question to be asked to the Recommender System"
    )
):
    """Recommends articles based on input query"""
    rs = RecommenderSystem()
    return rs.ask_by_query(question=question)
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000) 