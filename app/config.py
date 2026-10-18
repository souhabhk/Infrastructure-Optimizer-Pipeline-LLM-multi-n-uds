from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    input_path: str = "data/rapport.json"
    output_path: str = "output.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
