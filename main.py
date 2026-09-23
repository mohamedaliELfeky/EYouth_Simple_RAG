import logging

from fastapi import FastAPI
from configuration.app_config import AppConfig

logger = logging.getLogger(__name__)

from src.endpoints.routes.retriever_route import retriever_route

config = AppConfig()
app = FastAPI()

app.include_router(retriever_route, tags=["Retriever"])



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting FastAPI application...")

    