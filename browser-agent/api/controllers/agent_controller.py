from __future__ import annotations

import asyncio
import concurrent.futures
import sys
import traceback
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from agent.browser_agent import run_agent 
from api.schemas.agent import AgentRunResponse, RunAgentRequest, TaskResponse
from config.settings import settings
from db.mongo.models import SessionModel, SessionStatus, TaskModel, TaskStatus
from db.mongo.repositories.result_repo import ResultRepository
from db.mongo.repositories.session_repo import SessionRepository
from db.mongo.repositories.task_repo import TaskRepository

# Strong references — prevent GC from killing background tasks mid-run
_background_tasks: set[asyncio.Task] = set()


class AgentController:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._tasks = TaskRepository(db)
        self._sessions = SessionRepository(db)
        self._results = ResultRepository(db)

    async def run(self, body: RunAgentRequest) -> AgentRunResponse:
        task = TaskModel(input=body.input)
        await self._tasks.create(task)
        await self._tasks.update_status(task.task_id, TaskStatus.RUNNING)

        session = SessionModel(task_id=task.task_id, max_retries=settings.MAX_RETRIES)
        await self._sessions.create(session)

        bg_task = asyncio.create_task(self._execute(task, session))
        _background_tasks.add(bg_task)
        bg_task.add_done_callback(_background_tasks.discard)

        return AgentRunResponse(
            task=TaskResponse(
                task_id=task.task_id,
                input=task.input,
                status=TaskStatus.RUNNING,
                created_at=task.created_at,
                updated_at=task.updated_at,
            ),
            message="Agent started. Poll /agent/tasks/{task_id}/status for updates.",
        )

    async def _execute(self, task: TaskModel, session: SessionModel) -> None:
        """
        Runs the agent in a dedicated thread with its own ProactorEventLoop.
        Playwright needs ProactorEventLoop on Windows to spawn the browser process.
        """
        try:
            loop = asyncio.get_running_loop()

            def run_in_thread() -> None:
                if sys.platform == "win32":
                    thread_loop = asyncio.ProactorEventLoop()
                else:
                    thread_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(thread_loop)
                try:
                    thread_loop.run_until_complete(run_agent(task, session))
                finally:
                    thread_loop.close()

            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            await loop.run_in_executor(executor, run_in_thread)
            executor.shutdown(wait=False)

        except Exception:
            error_detail = traceback.format_exc()
            print(f"[AGENT ERROR] task={task.task_id}\n{error_detail}", flush=True)
            await self._tasks.update_status(task.task_id, TaskStatus.FAILED)
            await self._sessions.update_status(
                session.session_id, SessionStatus.FAILED, error=error_detail
            )

    async def get_task(self, task_id: str) -> Optional[TaskModel]:
        return await self._tasks.get_by_id(task_id)

    async def list_tasks(self) -> List[TaskModel]:
        return await self._tasks.list_all()

    async def get_error(self, task_id: str) -> Optional[str]:
        session = await self._sessions.get_by_task_id(task_id)
        return session.error if session else None

    async def get_result(self, task_id: str):
        return await self._results.get_by_task_id(task_id)

    async def get_session(self, task_id: str):
        return await self._sessions.get_by_task_id(task_id)
