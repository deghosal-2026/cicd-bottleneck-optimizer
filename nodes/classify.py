"""LangGraph node for bottleneck classification."""

from lib.classifier import classify


def classify_bottlenecks_node(state: dict) -> dict:
    profiles = state.get("profiles", [])
    workflows = state.get("workflows", [])

    bottlenecks = classify(profiles, workflows)

    if not bottlenecks:
        print("  No bottlenecks found in job profiles.")

    return {
        "bottlenecks": bottlenecks,
        "errors": state.get("errors", []),
    }
