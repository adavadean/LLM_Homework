from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os
load_dotenv(override=True)
class Settings(BaseSettings):
    OPENAI_API_KEY: str
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    CHROMA_DIR: str = os.getenv("CHROMA_DIR", "./chroma_db")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "book_summaries")
    ENABLE_PROFANITY_FILTER: bool = os.getenv("ENABLE_PROFANITY_FILTER", "true").lower() == "true"
    TOP_K: int = int(os.getenv("TOP_K", "3"))
    CORS_ALLOW_ORIGINS: List[str] = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173").split(",")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
