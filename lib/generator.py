"""Rewrite workflow YAML with selected optimizations applied."""

import re


def rewrite(workflows: list[dict], selected_ids: list[str], optimizations: list[dict]) -> str:
    if not workflows or not selected_ids:
        return ""

    selected = {o["id"]: o for o in optimizations if o["id"] in selected_ids}
    if not selected:
        return ""

    target = _find_target_workflow(workflows, list(selected.values()))
    content = target.get("content", "")

    if not content:
        return ""

    changes = []
    for opt_id, opt in selected.items():
        btype = opt.get("bottleneck_type", "")
        job = opt.get("job_name", "")

        if btype == "missing_cache" and job:
            new_content = _add_cache(content, job)
            if new_content != content:
                content = new_content
                changes.append(f"added cache to {job}")
            else:
                changes.append(f"cache suggested for {job} (manual review)")
        elif btype == "serial_parallel" and job:
            new_content = _add_needs_parallel(content, job)
            if new_content != content:
                content = new_content
                changes.append(f"parallelized {job}")
            else:
                changes.append(f"parallel suggested for {job} (manual review)")
        elif btype == "redundant_matrix":
            new_content = _reduce_matrix(content, job)
            if new_content != content:
                content = new_content
                changes.append(f"reduced matrix in {job}")
            else:
                changes.append(f"matrix reduction suggested for {job}")
        elif btype == "redundant_rebuild":
            new_content = _add_artifact_reuse(content, job)
            if new_content != content:
                content = new_content
                changes.append(f"artifact reuse for {job}")
            else:
                changes.append(f"artifact reuse suggested for {job}")
        elif btype == "oversized_context":
            new_content = _add_dockerignore_note(content, job)
            if new_content != content:
                content = new_content
                changes.append(f"context optimization for {job}")
            else:
                changes.append(f".dockerignore suggested for {job}")

    header = f"# CI/CD Bottleneck Optimizer: {', '.join(changes)}\n"
    if not content.startswith("#"):
        content = header + content

    return content


def _find_target_workflow(workflows: list[dict], opts: list[dict]) -> dict:
    if len(workflows) == 1:
        return workflows[0]

    best = None
    best_matches = -1
    for wf in workflows:
        wf_job_names = {j["name"] for j in wf.get("jobs", [])}
        matches = sum(1 for o in opts if _base_job_name(o.get("job_name", "")) in wf_job_names)
        if matches > best_matches:
            best = wf
            best_matches = matches

    return best or workflows[0]


def _base_job_name(job_name: str) -> str:
    return job_name.split(" / ")[0].strip() if " / " in job_name else job_name


def _find_job_block(lines: list[str], job_name: str) -> tuple[int, int] | None:
    """Find the start and end line indices of a job block in the YAML."""
    base_name = _base_job_name(job_name)
    job_pattern = re.compile(rf"^(\s*){re.escape(base_name)}:\s*$")
    start = None
    base_indent: int | None = None

    for i, line in enumerate(lines):
        m = job_pattern.match(line)
        if m:
            start = i
            base_indent = len(m.group(1))
            break

    if start is None or base_indent is None:
        return None

    end = len(lines)
    for i in range(start + 1, len(lines)):
        line = lines[i]
        if line.strip() == "":
            continue
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if indent <= base_indent and stripped and not stripped.startswith("#"):
            end = i
            break

    return (start, end)


def _add_cache(yaml_content: str, job_name: str) -> str:
    lines = yaml_content.split("\n")
    block = _find_job_block(lines, job_name)
    if block is None:
        return yaml_content

    start, end = block
    steps_idx = None
    for i in range(start, end):
        stripped = lines[i].lstrip()
        if stripped.startswith("steps:"):
            steps_idx = i
            break

    if steps_idx is None:
        return yaml_content

    indent = len(lines[steps_idx]) - len(lines[steps_idx].lstrip())
    cache_lines = [
        " " * (indent + 2) + "- name: Cache dependencies",
        " " * (indent + 4) + "uses: actions/cache@v4",
        " " * (indent + 4) + "with:",
        " " * (indent + 6) + "path: |",
        " " * (indent + 8) + "~/.npm",
        " " * (indent + 8) + "~/.cache/pip",
        " " * (indent + 6) + "key: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json', '**/requirements.txt') }}",
        " " * (indent + 6) + "restore-keys: |",
        " " * (indent + 8) + "${{ runner.os }}-deps-",
    ]

    result = lines[:steps_idx + 1] + cache_lines + lines[steps_idx + 1:]
    return "\n".join(result)


def _add_needs_parallel(yaml_content: str, job_name: str) -> str:
    lines = yaml_content.split("\n")
    block = _find_job_block(lines, job_name)
    if block is None:
        return yaml_content

    start, end = block
    for i in range(start, end):
        stripped = lines[i].lstrip()
        if stripped.startswith("needs:"):
            indent = len(lines[i]) - len(stripped)
            lines[i] = " " * indent + "# Removed needs: to allow parallel execution (ci-optimizer)"
            return "\n".join(lines)

    return yaml_content


def _reduce_matrix(yaml_content: str, job_name: str) -> str:
    lines = yaml_content.split("\n")
    block = _find_job_block(lines, job_name)
    if block is None:
        return yaml_content

    start, end = block
    for i in range(start, end):
        stripped = lines[i].lstrip()
        if stripped.startswith("strategy:"):
            indent = len(lines[i]) - len(stripped)
            lines.insert(i + 1, " " * (indent + 2) + "# TODO: Review matrix for redundant combinations (ci-optimizer)")
            return "\n".join(lines)

    return yaml_content


def _add_artifact_reuse(yaml_content: str, job_name: str) -> str:
    lines = yaml_content.split("\n")
    block = _find_job_block(lines, job_name)
    if block is None:
        return yaml_content

    start, end = block
    steps_idx = None
    for i in range(start, end):
        stripped = lines[i].lstrip()
        if stripped.startswith("steps:"):
            steps_idx = i
            break

    if steps_idx is None:
        return yaml_content

    indent = len(lines[steps_idx]) - len(lines[steps_idx].lstrip())
    artifact_lines = [
        " " * (indent + 2) + "- name: Download build artifacts",
        " " * (indent + 4) + "uses: actions/download-artifact@v4",
        " " * (indent + 4) + "with:",
        " " * (indent + 6) + "name: build-output",
        " " * (indent + 6) + "path: ./build",
    ]

    result = lines[:steps_idx + 1] + artifact_lines + lines[steps_idx + 1:]
    return "\n".join(result)


def _add_dockerignore_note(yaml_content: str, job_name: str) -> str:
    lines = yaml_content.split("\n")
    block = _find_job_block(lines, job_name)
    if block is None:
        return yaml_content

    start, end = block
    steps_idx = None
    for i in range(start, end):
        stripped = lines[i].lstrip()
        if stripped.startswith("steps:"):
            steps_idx = i
            break

    if steps_idx is None:
        return yaml_content

    indent = len(lines[steps_idx]) - len(lines[steps_idx].lstrip())
    note_lines = [
        " " * (indent + 2) + "- name: Optimize build context",
        " " * (indent + 4) + "run: |",
        " " * (indent + 6) + "if [ ! -f .dockerignore ]; then",
        " " * (indent + 8) + "cat > .dockerignore << 'EOF'",
        " " * (indent + 8) + "node_modules",
        " " * (indent + 8) + ".git",
        " " * (indent + 8) + "*.md",
        " " * (indent + 8) + "dist",
        " " * (indent + 8) + "build",
        " " * (indent + 8) + "EOF",
        " " * (indent + 6) + "fi",
    ]

    result = lines[:steps_idx + 1] + note_lines + lines[steps_idx + 1:]
    return "\n".join(result)
