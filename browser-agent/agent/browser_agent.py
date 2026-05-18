from __future__ import annotations

import asyncio
import time
import traceback

from motor.motor_asyncio import AsyncIOMotorClient

from browser.actions import BrowserActions
from browser.engine import BrowserEngine
from browser.screenshot import ScreenshotCapture
from config.settings import settings
from db.mongo.models import SessionStatus, TaskStatus
from db.mongo.repositories.result_repo import ResultRepository
from db.mongo.repositories.session_repo import SessionRepository
from db.mongo.repositories.task_repo import TaskRepository
from graph.builder import GraphContext, build_graph
from db.mongo.models import SessionModel, TaskModel


async def run_agent(task: TaskModel, session: SessionModel) -> None:
    """
    Full agent execution pipeline.
    Runs inside a dedicated ProactorEventLoop thread (called from agent_controller).
    Creates its own Motor client bound to this thread's event loop.
    """
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]

    t_repo = TaskRepository(db)
    s_repo = SessionRepository(db)
    r_repo = ResultRepository(db)

    try:
        print(f"[AGENT] Browser starting for task {task.task_id}", flush=True)
        async with BrowserEngine() as engine:
            print(f"[AGENT] Browser ready", flush=True)
            actions = BrowserActions(engine.page)
            screenshots = ScreenshotCapture(engine.page)

            ctx = GraphContext(
                actions=actions,
                screenshots=screenshots,
                session_repo=s_repo,
                result_repo=r_repo,
            )
            graph = build_graph(ctx)

            initial_state = {
                "task": task.input,
                "task_id": task.task_id,
                "session_id": session.session_id,
                "clarified_task": "",
                "action_plan": [],
                "current_step": 0,
                "retry_count": 0,
                "max_retries": session.max_retries,
                "steps_taken": [],
                "last_screenshot": None,
                "last_vision": None,
                "last_decision": None,
                "extracted_data": None,
                "reflection": None,
                "status": "running",
                "error": None,
                "start_time": time.time(),
            }

            await graph.ainvoke(initial_state)
            await t_repo.update_status(task.task_id, TaskStatus.COMPLETED)
            print(f"[AGENT] Task {task.task_id} completed", flush=True)

            if settings.BROWSER_KEEP_OPEN_SECONDS > 0:
                print(f"[AGENT] Browser staying open for {settings.BROWSER_KEEP_OPEN_SECONDS}s", flush=True)
                await asyncio.sleep(settings.BROWSER_KEEP_OPEN_SECONDS)

    except Exception:
        error_detail = traceback.format_exc()
        print(f"[AGENT ERROR] task={task.task_id}\n{error_detail}", flush=True)
        await t_repo.update_status(task.task_id, TaskStatus.FAILED)
        await s_repo.update_status(session.session_id, SessionStatus.FAILED, error=error_detail)
    finally:
        client.close()
