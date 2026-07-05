# Repository Guidelines

## Project Structure & Module Organization

The application lives in `salutebotexam/`. `cup_server.py` is the mock CUP API (the server), `daemon.py` polls it, `store.py`/`database.py` manage SQLite, and `cli.py`/`web.py` are the clients; `templates/` and `static/` hold the web assets. Root documents are `README.md` (usage), `log.md` (architecture, schema, API, design decisions), and `TODO.md` (tracked work). `ref_exercises/` defines the expected course-level style. **The architecture and every spec that can change during the project live in `log.md`, not here — read it there.**

## Build, Test, and Development Commands

Run from `salutebotexam/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python salutebotexam.py
python salutebotexam.py status
python salutebotexam.py stop
python -m unittest discover -s tests -t . -p "test_*.py"
python -m compileall .
```

For debugging, run `cup_server.py`, `daemon.py`, and `web.py` separately. The web UI is at `http://127.0.0.1:5001`.

## Coding Style & Naming Conventions

Use four spaces and PEP 8 names: `snake_case` functions/variables, `PascalCase` classes, uppercase constants. Keep code explicit and easy to defend orally. **Exactly one `return` per function/method — no early returns.** Avoid `while True` except for the daemon loop. The CLI reads `sys.argv` directly (no argparse). Add type hints and docstrings describing inputs, outputs, and side effects — including return annotations on every Flask route and parameter types on injected callables (clocks, clients, I/O); keep annotations simple, avoiding elaborate `Callable`/`Union` unless necessary. Do not use `from __future__ import annotations`.

Encapsulation is a professor requirement. Every attribute is private (`__attr`) unless it must be protected (`_attr`) or public; justify each exception individually. Expose state through properties. Internal module functions use a leading underscore; only the intended import API remains unprefixed. Keep code/comments/docstrings in English and UI text in Italian.

## Testing Guidelines

Use standard-library `unittest`; files go in `salutebotexam/tests/` as `test_*.py`. Isolate SQLite with temporary databases and inject clocks, clients, and I/O. Cover the slot generator and expiry, detection, registration, routes, and PDF output — the exact spec (baseline count, seed, expiry window) lives in `log.md`.

## Decisions, Tracker & Commits

**`log.md` is the single source of design truth and must never be stale** — update it the moment a design decision, schema, or API changes, in the same change that makes the change. **Re-read the relevant `log.md` sections at the start of every new `TODO.md` task** (grep by topic); never rely on memory. - claude.md holds the immutable info and guidelines. log.md holds architectural and specs choices that can change throughout the process (and must be kept up to date) - **Keep `TODO.md` in sync at commit time.** Whenever a commit completes or advances a tracked task, check it off (`[x]`) / update its status in `TODO.md` **in that same commit** — the tracker must never lag the code.

Use concise imperative commits, such as `Add deterministic slot generator`. Pull requests explain changes and verification; include screenshots for UI work. Do not commit `.venv/`, databases, reports, logs, PID files, or `__pycache__/`. **The build workflow (branching, TDD order, merge policy) lives in `log.md` §8.**

## Configuration & Safety

Use documented `SALUTEBOT_*` environment variables. CF and NRE are stored unencrypted (local exam demo) — treat them as sensitive. The security posture (CF-only access, no authentication, no email) and the exact demo-disclaimer text are specified in `log.md`.
