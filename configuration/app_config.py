import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from .entities.llm_config import LLMConfig
from .entities.document_ingestor_config import DocumentIngestorConfig
from .entities.chroma_retriever_config import ChromaRetrieverConfig

class AppConfig(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=(".env", f".env.{os.getenv('ENV', 'development')}"),
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
            env_prefix="APP_",
        )


        app_name: str = "RAG_Papers"

        # ---------- LLM Config ----------
        llm_config: LLMConfig = Field(default_factory=LLMConfig)

        # ---------- Document Ingestor Config ----------
        ingestor_config: DocumentIngestorConfig = Field(default_factory=DocumentIngestorConfig)

        # ---------- Chroma Retriever Config ----------
        chroma_retriever_config: ChromaRetrieverConfig = Field(default_factory=ChromaRetrieverConfig)
        




def get_app_config() -> AppConfig:
    return AppConfig()