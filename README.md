# API Health Checker — Python

A command-line HTTP health monitor that requests a service's health endpoint, measures the result, and emits a JSON report with a nonzero process exit code on failure.

## Run

```bash
python check_api.py --url http://localhost:8000
```

Point it to a service that exposes `/health`. For the local test suite:

```bash
python -m pip install pytest
pytest -q
```

No cloud credentials required. Don't target endpoints you aren't authorized to probe.
