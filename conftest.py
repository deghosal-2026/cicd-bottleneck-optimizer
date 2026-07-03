import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="Run tests that make real GitHub API calls (requires GITHUB_TOKEN env var)",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "live: marks tests that hit real GitHub API")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-live"):
        return
    skip_live = pytest.mark.skip(reason="need --run-live option to run")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)
