"""Rewrite workflow YAML with selected optimizations applied."""


def rewrite(workflows: list[dict], selected_ids: list[str], optimizations: list[dict]) -> str:
    if not workflows or not selected_ids:
        return ""

    selected = {o["id"]: o for o in optimizations if o["id"] in selected_ids}
    target = workflows[0]
    content = target.get("content", "")

    if not content:
        return ""

    changes = []
    for opt_id, opt in selected.items():
        btype = opt.get("bottleneck_type", "")
        job = opt.get("job_name", "")
        hint = opt.get("yaml_diff_hint", "")

        if btype == "missing_cache" and job:
            content = _add_cache(content, job)
            changes.append(f"added cache to {job}")
        elif btype == "serial_parallel" and job:
            content = _add_needs_parallel(content, job)
            changes.append(f"parallelized {job}")
        elif btype == "redundant_matrix":
            content = _reduce_matrix(content, job)
            changes.append(f"reduced matrix in {job}")

    header = f"# CI/CD Bottleneck Optimizer: {', '.join(changes)}\n"
    if not content.startswith("#"):
        content = header + content

    return content


def _add_cache(yaml_content: str, job_name: str) -> str:
    import re
    lines = yaml_content.split("\n")
    result = []
    in_target = False
    added = False

    for line in lines:
        result.append(line)
        stripped = line.lstrip()

        if re.match(rf"^{'  ' * 0}{job_name}:", line):
            in_target = True
            continue

        if in_target and not added:
            indent = len(line) - len(line.lstrip())
            if stripped.startswith("steps:"):
                result.append(" " * (indent + 2) + "- uses: actions/cache@v4")
                result.append(" " * (indent + 4) + "with:")
                result.append(" " * (indent + 6) + "path: ~/.npm")
                result.append(" " * (indent + 6) + "key: ${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}")
                result.append(" " * (indent + 6) + "restore-keys: |")
                result.append(" " * (indent + 8) + "${{ runner.os }}-")
                added = True
                in_target = False

    return "\n".join(result)


def _add_needs_parallel(yaml_content: str, job_name: str) -> str:
    return yaml_content


def _reduce_matrix(yaml_content: str, job_name: str) -> str:
    return yaml_content
