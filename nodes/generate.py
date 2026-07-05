"""LangGraph nodes for YAML generation and validation."""

from lib.generator import rewrite
from lib.validator import validate
from llm.client import LLMClient


def generate_yaml_node(state: dict) -> dict:
    workflows = state.get("workflows", [])
    selected_ids = state.get("selected_optimizations", [])
    optimizations = state.get("optimizations", [])

    rewritten = rewrite(workflows, selected_ids, optimizations)

    if not rewritten:
        llm_client = state.get("llm_client")
        if llm_client:
            rewritten = _generate_with_llm(llm_client, workflows, optimizations, selected_ids)

    return {
        "rewritten_yaml": rewritten,
        "errors": state.get("errors", []),
    }


def validate_syntax_node(state: dict) -> dict:
    yaml_content = state.get("rewritten_yaml", "")
    attempts = state.get("validation_attempts", 0)

    is_valid, msg = validate(yaml_content)

    if not is_valid:
        attempts += 1
        print(f"  YAML validation failed (attempt {attempts}): {msg}")
        if attempts >= 3:
            print("  Max validation attempts reached. Stopping.")

    return {
        "validation_attempts": attempts,
        "rewritten_yaml": yaml_content if is_valid else "",
        "errors": state.get("errors", []),
    }


def _generate_with_llm(llm_client, workflows: list[dict], optimizations: list[dict], selected_ids: list[str]) -> str:
    selected = [o for o in optimizations if o["id"] in selected_ids]
    original = workflows[0].get("content", "") if workflows else ""

    prompt = f"""Rewrite this GitHub Actions workflow YAML with the following optimizations applied:

Original workflow:
```yaml
{original}
```

Optimizations to apply:
"""
    for opt in selected:
        prompt += f"- {opt['description']}\n  YAML change: {opt.get('yaml_diff_hint', '')}\n"

    prompt += """
Return ONLY the complete rewritten YAML. No explanations, no markdown.
"""

    try:
        result = llm_client.call_local(prompt)
        return result.strip()
    except ConnectionError:
        print("  → YAML generation: OMLX local LLM not available. Skipping.")
        return ""
