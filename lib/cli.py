"""CLI interaction for human-in-the-loop: trade-off table, evidence view, selection."""


def trade_off_table(optimizations: list[dict], bottlenecks: list[dict]) -> tuple[list[str], bool]:
    """Interactive CLI: display trade-offs, let user view evidence and select optimizations.

    Returns (selected_ids, approved).
    """
    if not optimizations:
        print("No optimizations to review.")
        return [], False

    bottleneck_map = {b["job_name"]: b for b in bottlenecks}

    while True:
        _print_table(optimizations, bottleneck_map)

        print()
        choice = input("Enter # to view evidence, 's' to select, 'a' for all, 'q' to quit: ").strip().lower()

        if choice == "q":
            return _select_and_confirm(optimizations, list(range(len(optimizations))))

        if choice == "a":
            selected = list(range(len(optimizations)))
            approved = _confirm_selection(optimizations, selected)
            ids = [optimizations[i]["id"] for i in selected]
            return ids, approved

        if choice == "s":
            return _selection_mode(optimizations)

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(optimizations):
                _show_evidence(idx, optimizations, bottleneck_map)
            else:
                print(f"Enter a number between 1 and {len(optimizations)}")
        except ValueError:
            print("Invalid input. Enter a number, 's', 'a', or 'q'.")


def _print_table(optimizations: list[dict], bottleneck_map: dict) -> None:
    print()
    print(f"{'#':<4s} {'Optimization':<55s} {'Job':<20s} {'Saved':<8s} {'Cost':<8s} {'Risk':<8s}")
    print("-" * 103)

    for i, opt in enumerate(optimizations):
        desc = opt.get("description", "")[:52]
        job = opt.get("job_name", "")[:18]
        saved = f"{opt.get('estimated_time_saved_min', 0)}m"
        cost = f"${opt.get('estimated_cost_per_run', 0):.2f}"
        risk = opt.get("risk_level", "")
        print(f"{i+1:<4d} {desc:<55s} {job:<20s} {saved:<8s} {cost:<8s} {risk:<8s}")


def _show_evidence(idx: int, optimizations: list[dict], bottleneck_map: dict) -> None:
    opt = optimizations[idx]
    job = opt.get("job_name", "")
    bottleneck = bottleneck_map.get(job, {})

    print()
    print(f"  ── Bottleneck Evidence ──")
    print(f"  Type:     {bottleneck.get('type', 'N/A')}")
    print(f"  Job:      {job}")
    print(f"  Severity: {bottleneck.get('severity', 'N/A')}")
    print(f"  Evidence: {bottleneck.get('evidence', 'N/A')}")
    print()
    print(f"  Proposed optimization:")
    print(f"    {opt.get('description', '')}")
    print(f"    Time saved: {opt.get('estimated_time_saved_min', 0)}m, "
          f"Cost: ${opt.get('estimated_cost_per_run', 0):.2f}/run, "
          f"Risk: {opt.get('risk_level', '')}")
    print()

    input("  Press Enter to return to the table...")


def _selection_mode(optimizations: list[dict]) -> tuple[list[str], bool]:
    print()
    nums = input("Select optimizations to apply (enter numbers, e.g. 1 3 4): ").strip()

    if not nums:
        return [], False

    selected = []
    for part in nums.split():
        try:
            idx = int(part) - 1
            if 0 <= idx < len(optimizations):
                selected.append(idx)
        except ValueError:
            pass

    if not selected:
        print("No valid selections.")
        return _selection_mode(optimizations)

    selected = sorted(set(selected))
    approved = _confirm_selection(optimizations, selected)
    ids = [optimizations[i]["id"] for i in selected]
    return ids, approved


def _confirm_selection(optimizations: list[dict], indices: list[int]) -> bool:
    print()
    print("Selected optimizations:")
    for i in indices:
        opt = optimizations[i]
        print(f"  {i+1}. {opt.get('description', '')[:60]}")

    result = input("Proceed? (y/n): ").strip().lower()
    return result == "y"


def _select_and_confirm(optimizations: list[dict], indices: list[int]) -> tuple[list[str], bool]:
    approved = _confirm_selection(optimizations, indices)
    ids = [optimizations[i]["id"] for i in indices]
    return ids, approved


def prompt_re_analyze_or_recompute() -> str:
    """After human edits selections, ask: re-analyze with LLM or just recompute savings?"""
    print()
    choice = input("Re-analyze with your edits (uses LLM), or just recompute savings? (1/2): ").strip()
    if choice == "2":
        return "recompute"
    return "reanalyze"


def summary_table(results: list[dict]) -> None:
    """Print field study summary table."""
    print()
    print(f"{'Repo':<30s} {'PR #':<8s} {'Bottlenecks':<12s} {'Min Wasted':<12s} {'Top Rec'}")
    print("-" * 80)
    for r in sorted(results, key=lambda x: -x.get("total_wasted", 0)):
        print(f"{r.get('repo', ''):<30s} {r.get('pr_number', 0):<8d} "
              f"{r.get('bottleneck_count', 0):<12d} {r.get('total_wasted', 0):<12d} "
              f"{str(r.get('top_rec', ''))[:25]}")
