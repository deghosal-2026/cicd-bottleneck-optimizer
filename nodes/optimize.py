"""LangGraph nodes for optimization proposals and savings simulation."""

from lib.optimizer import propose, simulate


def propose_optimizations_node(state: dict, llm_client=None) -> dict:
    bottlenecks = state.get("bottlenecks", [])
    profiles = state.get("profiles", [])

    optimizations = propose(bottlenecks, profiles, llm_client=llm_client)

    if not optimizations:
        print("  No optimizations to propose.")

    return {"optimizations": optimizations, "errors": state.get("errors", [])}


def simulate_savings_node(state: dict) -> dict:
    optimizations = state.get("optimizations", [])

    simulated = simulate(optimizations)

    return {
        "simulated_total_saved_min": simulated,
        "errors": state.get("errors", []),
    }
