project_root = "./"

db_configuration = {"db_path": "news_v2", "collection_name": "news"}

mongo_configuration = {
    "host": "mongodb://localhost:27017/",
    "db": "news_hub",
    "collection": "topics",
}

db_configuration_old = {"db_path": "news_v1", "collection_name": "cnn_es_news"}

embeddings_configuration = {
    "endpoint": "https://models.github.ai/inference",
    "model": "openai/text-embedding-3-small",
}

# news_api_configuration = {
#     "url" : "https://newsapi.org/v2",
#     "endpoint" : "top-headlines/"
# }

news_api_configuration = {"url": "https://api.finlight.me/v2/", "endpoint": "articles/"}

chat_configuration = {
    "endpoint": "https://models.github.ai/inference/chat/completions",
    # "model": "xai/grok-3-mini",
    # "model": "xai/grok-3",
    "model": "openai/gpt-4.1-nano",
}
