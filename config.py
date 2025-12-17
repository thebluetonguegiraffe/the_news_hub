project_root = "./"

chroma_configuration = {
    # "host": "localhost",
    # "port": 8000,
    "database": "the_news_hub",
    "collection_name": "news"
}

mongo_configuration = {
    "host": "mongodb://localhost:27017/",
    "db": "the_news_hub",
    "collection": "topics",
}

embeddings_configuration = {
    "endpoint": "https://models.github.ai/inference",
    "model": "openai/text-embedding-3-small",
}

news_api_configuration = {"url": "https://api.finlight.me/v2/", "endpoint": "articles/"}

chat_configuration = {
    "endpoint": "https://models.github.ai/inference/chat/completions",
    "model": "openai/gpt-4.1-mini",
    "ask_hub": "openai/gpt-4.1",
}
