from __future__ import annotations

from graph.state import AgentState
from llm.chains import build_supervisor_chain


async def run(state: AgentState) -> dict:
    chain = build_supervisor_chain()
    clarified = await chain.ainvoke({"input": state["task"]})
    return {"clarified_task": clarified.strip()}
