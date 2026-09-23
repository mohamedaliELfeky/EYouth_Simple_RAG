import os
import logging
from typing import Any
logger = logging.getLogger(__name__)

from configuration.entities import ChromaRetrieverConfig

import chromadb

class ChromaRetriever:
    def __init__(self, 
                retriever_config: ChromaRetrieverConfig,
                embedding_function:  Any| None = None
            ):
        
        self.retriever_config = retriever_config
        self.client = chromadb.PersistentClient(path=retriever_config.chroma_retriever_persist_dir)
        kwargs = {"embedding_function": embedding_function} if embedding_function else {}
        try:
            self.collection = self.client.get_collection(
                name=retriever_config.chroma_retriever_collection_name,
                metadata={"hnsw:space": "cosine"},
                **kwargs,
            )
        except Exception as e:
            logger.error(f"Collection '{retriever_config.chroma_retriever_collection_name}' not found. Creating a new collection.")
            raise ValueError(f"Collection '{retriever_config.chroma_retriever_collection_name}' not found. Please create the collection before using the retriever.") from e    
        

    def retrieve(self, query: str):
        if self.collection.count() == 0:
            raise ValueError("The collection is empty. Please add documents before retrieving.")


        results = self.collection.query(
                    query_texts=[query],
                    n_results=self.retriever_config.chroma_retriever_top_k,
                    include=["metadatas", "distances"]
                )

        return results