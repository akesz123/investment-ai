from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = 'Investment AI'
    debug: bool = True
    database_url: str = 'sqlite:///./investment_ai.db'
    class Config:
        env_file = '.env'

settings = Settings()
