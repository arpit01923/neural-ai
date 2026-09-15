from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: str = "."

    # Database
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # Ollama
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # LangSmith
    LANGSMITH_TRACING: bool = False
    LANGSMITH_ENDPOINT: str | None = None
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_PROJECT: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
