from __future__ import annotations

import json
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from llm.client import get_llm, get_vision_llm
from llm.prompts import (
    DECISION_PROMPT,
    EXTRACTOR_PROMPT,
    PLANNER_PROMPT,
    REFLECTOR_PROMPT,
    SUPERVISOR_PROMPT,
    VISION_PROMPT,
)


def _json_parser(raw: str) -> Any:
    text = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)



# Supervisor chain  →  str


def build_supervisor_chain() -> Runnable:
    return SUPERVISOR_PROMPT | get_llm() | StrOutputParser()



# Planner chain  →  list[dict]

def build_planner_chain() -> Runnable:
    return PLANNER_PROMPT | get_llm() | StrOutputParser()


async def run_planner(task: str) -> list[dict]:
    chain = build_planner_chain()
    raw = await chain.ainvoke({"task": task})
    return _json_parser(raw)



# Vision chain  →  dict {observation, success, next_hint}

def build_vision_chain() -> Runnable:
    return VISION_PROMPT | get_vision_llm() | StrOutputParser()


async def run_vision(action: str, expected: str, screenshot_b64: str) -> dict:
    from langchain_core.messages import HumanMessage
    llm = get_vision_llm()
    messages = VISION_PROMPT.format_messages(action=action, expected=expected)
    # Append the image to the last human message
    last = messages[-1]
    messages[-1] = HumanMessage(content=[
        {"type": "text", "text": last.content},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}},
    ])
    raw = await llm.ainvoke(messages)
    return _json_parser(raw.content)



# Decision chain  →  dict {decision, reason}


def build_decision_chain() -> Runnable:
    return DECISION_PROMPT | get_llm() | StrOutputParser()


async def run_decision(
    task: str,
    current_step: int,
    total_steps: int,
    last_action: str,
    observation: str,
    success: bool,
    retry_count: int,
    max_retries: int,
) -> dict:
    chain = build_decision_chain()
    raw = await chain.ainvoke({
        "task": task,
        "current_step": current_step,
        "total_steps": total_steps,
        "last_action": last_action,
        "observation": observation,
        "success": success,
        "retry_count": retry_count,
        "max_retries": max_retries,
    })
    return _json_parser(raw)



# Extractor chain  →  dict (raw extracted data)


def build_extractor_chain() -> Runnable:
    return EXTRACTOR_PROMPT | get_llm() | StrOutputParser()


async def run_extractor(task: str, page_content: str) -> dict:
    chain = build_extractor_chain()
    raw = await chain.ainvoke({"task": task, "page_content": page_content[:8000]})
    return _json_parser(raw)


# Reflector chain  →  dict {score, reason, improvements}


def build_reflector_chain() -> Runnable:
    return REFLECTOR_PROMPT | get_llm() | StrOutputParser()


async def run_reflector(
    task: str,
    extracted_data: dict,
    total_steps: int,
    retries: int,
) -> dict:
    chain = build_reflector_chain()
    raw = await chain.ainvoke({
        "task": task,
        "extracted_data": json.dumps(extracted_data, indent=2),
        "total_steps": total_steps,
        "retries": retries,
    })
    return _json_parser(raw)
