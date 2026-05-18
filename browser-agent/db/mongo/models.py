from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid

from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class StepStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class ResultStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"



# Nested sub-documents


class ActionPlanStep(BaseModel):
    step: int
    description: str


class StepTaken(BaseModel):
    step: int
    action: str
    status: StepStatus
    input: Optional[str] = None
    output: Optional[str] = None
    vision: Optional[str] = None
    screenshot: Optional[str] = None          
    retry_count: int = 0
    started_at: datetime
    completed_at: Optional[datetime] = None


class MetricsModel(BaseModel):
    total_steps: int = 0
    retries: int = 0
    duration_ms: int = 0





class TaskModel(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    input: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class SessionModel(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    action_plan: List[ActionPlanStep] = Field(default_factory=list)
    steps_taken: List[StepTaken] = Field(default_factory=list)
    current_step: int = 0
    max_retries: int = 3
    status: SessionStatus = SessionStatus.RUNNING
    error: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class ResultModel(BaseModel):
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    session_id: str
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    metrics: MetricsModel = Field(default_factory=MetricsModel)
    score: int = Field(default=5, ge=1, le=10)
    status: ResultStatus
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
