import os
from typing import List, Optional
from logging import getLogger
logger = getLogger(__name__)


from configuration.app_config import AppConfig
from src.retrievers.chroma_retriever import ChromaRetriever
from src.agents.q_a_research_agent import RAGAgent


class RAGService:
    def __init__(self, rag_config: AppConfig, prompt: str = None):
        
        self.rag_config = rag_config
        self.prompt = prompt 

        self.rag_agent = RAGAgent()
        self.chroma_retriever = ChromaRetriever(
            retriever_config=self.rag_config.chroma_retriever_config
        )

    def execute_service(self, query: str) -> List[str]:
        logger.info(f"Starting RAG service for query: {query}")

        retrieved_docs = self.chroma_retriever.retrieve(query)

        generated_response = self.rag_agent(retrieved_docs)

        logger.info(f"RAG service completed for query: {query}. Generated response: {generated_response}")
        return generated_response

   