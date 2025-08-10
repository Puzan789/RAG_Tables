from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    GROQ_MODEL: str
    GROQ_API_KEY: str
    GOOGLE_API_KEY: str
    GOOGLE_EMBEDDINGS_MODEL: str
    QDRANT_URL: str


settings = Settings()
