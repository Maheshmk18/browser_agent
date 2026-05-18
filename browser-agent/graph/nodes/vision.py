from __future__ import annotations

from graph.state import AgentState
from llm.chains import run_vision


async def run(state: AgentState) -> dict:
    plan = state.get("action_plan", [])
    idx = state.get("current_step", 0)
    screenshot = state.get("last_screenshot", "")

    if not screenshot:
        return {"last_vision": {"observation": "No screenshot available", "success": False, "next_hint": None}}

    step = plan[idx] if idx < len(plan) else {}
    action = step.get("description", "unknown action")
    expected = step.get("description", "")

    vision_result = await run_vision(
        action=action,
        expected=expected,
        screenshot_b64=screenshot,
    )

    # Also store vision text in the latest step_taken
    steps_taken = list(state.get("steps_taken", []))
    if steps_taken:
        steps_taken[-1]["vision"] = vision_result.get("observation", "")

    return {
        "last_vision": vision_result,
        "steps_taken": steps_taken,
    }
