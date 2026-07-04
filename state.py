from typing import TypedDict, Annotated, Any


class AgentState(TypedDict):
    # Input
    repo_url: str
    mode: str
    field_study_repos: list[str]
    pr_limit: int
    since_days: int
    workflow_limit: int

    # Fetched data
    workflows: list[dict]
    runs: list[dict]
    prs: list[dict]
    pr_runs: dict[str, list[dict]]

    # Analysis
    profiles: list[dict]
    bottlenecks: list[dict]
    optimizations: list[dict]
    simulated_total_saved_min: int

    # Human-in-the-loop
    selected_optimizations: list[str]
    human_approved: bool

    # Output
    rewritten_yaml: str
    rewritten_yaml_path: str
    pr_url: str | None
    report_path: str | None

    # Control
    validation_attempts: int
    token_usage: dict[str, int]
    errors: Annotated[list[str], lambda a, b: a + b]

    # Runtime
    llm_client: Any
    github_client: Any
