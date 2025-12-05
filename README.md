# JWT Calculator Platform

## Front-End Instructions

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
uvicorn app.main:app --reload --port 8000
```

Access at `http://localhost:8000`

## Playwright E2E Tests

```bash
# Install Playwright browsers
playwright install --with-deps

# Run E2E tests
pytest tests/e2e/test_auth_playwright.py
```

## Docker Hub Repository

Docker image: [`shivajiburle/assignmentsqsqla`](https://hub.docker.com/r/shivajiburle/assignmentsqsqla)