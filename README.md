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

## Notes

- FastAPI demos use local SQLite database files generated at runtime.
- `__pycache__`, `.venv`, `.idea`, `.db`, and local `.env` files are ignored by Git.

