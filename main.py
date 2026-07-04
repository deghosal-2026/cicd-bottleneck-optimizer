import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="CI/CD Bottleneck Optimizer — profile, classify, and optimize GitHub Actions workflows.",
    )

    # Target
    parser.add_argument(
        "--repo",
        type=str,
        help="Target repository in owner/repo format",
    )

    # Modes (mutually exclusive group)
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

    # Field study options
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

    # Workflow limit
    parser.add_argument(
        "--workflow-limit",
        type=int,
        default=5,
        help="Maximum number of workflows to analyze (default: 5)",
    )

    # Resume
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

    print(f"CI/CD Bottleneck Optimizer")
    print(f"  Mode: {'field-study' if args.field_study else 'audit' if args.audit else 'optimize'}")

    if args.field_study:
        print(f"  Repos: {args.repos}")
        print(f"  PR limit: {args.pr_limit}")
        print(f"  Since: {args.since} days")
        if args.review:
            print(f"  Review: enabled")
    else:
        print(f"  Repo: {args.repo}")
        print(f"  Workflow limit: {args.workflow_limit}")

    if args.resume:
        print(f"  Resuming session: {args.resume}")

    print()
    print("Starting analysis...")

    # TODO: Load config
    # TODO: Run LangGraph agent

    return 0


if __name__ == "__main__":
    exit(main())
