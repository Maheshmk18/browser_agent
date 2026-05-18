from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from api.controllers.agent_controller import AgentController
from api.schemas.agent import (
    AgentRunResponse,
    ErrorResponse,
    ResultResponse,
    RunAgentRequest,
    SessionResponse,
    TaskResponse,
    TaskStatusResponse,
)
from db.mongo.client import get_db

router = APIRouter()


def get_controller(db: AsyncIOMotorDatabase = Depends(get_db)) -> AgentController:
    return AgentController(db)


@router.post(
    "/run",
    response_model=AgentRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={500: {"model": ErrorResponse}},
)
async def run_agent(
    body: RunAgentRequest,
    controller: AgentController = Depends(get_controller),
):
    return await controller.run(body)


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_task(
    task_id: str,
    controller: AgentController = Depends(get_controller),
):
    task = await controller.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@router.get(
    "/tasks/{task_id}/status",
    response_model=TaskStatusResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_task_status(
    task_id: str,
    controller: AgentController = Depends(get_controller),
):
    task = await controller.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        updated_at=task.updated_at,
    )


@router.get(
    "/tasks",
    response_model=list[TaskResponse],
)
async def list_tasks(
    controller: AgentController = Depends(get_controller),
):
    return await controller.list_tasks()


@router.get(
    "/tasks/{task_id}/error",
    responses={404: {"model": ErrorResponse}},
)
async def get_task_error(
    task_id: str,
    controller: AgentController = Depends(get_controller),
):
    task = await controller.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    error = await controller.get_error(task_id)
    return {"task_id": task_id, "status": task.status, "error": error}


@router.get(
    "/tasks/{task_id}/result",
    response_model=ResultResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_task_result(
    task_id: str,
    controller: AgentController = Depends(get_controller),
):
    result = await controller.get_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No result found for task {task_id}")
    return result


@router.get(
    "/tasks/{task_id}/session",
    response_model=SessionResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_task_session(
    task_id: str,
    controller: AgentController = Depends(get_controller),
):
    session = await controller.get_session(task_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"No session found for task {task_id}")
    return session
