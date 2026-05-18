from __future__ import annotations

from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from config.settings import settings
from db.mongo.models import ResultModel


class ResultRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._col = db[settings.RESULTS_COLLECTION]

    async def create(self, result: ResultModel) -> ResultModel:
        await self._col.insert_one(result.model_dump())
        return result

    async def get_by_id(self, result_id: str) -> Optional[ResultModel]:
        doc = await self._col.find_one({"result_id": result_id})
        return ResultModel(**doc) if doc else None

    async def get_by_task_id(self, task_id: str) -> Optional[ResultModel]:
        doc = await self._col.find_one({"task_id": task_id})
        return ResultModel(**doc) if doc else None

    async def get_by_session_id(self, session_id: str) -> Optional[ResultModel]:
        doc = await self._col.find_one({"session_id": session_id})
        return ResultModel(**doc) if doc else None

    async def list_by_status(self, status: str) -> List[ResultModel]:
        cursor = self._col.find({"status": status})
        return [ResultModel(**doc) async for doc in cursor]

    async def list_by_score(self, min_score: int = 1, max_score: int = 10) -> List[ResultModel]:
        cursor = self._col.find({"score": {"$gte": min_score, "$lte": max_score}})
        return [ResultModel(**doc) async for doc in cursor]

    async def delete(self, result_id: str) -> bool:
        result = await self._col.delete_one({"result_id": result_id})
        return result.deleted_count == 1
