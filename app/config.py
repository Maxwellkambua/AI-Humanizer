import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "groq")

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")

    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    VERIFY_ENABLED: bool = os.getenv("VERIFY_ENABLED", "true").lower() == "true"
    MAX_CONCURRENCY: int = int(os.getenv("MAX_CONCURRENCY", "3"))


settings = Settings()