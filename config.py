project_root = "./"

chroma_configuration = {
    # "host": "localhost",
    # "port": 8000,
    "database": "the_news_hub",
    "collection_name": "news_2026_mistral"
}

mongo_configuration = {
    "host": "mongodb://localhost:27017/",
    "db": "the_news_hub",
    "collection": "topics_2026",
}

embeddings_configuration = {
    "endpoint": "https://api.mistral.ai/v1",
    "model": "mistral-embed",
}

news_api_configuration = {"url": "https://api.finlight.me/v2/", "endpoint": "articles/"}

chat_configuration = {
    "endpoint": "https://api.mistral.ai/v1",
    "model": "ministral-3b-latest",
    "ask_hub": "ministral-3b-latest",
}
