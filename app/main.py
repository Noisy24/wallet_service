import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.logging_config import configure_logging
from app.routers import health, wallets


configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("wallet-service started")
    yield


app = FastAPI(title="wallet-service", lifespan=lifespan)
app.include_router(health.router)
app.include_router(wallets.router)
