
import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class ChromaRetrieverConfig(BaseSettings):

    model_config = SettingsConfigDict(env_file=(".env", f".env.{os.getenv('ENV', 'development')}"),
                                       env_file_encoding="utf-8",
                                       case_sensitive=False,
                                       extra="ignore",
                                       env_prefix="CHROMA_RETRIEVER_",
                                    )


    chroma_retriever_k:int = Field(default=5, gt=0,description="Number of top documents to retrieve from Chroma for a given query.")
    chroma_retriever_persist_dir:str = Field(default="./chroma_persist", description="Directory to persist Chroma data.")
    chroma_retriever_collection_name:str = Field(default="documents", description="Name of the Chroma collection to use.")