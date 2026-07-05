# Repository Guidelines

## Project Structure & Module Organization

The application lives in `salutebotexam/`. `cup_server.py` provides the mock CUP API, `daemon.py` polls it, `store.py`/`database.py` manage SQLite, and `cli.py`/`web.py` are clients. Templates, CSS, and data configuration live in `templates/`, `static/`, and `data/`. Root documents contain requirements, decisions, tracked work, and usage. `ref_exercises/` defines the expected course-level style.

## Build, Test, and Development Commands

Run from `salutebotexam/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python salutebotexam.py
python salutebotexam.py status
python salutebotexam.py stop
python -m unittest discover -s tests -p "test_*.py"
python -m compileall .
```

For debugging, run `cup_server.py`, `daemon.py`, and `web.py` separately. The web UI is at `http://127.0.0.1:5001`.

## Coding Style & Naming Conventions

Use four spaces and PEP 8 names: `snake_case` functions/variables, `PascalCase` classes, uppercase constants. Keep code explicit and easy to defend orally. Prefer one return per function; avoid `while True` except for the daemon loop. Add type hints and docstrings describing inputs, outputs, and side effects. Do not use `from __future__ import annotations`.

Encapsulation is a professor requirement. Every attribute is private (`__attr`) unless it must be protected (`_attr`) or public; justify each exception individually. Expose state through properties. Internal module functions use a leading underscore; only the intended import API remains unprefixed. Keep code/comments/docstrings in English and UI text in Italian.

## Testing Guidelines

Use standard-library `unittest`; files go in `salutebotexam/tests/` as `test_*.py`. Isolate SQLite with temporary databases and inject clocks, clients, and I/O. Test baseline slots, clock-driven growth/expiry, detection, registration, routes, and PDF output.

## Decisions, Tracker, and Git Workflow

Before any task, phase, module, or `D#` citation, grep and read the relevant `log.md` decisions; never rely on memory. Keep `AGENTS.md` current when rules change. Synchronize `TODO.md` in every commit that advances a tracked task.

Use GitHub flow: one `phase-N` branch per TODO phase. Commit each completed/advanced task only with green tests and synchronized TODO status. Merge completed phases with `git merge --no-ff`; `main` stays releasable. Project-meta changes (`AGENTS.md`, guardrails, docs) go directly to `main`. Merge, push, and delete branches only when Matteo explicitly requests them.

Use concise imperative commits, such as `Add deterministic slot generator`. Pull requests explain changes and verification; include screenshots for UI work. Do not commit `.venv/`, databases, reports, logs, PID files, or `__pycache__/`.

## Configuration & Safety

Use documented `SALUTEBOT_*` environment variables. Treat CF and NRE as sensitive even though this local exam demo stores them unencrypted.
