"""Validate generated workflow YAML syntax and structure."""


def validate(yaml_content: str) -> tuple[bool, str]:
    if not yaml_content or not yaml_content.strip():
        return False, "Empty YAML content"

    import yaml
    try:
        parsed = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        return False, f"YAML parse error: {e}"

    if not isinstance(parsed, dict):
        return False, "YAML root is not a mapping"

    if "jobs" not in parsed:
        return False, "Missing required 'jobs' key"

    if not isinstance(parsed["jobs"], dict):
        return False, "'jobs' must be a mapping"

    jobs = parsed["jobs"]
    for name, job in jobs.items():
        if not isinstance(job, dict):
            return False, f"Job '{name}' must be a mapping"
        if "uses" in job:
            continue
        if "steps" not in job:
            return False, f"Job '{name}' missing 'steps'"
        if not isinstance(job["steps"], list):
            return False, f"Job '{name}' steps must be a list"

    return True, "Valid YAML"
