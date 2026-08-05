from pydantic_settings import BaseSettings
from pydantic import AnyUrl


class Settings(BaseSettings):
    app_name: str = "Investment AI"
    debug: bool = True

    database_url: str = "sqlite:///./investment_ai.db"

    # External API keys (optional)
    finnhub_api_key: str | None = None
    alphavantage_api_key: str | None = None
    fmp_api_key: str | None = None
    newsapi_api_key: str | None = None
    fred_api_key: str | None = None

    secret_key: str = "change_this_in_production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
