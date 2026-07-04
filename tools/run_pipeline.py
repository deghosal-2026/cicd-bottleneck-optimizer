#!/usr/bin/env python3
"""
Run the full optimize pipeline on cached PRs.
Reads from data/, saves results to output/. No live API calls to public repos.

Usage:
  python3 tools/run_pipeline.py --zen                      # Zen paid model (deepseek-v4-flash)
  python3 tools/run_pipeline.py --zen --zen-model big-pickle # stealth free model
  python3 tools/run_pipeline.py --groq                      # Groq LLM (fast, free)
  python3 tools/run_pipeline.py --groq --max 10             # first 10 PRs
  python3 tools/run_pipeline.py --groq --resume             # skip already-analyzed PRs
  python3 tools/run_pipeline.py --no-llm                    # rules only
  python3 tools/run_pipeline.py --since 90                  # last 90 days
"""

import argparse
import json
import glob
import os
import sys
import time
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.profiler import parse_job_graph
from lib.classifier import classify
from lib.optimizer import propose, simulate
from lib.generator import rewrite
from lib.validator import validate
from nodes.pr import _make_title, _make_pr_body
from llm.client import LLMClient
import config as cfg


class GroqClient:
    """Groq free API client (800+ tok/s)."""
    def __init__(self, model: str, token: str):
        from openai import OpenAI
        self.client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=token)
        self.model = model

    def call_local(self, prompt: str, system: str | None = None, **kwargs) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = self.client.chat.completions.create(model=self.model, messages=messages, max_tokens=1024)
        return resp.choices[0].message.content or ""


class ZenClient:
    """OpenCode Zen API client (free + paid models)."""
    def __init__(self, model: str, token: str):
        from openai import OpenAI
        self.client = OpenAI(base_url="https://opencode.ai/zen/v1", api_key=token)
        self.model = model

    def call_local(self, prompt: str, system: str | None = None, **kwargs) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = self.client.chat.completions.create(model=self.model, messages=messages, max_tokens=1024)
        return resp.choices[0].message.content or ""


def parse_args():
    p = argparse.ArgumentParser(description="Run pipeline on cached PRs")
    p.add_argument("--data", default="data", help="Dataset directory")
    p.add_argument("--output", default="output", help="Output directory")
    p.add_argument("--since", type=int, default=90, help="Days to filter (default: 90)")
    p.add_argument("--max", type=int, default=0, help="Max PRs to process")
    p.add_argument("--no-llm", action="store_true", help="Rules only")
    p.add_argument("--groq", action="store_true", help="Use Groq free API")
    p.add_argument("--groq-model", default="llama-3.3-70b-versatile", help="Groq model")
    p.add_argument("--groq-token", default="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", help="Groq API key")
    p.add_argument("--zen", action="store_true", help="Use OpenCode Zen API")
    p.add_argument("--zen-model", default="deepseek-v4-flash", help="Zen model (paid: deepseek-v4-flash; free: deepseek-v4-flash-free, big-pickle, mimo-v2.5-free)")
    p.add_argument("--zen-token", default="", help="Zen API key (reads from auth.json if empty)")
    p.add_argument("--resume", action="store_true", help="Skip already-analyzed PRs")
    p.add_argument("--config", help="Path to config.yaml")
    return p.parse_args()


def report_dir(out_dir: str, repo_dir: str) -> str:
    return os.path.join(out_dir, os.path.basename(repo_dir))

def report_path(out_dir: str, repo_dir: str, pr_number: int) -> str:
    return os.path.join(report_dir(out_dir, repo_dir), f"PR-{pr_number}.md")

def report_exists(out_dir: str, repo_dir: str, pr_number: int) -> bool:
    return os.path.exists(report_path(out_dir, repo_dir, pr_number))


def _load_zen_token() -> str:
    """Load Zen API key from opencode auth.json."""
    auth_path = os.path.expanduser("~/.local/share/opencode/auth.json")
    if not os.path.exists(auth_path):
        return ""
    try:
        with open(auth_path) as f:
            auth = json.load(f)
        return auth.get("opencode", {}).get("key", "")
    except (json.JSONDecodeError, KeyError, TypeError):
        return ""

def main():
    args = parse_args()
    c = cfg.load_config(args.config, validate=False) if os.path.exists("config.yaml") else {}

    llm_client = None
    llm_label = "disabled"
    if not args.no_llm:
        if args.groq:
            llm_client = GroqClient(args.groq_model, args.groq_token)
            llm_label = f"Groq:{args.groq_model}"
        elif args.zen:
            token = args.zen_token
            if not token:
                token = _load_zen_token()
            if not token:
                print("ERROR: No Zen API key found. Run with --zen-token <key> or add to auth.json")
                sys.exit(1)
            llm_client = ZenClient(args.zen_model, token)
            llm_label = f"Zen:{args.zen_model}"
        else:
            llm_cfg = c.get("llm", {}) if c else {}
            if llm_cfg and llm_cfg.get("local"):
                llm_client = LLMClient(c)
                llm_label = f"OMLX:{llm_cfg['local'].get('model', '?')}"

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.since)
    pr_files = sorted(glob.glob(os.path.join(args.data, "*", "prs", "*.json")))
    filtered = []
    for f in pr_files:
        with open(f) as fh:
            pr = json.load(fh)
        created = pr.get("created_at", "")
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if dt >= cutoff:
                    filtered.append(f)
            except ValueError:
                continue
    if args.max > 0:
        filtered = filtered[: args.max]

    proc = 0
    errors = 0

    print(f"Cached PRs: {len(filtered)} (last {args.since}d)")
    print(f"LLM:        {llm_label}")
    print(f"Output:     {args.output}/")
    print()

    for i, path in enumerate(filtered):
        try:
            with open(path) as f:
                pr = json.load(f)

            repo_dir = os.path.dirname(os.path.dirname(path))
            repo_label = os.path.basename(repo_dir).replace("-", "/", 1)
            pr_num = pr["pr_number"]

            if args.resume and report_exists(args.output, repo_dir, pr_num):
                proc += 1
                continue

            # Parse profiles from CI runs
            profs = []
            for run in pr.get("ci_runs", []):
                for job in run.get("jobs", []):
                    if job.get("duration_sec", 0) > 0:
                        profs.append({
                            "job_name": job["name"],
                            "median_sec": job["duration_sec"],
                            "p90_sec": job["duration_sec"],
                            "p99_sec": job["duration_sec"],
                            "failure_rate": 0.0 if job.get("status") == "success" else 0.5,
                            "cache_hit_ratio": None,
                        })

            # Parse workflow YAML files
            wfs = []
            for wf_ref in pr.get("workflows", []):
                wf_path = os.path.join(repo_dir, "workflows", f'{wf_ref["hash"]}.yml')
                content = ""
                if os.path.exists(wf_path):
                    with open(wf_path) as f:
                        content = f.read()
                wf = {"filename": wf_ref["filename"], "content": content, "jobs": []}
                if content:
                    wf["jobs"] = parse_job_graph(wf)
                wfs.append(wf)

            if not profs:
                continue

            llm_tag = "LLM on" if llm_client else "rules only"
            print(f"  [{i+1}/{len(filtered)}] {repo_label:<25s} PR #{pr_num:<6d} analyzing {len(profs)} jobs ({llm_tag})...", flush=True)

            # Classify + propose
            bottlenecks = classify(profs, wfs, llm_client=llm_client)
            optimizations = propose(bottlenecks, profs, llm_client=llm_client)
            total_saved = simulate(optimizations)

            if not optimizations:
                continue

            # Generate YAML
            selected_ids = [o["id"] for o in optimizations]
            rewritten = rewrite(wfs, selected_ids, optimizations)
            is_valid, _ = validate(rewritten)

            # Save locally
            out_dir = os.path.join(args.output, os.path.basename(repo_dir))
            os.makedirs(os.path.join(out_dir, "workflows"), exist_ok=True)

            yaml_path = os.path.join(out_dir, "workflows", f"pr-{pr_num}-optimized.yml")
            with open(yaml_path, "w") as f:
                f.write(rewritten)

            title = _make_title(optimizations)
            body = _make_pr_body(repo_label, optimizations, bottlenecks, profs, rewritten, f"pr-{pr_num}")
            pr_path = os.path.join(out_dir, f"PR-{pr_num}.md")
            with open(pr_path, "w") as f:
                f.write(f"# {title}\n\n{body}")

            proc += 1
            print(f"    ✓ {len(bottlenecks)} bottlenecks, {len(optimizations)} optimizations, {total_saved}m saved", flush=True)

        except Exception as e:
            errors += 1
            print(f"  [{i+1}/{len(filtered)}] ERROR: {e}")

    print(f"\nDone. {proc} PRs processed, {errors} errors")
    print(f"Output: {args.output}/")


if __name__ == "__main__":
    main()
