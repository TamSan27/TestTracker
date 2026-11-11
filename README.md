# Test Case Tracker

A web app where you enter a URL, pick the types of testing, and get a test report.

## Run locally (Windows PowerShell)
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
copy .env.example .env
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

## Run our own tests
```
pip install pytest httpx
pytest
```
