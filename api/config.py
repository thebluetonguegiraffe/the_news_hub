from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "The News HUB API"
    VERSION: str = "1.0.0"
    API_ACCESS_TOKEN: str | None = None
    ENABLE_TOKEN_AUTH: bool = False
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://the_news_hub.thebluetonguegiraffe.online",
    ]


settings = Settings()
