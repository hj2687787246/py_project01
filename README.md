# py_project01

## Environment

- Python: `3.13`
- Create venv: `python -m venv .venv`
- Activate on PowerShell: `.\\.venv\\Scripts\\Activate.ps1`
- Install deps: `pip install -r requirements.txt`

## Runtime config

- Copy `.env.example` to `.env` and fill in the values you need.
- AI scripts under `第3章` require `DEEPSEEK_API_KEY`.
- MySQL scripts under `mysql` require the `MYSQL_*` variables from `.env.example`.

## FastAPI Layered Demo

- Standard layered FastAPI project: [Depends + SQLAlchemy 2 分层](/D:/Develop/Python-project/py_project01/Depends%20+%20SQLAlchemy%202%20分层)
- Internal structure: `app/config/db/dao/services/api/deps/core/schemas`
- Entry file: [main.py](/D:/Develop/Python-project/py_project01/Depends%20+%20SQLAlchemy%202%20分层/main.py)
- App module: [app/main.py](/D:/Develop/Python-project/py_project01/Depends%20+%20SQLAlchemy%202%20分层/app/main.py)

Run this demo:

```bash
cd "Depends + SQLAlchemy 2 分层"
copy .env .env
uvicorn main:app --reload
```

Integration test:

```bash
python tests/test_user_system.py
```

## Notes

- FastAPI demos use local SQLite database files generated at runtime.
- `__pycache__`, `.venv`, `.idea`, `.db`, and local `.env` files are ignored by Git.
