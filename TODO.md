# salute-bot (versione esame) — TODO

Build tracker for the stripped-down exam version. Ordered by build sequence.
Keep in sync at each step: check items off (`[x]`) as they land.

Legend: `[ ]` todo · `[~]` in progress · `[x]` done

**Style reminder (all files):** **type hints on every function/method signature** + docstrings documenting params & return (NOTE 2 of the assignment grades this), 4-space indent, Italian UI text, heavy encapsulation (`__private` + getters) on every class unless explicitly justified, OOP paradigm. Target OS = **GNU/Linux** (no macOS-isms). Decisions live in `log.md`.

## Exam requirements → where they are covered

- **Client + server, CLI** → mock CUP server (`cup_server.py`) ↔ daemon (the only CUP client: `daemon.py`, `cup_client.py`); managed from `cli.py`
- **GUI on the client only (web)** → `web.py` + `templates/`
- **PDF printout of slot reports** → `report.py`
- **Server-side DB (users, slots) + request history** → `database.py` + `store.py` (`richieste` table = per-user request history)
- **No email, no true client/server between CLI and daemon** → CLI/GUI/daemon just share the SQLite file

---

## 1 — Scaffolding & data
- [x] `requirements.txt` (flask, requests, fpdf2)
- [x] `data/fixtures.json` — NRE→prestazione map + scripted slot frames that grow over time
- [x] `config.py` — shared paths, CUP URL, poll interval, `FRAME_SECONDS`
- [x] `database.py` — connection helper + schema: tables `utenti`, `prestazioni`, `targets`, `slots`, **`richieste`** (registration work-queue + per-user history)

## 2 — Domain models
- [x] `models.py` — `Slot` (natural-key hash) + `Prestazione`, private attrs + getters (tested: key stability, address excluded from key, name-mangling)

## 3 — Persistence
- [x] `store.py` — `Store` class: users, prestazioni, targets; slots (save / known-keys / touch / read with `is_new` inferred from newest `first_seen`); `richieste` (insert pending, read a user's history); daemon-side resolve helpers (create user+target, baseline slots). Tested full lifecycle + is_new rule.

## 4 — Server half (mock CUP)
- [x] `cup_server.py` — Flask HTTP server (port 5050; 5000 is taken by macOS AirPlay): `/prestazione?nre=` (resolve NRE) + `/slots?code=` (frame by wall-clock, `FRAME_SECONDS`). Tested frame math (fake clock), routes (test client), and a real curl smoke.

## 5 — Client half (watcher)
- [x] `cup_client.py` — `CupClient`: `requests.get` wrapper → `Prestazione` / list of `Slot`. Tested against a live server (real HTTP).
- [x] `detector.py` — diff current vs known slots → the new ones
- [x] `daemon.py` — loop: (a) resolve pending `richieste` (call CUP, create user/target, baseline slots), then (b) sweep watched prestazioni, detect + save new slots; idle heartbeat when no users. Tested with a fake client (baseline → new-slot punchline).

## 6 — CLI client
- [x] `cli.py` — `CLI` class (injected I/O): register (CF+email+NRE → stage a `richiesta`, block-poll until the daemon resolves it, show result), add prestazione, slots, history. Argparse sub-commands. Tested all flows + validation + timeout.

## 7 — PDF report
- [x] `report.py` — `SlotReport` class: build a PDF of a user's slots (fpdf2), grouped by prestazione, `[NUOVO]` marker. Tested: valid PDF, accented chars, empty case.

## 8 — Web GUI client
- [x] `web.py` — Flask app (login by CF; register → stage a `richiesta`, page auto-refreshes until the daemon resolves it; dashboard slots with new highlighted; add prestazione; history; download PDF). Tested all routes (Flask test client) + real HTTP.
- [x] `templates/` — base, index, register, richiesta, dashboard, add, history
- [x] `static/style.css` — minimal styling
- [x] `validation.py` — shared CF/NRE/email checks (CLI + web); `Store` context-manager

## 9 — Wrap-up & exam deliverables
- [x] `README.md` — how to run (start CUP server → daemon → CLI/web), Italian + env vars + project map
- [x] Retrofit type hints + typed docstrings across all files (NOTE 2)
- [x] Linux audit — grep clean (no macOS-isms; pathlib/os.path.join); `.venv` excluded from zip
- [x] Config via env vars (`SALUTEBOT_DB`, `SALUTEBOT_FRAME_SECONDS`, ...) for testing + faster demo
- [x] Store self-initialises the schema (bug found by the e2e: no process created tables)
- [x] **Technical documentation PDF** (required deliverable): `documentazione.py` → `documentazione.pdf` (Oggetto, Scopo, Analisi tecnica, commenti procedure, guida I/O, Conclusioni). 3 pages.
- [x] **Self-contained zip** of the project (excludes `.venv`, `__pycache__`, `*.db`, `report/`, dev docs)
- [x] Manual end-to-end run: register (daemon resolves), new slot appears after FRAME_SECONDS (`>> NUOVO`), history, PDF — all as real processes over HTTP + sqlite

## Post-build enhancements
- [x] Fix: slot growth anchored per-prestazione to its first fetch (registering late no longer misses new slots)
- [x] `salutebotexam.py` — single-command launcher: starts cup_server + daemon + web in background (`start`/`stop`/`status`), logs to `logs/`
- [x] Fixtures expanded to **17 slots per prestazione** (flat list + `baseline`); one new slot revealed every `FRAME_SECONDS`, so the demo grows for ~2 min
- [x] Web dashboard **auto-refreshes when a new slot appears**: JS polls `/api/state/<cf>` (a slot-count + newest-first_seen signature) every 3s and reloads only when it changes (`store.slots_signature`)
