from __future__ import annotations

from datetime import datetime
from typing import Callable

from db.mongo.models import MetricsModel, ResultModel, ResultStatus
from db.mongo.repositories.result_repo import ResultRepository
from db.mongo.repositories.session_repo import SessionRepository
from db.mongo.models import SessionStatus
from graph.state import AgentState
from llm.chains import run_reflector


def make_reflector_node(
    session_repo: SessionRepository,
    result_repo: ResultRepository,
) -> Callable:

    async def run(state: AgentState) -> dict:
        steps_taken = state.get("steps_taken", [])
        total_retries = sum(s.get("retry_count", 0) for s in steps_taken)
        extracted = state.get("extracted_data") or {}

        reflection = await run_reflector(
            task=state["clarified_task"],
            extracted_data=extracted,
            total_steps=len(steps_taken),
            retries=total_retries,
        )

        duration_ms = int(
            (datetime.utcnow().timestamp() - state["start_time"]) * 1000
        )

        result = ResultModel(
            task_id=state["task_id"],
            session_id=state["session_id"],
            extracted_data=extracted,
            metrics=MetricsModel(
                total_steps=len(steps_taken),
                retries=total_retries,
                duration_ms=duration_ms,
            ),
            score=reflection.get("score", 5),
            status=ResultStatus.COMPLETED,
        )
        await result_repo.create(result)

        await session_repo.update_status(
            state["session_id"], SessionStatus.COMPLETED
        )

        return {
            "reflection": reflection,
            "status": "completed",
        }

    return run
