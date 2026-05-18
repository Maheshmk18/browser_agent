from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Callable

from browser.actions import BrowserActions
from browser.screenshot import ScreenshotCapture
from db.mongo.models import StepStatus, StepTaken
from db.mongo.repositories.session_repo import SessionRepository
from graph.state import AgentState


def make_browser_action_node(
    actions: BrowserActions,
    screenshots: ScreenshotCapture,
    session_repo: SessionRepository,
) -> Callable:

    async def run(state: AgentState) -> dict:
        plan = state["action_plan"]
        idx = state["current_step"]

        if idx >= len(plan):
            return {"last_decision": "extract"}

        step = plan[idx]
        action = step.get("action", "")
        target = step.get("target") or ""
        value = step.get("value") or ""
        started_at = datetime.utcnow()
        output = ""
        success = True

        try:
            if action == "navigate":
                output = await actions.navigate(target)
            elif action == "click":
                await actions.click(target)
                output = f"Clicked: {target}"
            elif action == "type":
                await actions.type_text(target, value)
                output = f"Typed '{value}' into {target}"
            elif action == "press_key":
                await actions.press_key(target)
                output = f"Pressed: {target}"
            elif action == "scroll":
                await actions.scroll(target or "down")
                output = "Scrolled"
            elif action == "wait":
                await asyncio.sleep(1)
                output = "Waited 1s"
            elif action == "extract":
                output = "Extraction step reached"
            else:
                output = f"Unknown action: {action}"

        except Exception as exc:
            success = False
            output = str(exc)

        screenshot_b64 = await screenshots.capture_base64()
        completed_at = datetime.utcnow()

        step_taken = StepTaken(
            step=idx,
            action=action,
            status=StepStatus.SUCCESS if success else StepStatus.FAILED,
            input=f"{target} | {value}".strip(" |") or None,
            output=output,
            screenshot=screenshot_b64,
            retry_count=state["retry_count"],
            started_at=started_at,
            completed_at=completed_at,
        )
        await session_repo.append_step(state["session_id"], step_taken)

        step_record = {
            "step": idx,
            "action": action,
            "status": "success" if success else "failed",
            "input": f"{target} | {value}".strip(" |"),
            "output": output,
            "screenshot": screenshot_b64,
            "retry_count": state["retry_count"],
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
        }

        steps_taken = list(state.get("steps_taken", []))
        steps_taken.append(step_record)

        return {
            "last_screenshot": screenshot_b64,
            "steps_taken": steps_taken,
        }

    return run
