from __future__ import annotations

from dataclasses import dataclass

from langgraph.graph import END, StateGraph

from browser.actions import BrowserActions
from browser.screenshot import ScreenshotCapture
from db.mongo.repositories.result_repo import ResultRepository
from db.mongo.repositories.session_repo import SessionRepository
from graph.nodes import supervisor, decision, vision
from graph.nodes.browser_action import make_browser_action_node
from graph.nodes.planner import make_planner_node
from graph.nodes.extractor import make_extractor_node
from graph.nodes.reflector import make_reflector_node
from graph.state import AgentState


@dataclass
class GraphContext:
    actions: BrowserActions
    screenshots: ScreenshotCapture
    session_repo: SessionRepository
    result_repo: ResultRepository


def _route_decision(state: AgentState) -> str:
    decision_val = state.get("last_decision", "extract")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)
    current_step = state.get("current_step", 0)
    total_steps = len(state.get("action_plan", []))

    if decision_val == "extract" or current_step >= total_steps:
        return "extractor"
    if decision_val == "retry" and retry_count >= max_retries:
        return "extractor"
    return "browser_action"


def build_graph(ctx: GraphContext):
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("supervisor", supervisor.run)
    workflow.add_node("planner", make_planner_node(ctx.session_repo))
    workflow.add_node("browser_action", make_browser_action_node(ctx.actions, ctx.screenshots, ctx.session_repo))
    workflow.add_node("vision", vision.run)
    workflow.add_node("decision", decision.run)
    workflow.add_node("extractor", make_extractor_node(ctx.actions))
    workflow.add_node("reflector", make_reflector_node(ctx.session_repo, ctx.result_repo))

    # Linear edges
    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "planner")
    workflow.add_edge("planner", "browser_action")
    workflow.add_edge("browser_action", "vision")
    workflow.add_edge("vision", "decision")

    # Conditional routing from decision node
    workflow.add_conditional_edges(
        "decision",
        _route_decision,
        {
            "browser_action": "browser_action",
            "extractor": "extractor",
        },
    )

    workflow.add_edge("extractor", "reflector")
    workflow.add_edge("reflector", END)

    return workflow.compile()
