import os

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from state import AgentState
from nodes.fetch import fetch_workflows_node, fetch_runs_node, fetch_prs_node, fetch_pr_runs_node
from nodes.profile import profile_jobs_node
from nodes.classify import classify_bottlenecks_node
from nodes.optimize import propose_optimizations_node, simulate_savings_node
from nodes.pr import interrupt_node, open_pr_node
from nodes.generate import generate_yaml_node, validate_syntax_node
from llm.client import LLMClient
from tools.github import GitHubClient
import config as cfg

CHECKPOINT_DB = os.environ.get("CICD_CHECKPOINT_DB", "checkpoints/checkpoints.db")


def route_by_mode(state: AgentState) -> str:
    mode = state.get("mode", "optimize")
    if mode == "field_study":
        return "fetch_prs"
    return "fetch_workflows"


def build_graph(config_path: str | None = None):
    c = cfg.load_config(config_path)
    token = c["github"]["token"]
    gh_client = GitHubClient(token)

    llm_cfg = c.get("llm", {})
    llm_client = LLMClient(c) if llm_cfg and llm_cfg.get("local") else None

    graph = StateGraph(AgentState)

    def with_gh(fn):
        def wrapper(state):
            return fn(state, gh_client)
        return wrapper

    def with_llm(fn):
        def wrapper(state):
            return fn(state, llm_client)
        return wrapper

    graph.add_node("fetch_workflows", with_gh(fetch_workflows_node))
    graph.add_node("fetch_runs", with_gh(fetch_runs_node))
    graph.add_node("fetch_prs", with_gh(fetch_prs_node))
    graph.add_node("fetch_pr_runs", with_gh(fetch_pr_runs_node))
    graph.add_node("profile_jobs", profile_jobs_node)
    graph.add_node("classify_bottlenecks", with_llm(classify_bottlenecks_node))
    graph.add_node("propose_optimizations", with_llm(propose_optimizations_node))
    graph.add_node("simulate_savings", simulate_savings_node)
    graph.add_node("interrupt_for_approval", interrupt_node)
    graph.add_node("generate_yaml", generate_yaml_node)
    graph.add_node("validate_syntax", validate_syntax_node)
    graph.add_node("open_pr", with_gh(open_pr_node))

    graph.set_conditional_entry_point(route_by_mode, {
        "fetch_workflows": "fetch_workflows",
        "fetch_prs": "fetch_prs",
    })

    graph.add_edge("fetch_workflows", "fetch_runs")
    graph.add_edge("fetch_runs", "profile_jobs")
    graph.add_edge("fetch_prs", "fetch_pr_runs")
    graph.add_edge("fetch_pr_runs", "profile_jobs")
    graph.add_edge("profile_jobs", "classify_bottlenecks")
    graph.add_edge("classify_bottlenecks", "propose_optimizations")
    graph.add_edge("propose_optimizations", "simulate_savings")
    graph.add_edge("simulate_savings", "interrupt_for_approval")

    graph.add_conditional_edges("interrupt_for_approval", lambda s: "generate_yaml" if s.get("human_approved") else "propose_optimizations", {
        "generate_yaml": "generate_yaml",
        "propose_optimizations": "propose_optimizations",
    })

    graph.add_edge("generate_yaml", "validate_syntax")

    graph.add_conditional_edges("validate_syntax", lambda s: "open_pr" if s.get("validation_attempts", 0) < 3 else END, {
        "open_pr": "open_pr",
        END: END,
    })

    graph.add_edge("open_pr", END)

    import sqlite3

    os.makedirs(os.path.dirname(CHECKPOINT_DB), exist_ok=True)
    conn = sqlite3.connect(CHECKPOINT_DB, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    checkpointer.setup()

    return graph.compile(checkpointer=checkpointer)
