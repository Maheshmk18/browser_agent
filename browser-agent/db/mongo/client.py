from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config.settings import settings


class MongoClient:
    _client: AsyncIOMotorClient | None = None
    _db: AsyncIOMotorDatabase | None = None

    @classmethod
    def connect(cls) -> None:
        cls._client = AsyncIOMotorClient(
            settings.MONGO_URI,
            serverSelectionTimeoutMS=5000,
        )
        cls._db = cls._client[settings.MONGO_DB_NAME]

    @classmethod
    def disconnect(cls) -> None:
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._db = None

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        if cls._db is None:
            raise RuntimeError("MongoDB is not connected. Call MongoClient.connect() first.")
        return cls._db


def get_db() -> AsyncIOMotorDatabase:
    return MongoClient.get_db()
