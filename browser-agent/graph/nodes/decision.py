from __future__ import annotations

from graph.state import AgentState


async def run(state: AgentState) -> dict:
    plan = state.get("action_plan", [])
    current_step = state.get("current_step", 0)
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)
    vision = state.get("last_vision") or {}
    success = vision.get("success", True)
    total_steps = len(plan)

    # Completed all steps → extract
    if current_step >= total_steps - 1:
        return {"last_decision": "extract", "current_step": current_step, "retry_count": retry_count}

    # Last step failed and retries left → retry
    if not success and retry_count < max_retries:
        return {"last_decision": "retry", "current_step": current_step, "retry_count": retry_count + 1}

    # Last step failed and no retries left → extract anyway
    if not success and retry_count >= max_retries:
        return {"last_decision": "extract", "current_step": current_step, "retry_count": retry_count}

    # Last step succeeded → move to next step
    return {"last_decision": "next_action", "current_step": current_step + 1, "retry_count": 0}
