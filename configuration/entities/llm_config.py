import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    model_config = SettingsConfigDict(
            env_file=(".env", f".env.{os.getenv('ENV', 'development')}"),
            env_file_encoding="utf-8",
            case_sensitive=False,
            env_prefix="LLM_",
    )


    llm_model_name: str = "gpt-4o"
    llm_api_key: str = "EMPTY"
    llm_api_base: str = "https://api.groq.com/openai/v1"
