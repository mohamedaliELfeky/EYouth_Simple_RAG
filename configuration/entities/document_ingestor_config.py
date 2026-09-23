import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class DocumentIngestorConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{os.getenv('ENV', 'development')}"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="INGESTOR_",
    )

    ingestor_persist_dir: str = "./chroma_db"
    ingestor_collection_name: str = "documents"
    ingestor_chunker: str = "HybridChunker"
    ingestor_batch_size: int = Field(default=256, gt=0, description="Batch size for document ingestion")
