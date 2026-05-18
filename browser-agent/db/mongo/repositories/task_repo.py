from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from config.settings import settings
from db.mongo.models import TaskModel, TaskStatus


class TaskRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._col = db[settings.TASKS_COLLECTION]

    async def create(self, task: TaskModel) -> TaskModel:
        await self._col.insert_one(task.model_dump())
        return task

    async def get_by_id(self, task_id: str) -> Optional[TaskModel]:
        doc = await self._col.find_one({"task_id": task_id})
        return TaskModel(**doc) if doc else None

    async def list_all(self) -> List[TaskModel]:
        cursor = self._col.find()
        return [TaskModel(**doc) async for doc in cursor]

    async def update_status(self, task_id: str, status: TaskStatus) -> bool:
        result = await self._col.update_one(
            {"task_id": task_id},
            {"$set": {"status": status.value, "updated_at": datetime.utcnow()}},
        )
        return result.modified_count == 1

    async def delete(self, task_id: str) -> bool:
        result = await self._col.delete_one({"task_id": task_id})
        return result.deleted_count == 1
