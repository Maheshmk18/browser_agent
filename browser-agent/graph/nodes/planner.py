from __future__ import annotations

from typing import Callable

from db.mongo.models import ActionPlanStep
from db.mongo.repositories.session_repo import SessionRepository
from graph.state import AgentState
from llm.chains import run_planner


def make_planner_node(session_repo: SessionRepository) -> Callable:

    async def run(state: AgentState) -> dict:
        steps = await run_planner(state["clarified_task"])

        plan_docs = [
            ActionPlanStep(step=i, description=s.get("description", str(s)))
            for i, s in enumerate(steps)
        ]
        await session_repo.set_action_plan(state["session_id"], plan_docs)

        return {"action_plan": steps, "current_step": 0, "retry_count": 0}

    return run
