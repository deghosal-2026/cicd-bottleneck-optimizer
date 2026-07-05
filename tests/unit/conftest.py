from unittest.mock import Mock
import pytest


@pytest.fixture
def matrix_workflow():
    return [
        {
            "filename": "matrix.yml",
            "content": "name: Matrix\non: [push]\njobs:\n  test:\n    strategy:\n      matrix:\n        os: [ubuntu, macos, windows]\n        python: ['3.10', '3.11', '3.12']\n    steps:\n      - run: pytest\n",
            "jobs": [
                {
                    "name": "test",
                    "steps": [{"run": "pytest"}],
                    "matrix": {"os": ["ubuntu", "macos", "windows"], "python": ["3.10", "3.11", "3.12"]},
                },
            ],
        },
    ]


@pytest.fixture
def matrix_profiles():
    return [
        {"job_name": "test", "median_sec": 300, "p90_sec": 350, "p99_sec": 400, "failure_rate": 0.0, "cache_hit_ratio": None},
    ]


@pytest.fixture
def mock_llm_client():
    client = Mock()
    client.call_local.return_value = "[]"
    return client
