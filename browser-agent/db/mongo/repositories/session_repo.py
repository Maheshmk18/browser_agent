from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from config.settings import settings
from db.mongo.models import ActionPlanStep, SessionModel, SessionStatus, StepTaken


class SessionRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._col = db[settings.SESSIONS_COLLECTION]

    async def create(self, session: SessionModel) -> SessionModel:
        await self._col.insert_one(session.model_dump())
        return session

    async def get_by_id(self, session_id: str) -> Optional[SessionModel]:
        doc = await self._col.find_one({"session_id": session_id})
        return SessionModel(**doc) if doc else None

    async def get_by_task_id(self, task_id: str) -> Optional[SessionModel]:
        doc = await self._col.find_one({"task_id": task_id})
        return SessionModel(**doc) if doc else None

    async def list_by_task(self, task_id: str) -> List[SessionModel]:
        cursor = self._col.find({"task_id": task_id})
        return [SessionModel(**doc) async for doc in cursor]

    async def update_status(
        self,
        session_id: str,
        status: SessionStatus,
        error: Optional[str] = None,
    ) -> bool:
        update: dict = {
            "status": status.value,
            "ended_at": datetime.utcnow() if status != SessionStatus.RUNNING else None,
        }
        if error is not None:
            update["error"] = error
        result = await self._col.update_one(
            {"session_id": session_id},
            {"$set": update},
        )
        return result.modified_count == 1

    async def set_action_plan(
        self, session_id: str, plan: List[ActionPlanStep]
    ) -> bool:
        result = await self._col.update_one(
            {"session_id": session_id},
            {"$set": {"action_plan": [s.model_dump() for s in plan]}},
        )
        return result.modified_count == 1

    async def append_step(self, session_id: str, step: StepTaken) -> bool:
        result = await self._col.update_one(
            {"session_id": session_id},
            {
                "$push": {"steps_taken": step.model_dump()},
                "$set": {"current_step": step.step},
            },
        )
        return result.modified_count == 1

    async def increment_retry(self, session_id: str, step_index: int) -> bool:
        result = await self._col.update_one(
            {"session_id": session_id},
            {"$inc": {f"steps_taken.{step_index}.retry_count": 1}},
        )
        return result.modified_count == 1
