import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | None = None, validate: bool = True) -> dict[str, Any]:
    if path is None:
        path = _find_config()

    if not path:
        print("Error: config.yaml not found", file=sys.stderr)
        print("Copy config.yaml.example to config.yaml and fill in your values.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(path):
        print(f"Error: config file not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path) as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in {path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not config:
        print(f"Error: Empty config file: {path}", file=sys.stderr)
        sys.exit(1)

    if validate:
        _validate_config(config)

    return config


def _find_config() -> str | None:
    candidates = [
        os.environ.get("CICD_CONFIG"),
        "config.yaml",
        "config.yml",
        os.path.expanduser("~/.config/cicd-bottleneck-optimizer/config.yaml"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def _validate_config(config: dict[str, Any]) -> None:
    errors: list[str] = []

    # github.token
    github = config.get("github", {})
    token = github.get("token", "") if github else ""
    if not token:
        errors.append("github.token is required")

    # cost_rates
    cost_rates = config.get("cost_rates", {})
    if not cost_rates:
        errors.append("cost_rates section is required")
    else:
        if "runner_per_min" not in cost_rates:
            errors.append("cost_rates.runner_per_min is required")
        if "cache_per_gb_month" not in cost_rates:
            errors.append("cost_rates.cache_per_gb_month is required")

    # Warn about missing cloud keys (non-fatal)
    llm = config.get("llm", {})
    cloud = llm.get("cloud", {}) if llm else {}
    if cloud:
        if not cloud.get("openai_api_key") and not cloud.get("anthropic_api_key"):
            print("Warning: No cloud LLM keys configured. Will use local OMLX only.", file=sys.stderr)

    if errors:
        for e in errors:
            print(f"Config error: {e}", file=sys.stderr)
        sys.exit(1)


def check_omlx_reachable(config: dict[str, Any]) -> None:
    local_cfg = config.get("llm", {}).get("local", {})
    base_url = local_cfg.get("base_url", "http://127.0.0.1:8000/v1")

    try:
        req = urllib.request.Request(
            f"{base_url}/models",
            headers={"Authorization": f"Bearer {local_cfg.get('api_key', 'omlx-test')}"},
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        print(
            "Warning: OMLX not reachable at {}. LLM-dependent features (classify, propose) will fail. "
            "Start OMLX or configure cloud LLM keys.".format(base_url),
            file=sys.stderr,
        )


def check_act_installed() -> None:
    import shutil

    if not shutil.which("act"):
        print(
            "Warning: 'act' not found. YAML validation will use PyYAML fallback instead of dry-run.",
            file=sys.stderr,
        )


def check_token_scope(config: dict[str, Any], mode: str) -> None:
    token = config.get("github", {}).get("token", "")
    if not token:
        return

    try:
        req = urllib.request.Request(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "cicd-bottleneck-optimizer",
            },
        )
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())

        # Check for 403/401 by inspecting status
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("Error: Invalid GitHub token.", file=sys.stderr)
            sys.exit(1)
        if e.code == 403:
            if mode == "optimize":
                print(
                    "Error: Token lacks repo scope. Optimize mode requires write access. "
                    "Use --field-study or --audit for read-only analysis.",
                    file=sys.stderr,
                )
                sys.exit(1)
    except Exception:
        # Network error — skip scope check, let API calls fail naturally
        pass
