from __future__ import annotations

import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.mongo.client import MongoClient
from api.routers import agent as agent_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    MongoClient.connect()
    yield
    MongoClient.disconnect()


app = FastAPI(
    title="Browser Agent API",
    description="LangGraph powered browser automation agent",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router.router, prefix="/agent", tags=["agent"])


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
