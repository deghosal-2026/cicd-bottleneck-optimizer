"""LangGraph nodes for human-in-the-loop and PR operations."""

from lib.cli import trade_off_table, prompt_re_analyze_or_recompute, summary_table


def interrupt_node(state: dict) -> dict:
    optimizations = state.get("optimizations", [])
    bottlenecks = state.get("bottlenecks", [])

    selected_ids, approved = trade_off_table(optimizations, bottlenecks)

    return {
        "selected_optimizations": selected_ids,
        "human_approved": approved,
        "errors": state.get("errors", []),
    }
