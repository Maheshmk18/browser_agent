from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict


class AgentState(TypedDict):
    #  Input 
    task: str
    task_id: str
    session_id: str

    # Supervisor 
    clarified_task: str

    #  Planner 
    action_plan: list[dict]

    # Execution state 
    current_step: int
    retry_count: int
    max_retries: int
    steps_taken: list[dict]

    # Vision 
    last_screenshot: Optional[str]      # base64 PNG
    last_vision: Optional[dict]         # {observation, success, next_hint}

    #  Decision 
    last_decision: Optional[str]        # "next_action" | "retry" | "extract"

    #  Output
    extracted_data: Optional[dict]
    reflection: Optional[dict]          # {score, reason, improvements}

    #  Meta 
    status: str                         # running / completed / failed
    error: Optional[str]
    start_time: float
