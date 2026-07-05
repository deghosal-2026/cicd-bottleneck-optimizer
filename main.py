import argparse
import uuid
import sys
import config
from graph import build_graph
from state import AgentState


def parse_args():
    parser = argparse.ArgumentParser(
        description="CI/CD Bottleneck Optimizer — profile, classify, and optimize GitHub Actions workflows.",
    )

    parser.add_argument(
        "--repo",
        type=str,
        help="Target repository in owner/repo format",
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--optimize",
        action="store_true",
        default=True,
        help="Full optimize mode: fetch, profile, classify, propose, interrupt, generate YAML, open PR (default)",
    )
    mode_group.add_argument(
        "--audit",
        action="store_true",
        help="Read-only audit: fetch, profile, classify, print report to CLI",
    )
    mode_group.add_argument(
        "--field-study",
        action="store_true",
        help="Field study mode: analyze PRs across multiple repos, save local reports",
    )

    parser.add_argument(
        "--repos",
        type=str,
        help="Comma-separated list of repos for field study mode",
    )
    parser.add_argument(
        "--pr-limit",
        type=int,
        default=10,
        help="Number of PRs to fetch per repo in field study mode (default: 10)",
    )
    parser.add_argument(
        "--since",
        type=int,
        default=30,
        help="Only consider PRs updated within this many days (default: 30)",
    )
    parser.add_argument(
        "--review",
        action="store_true",
        help="In field study mode, show trade-off table interactively before saving reports",
    )
    parser.add_argument(
        "--workflow-limit",
        type=int,
        default=5,
        help="Maximum number of workflows to analyze (default: 5)",
    )
    parser.add_argument(
        "--resume",
        type=str,
        metavar="THREAD_ID",
        help="Resume an interrupted analysis session from checkpoint",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if not args.repo and not args.field_study:
        print("Error: --repo is required unless using --field-study or --audit")
        print("Usage: python main.py --repo owner/repo [--optimize|--audit]")
        print("       python main.py --field-study --repos owner1/repo1,owner2/repo2")
        return 1

    c = config.load_config()
    mode = "field_study" if args.field_study else "audit" if args.audit else "optimize"
    config.check_omlx_reachable(c)
    config.check_act_installed()
    config.check_token_scope(c, mode)

    print("CI/CD Bottleneck Optimizer")
    print(f"  Mode: {mode}")

    if args.field_study:
        print(f"  Repos: {args.repos}")
        print(f"  PR limit: {args.pr_limit}")
        print(f"  Since: {args.since} days")
        if args.review:
            print("  Review: enabled")
    else:
        print(f"  Repo: {args.repo}")
        print(f"  Workflow limit: {args.workflow_limit}")

    repos = args.repos.split(",") if args.repos else []
    thread_id = args.resume or str(uuid.uuid4())

    if args.resume:
        print(f"  Resuming session: {thread_id}")

    print()

    initial_state: AgentState = {
        "repo_url": args.repo or "",
        "mode": mode,
        "field_study_repos": repos,
        "pr_limit": args.pr_limit,
        "since_days": args.since,
        "workflow_limit": args.workflow_limit,
        "workflows": [],
        "runs": [],
        "prs": [],
        "pr_runs": {},
        "profiles": [],
        "bottlenecks": [],
        "optimizations": [],
        "simulated_total_saved_min": 0,
        "selected_optimizations": [],
        "human_approved": False,
        "rewritten_yaml": "",
        "rewritten_yaml_path": "",
        "pr_url": None,
        "report_path": None,
        "validation_attempts": 0,
        "token_usage": {},
        "errors": [],
        "llm_client": None,
        "github_client": None,
    }

    graph = build_graph()
    thread_config = {"configurable": {"thread_id": thread_id}}

    if args.resume:
        print("Resuming from checkpoint...")
        snapshot = graph.get_state(thread_config)  # type: ignore[arg-type]
        if not snapshot.values:
            print(f"Error: No checkpoint found for session {thread_id}", file=sys.stderr)
            return 1
        print(f"  Resumed at node: {snapshot.next[0] if snapshot.next else 'end'}")
        result = graph.invoke(None, thread_config)  # type: ignore[arg-type]
    else:
        result = graph.invoke(initial_state, thread_config)  # type: ignore[arg-type]

    print()

    if result.get("pr_url"):
        print(f"PR opened: {result['pr_url']}")
    if result.get("rewritten_yaml_path"):
        print(f"YAML saved: {result['rewritten_yaml_path']}")
    if result.get("prs"):
        print(f"PRs analyzed: {len(result['prs'])}")
    if result.get("errors"):
        errors = result["errors"]
        print(f"Errors ({len(errors)}):")
        for e in errors[-10:]:
            print(f"  - {e}")

    print(f"\nSession ID: {thread_id}")
    print("Done.")
    return 0


if __name__ == "__main__":
    exit(main())
