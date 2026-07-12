# Mufor Belmond Portfolio API

FastAPI + SQLite backend for the portfolio and admin dashboard.

## Run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Default admin credentials are seeded on first run:

- Email: `admin@belmond.dev`
- Password: `ChangeMe123!`

Override them with `ADMIN_EMAIL` and `ADMIN_PASSWORD` in your environment before first run.
