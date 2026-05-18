from __future__ import annotations

from graph.state import AgentState
from llm.chains import run_decision


async def run(state: AgentState) -> dict:
    vision = state.get("last_vision") or {}
    plan = state.get("action_plan", [])

    result = await run_decision(
        task=state["clarified_task"],
        current_step=state["current_step"],
        total_steps=len(plan),
        last_action=plan[state["current_step"]].get("description", "") if plan else "",
        observation=vision.get("observation", ""),
        success=vision.get("success", False),
        retry_count=state["retry_count"],
        max_retries=state["max_retries"],
    )

    decision = result.get("decision", "extract")
    new_step = state["current_step"]
    new_retry = state["retry_count"]

    if decision == "next_action":
        new_step = state["current_step"] + 1
        new_retry = 0
    elif decision == "retry":
        new_retry = state["retry_count"] + 1

    return {
        "last_decision": decision,
        "current_step": new_step,
        "retry_count": new_retry,
    }
