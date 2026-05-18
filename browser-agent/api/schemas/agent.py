from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from db.mongo.models import (
    ActionPlanStep,
    MetricsModel,
    ResultStatus,
    SessionStatus,
    StepTaken,
    TaskStatus,
)



# Request schemas

class RunAgentRequest(BaseModel):
    input: str = Field(..., min_length=1, description="Natural language task for the agent")



# Response schemas

class TaskResponse(BaseModel):
    task_id: str
    input: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime


class SessionResponse(BaseModel):
    session_id: str
    task_id: str
    action_plan: List[ActionPlanStep]
    steps_taken: List[StepTaken]
    current_step: int
    max_retries: int
    status: SessionStatus
    error: Optional[str]
    started_at: datetime
    ended_at: Optional[datetime]


class ResultResponse(BaseModel):
    result_id: str
    task_id: str
    session_id: str
    extracted_data: Dict[str, Any]
    metrics: MetricsModel
    score: int = Field(..., ge=1, le=10)
    status: ResultStatus
    error: Optional[str]
    created_at: datetime


class AgentRunResponse(BaseModel):
    task: TaskResponse
    session: Optional[SessionResponse] = None
    result: Optional[ResultResponse] = None
    message: str



# Status / utility responses

class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    updated_at: datetime


class ErrorResponse(BaseModel):
    detail: str
