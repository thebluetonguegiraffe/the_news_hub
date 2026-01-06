from datetime import datetime
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config import settings
from api.routers import ask_hub, topics, articles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("api_main")
logger.setLevel(logging.INFO)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for querying topics and news articles",
    version=settings.VERSION,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(topics.router)
app.include_router(articles.router)
app.include_router(ask_hub.router)


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


@app.get("/status")
async def health_check(
    # token_data: dict = Depends(verify_token)
):
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
