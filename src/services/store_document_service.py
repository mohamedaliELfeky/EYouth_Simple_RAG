import os
from typing import List, Optional
from logging import getLogger
logger = getLogger(__name__)

from configuration.app_config import AppConfig
from src.ingestioners.ingest_docling import DocumentIngestor


class StoreDocumentService:
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config


    def execute_service(self, file_path: str) -> int:
        logger.info(f"Starting document ingestion for file: {file_path}")

        ingestor = DocumentIngestor(
            ingestor_config=self.app_config.document_ingestor_config,
        )
        num_chunks = ingestor.ingest(file_path)
        logger.info(f"Document ingestion completed for file: {file_path}. Number of chunks created: {num_chunks}")
        return num_chunks
    


    