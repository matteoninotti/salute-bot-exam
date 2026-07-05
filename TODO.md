# salute-bot (versione esame) — TODO

Build tracker for the stripped-down exam version. Ordered by build sequence.
Keep in sync at each step: check items off (`[x]`) as they land.

Legend: `[ ]` todo · `[~]` in progress · `[x]` done

**Style reminder (all files):** **type hints on every function/method signature** + docstrings documenting params & return (NOTE 2 of the assignment grades this), 4-space indent, Italian UI text, heavy encapsulation (`__private` + getters) on every class unless explicitly justified, OOP paradigm, **exactly one `return` per function/method (no early returns)**. Target OS = **GNU/Linux** (no macOS-isms). Decisions live in `log.md` — re-read the relevant section before starting each task.

> **Testing status:** there is currently **no test suite** — the earlier "Tested …" notes were removed as inaccurate. The real `unittest` suite is written in §10.6.

## Exam requirements → where they are covered

- **Client + server, CLI** → mock CUP server (`cup_server.py`) ↔ daemon (the only CUP client: `daemon.py`, `cup_client.py`); managed from `cli.py`
- **GUI on the client only (web)** → `web.py` + `templates/`
- **PDF printout of slot reports** → `report.py`
- **Server-side DB (users, slots) + request history** → `database.py` + `store.py` (`richieste` table = per-user request history)
- **No true client/server between CLI and daemon** → CLI/GUI/daemon just share the SQLite file

---

## 1 — Scaffolding & data
- [x] `requirements.txt` (flask, requests, fpdf2 — `Faker` added in §10.3)
- [x] `config.py` — shared paths, CUP URL, poll interval, `FRAME_SECONDS`
- [x] `database.py` — connection helper + schema: tables `utenti`, `prestazioni`, `targets`, `slots`, **`richieste`** (registration work-queue + per-user history)

## 2 — Domain models
- [x] `models.py` — `Slot` (natural-key hash) + `Prestazione`, private attrs + getters

## 3 — Persistence
- [x] `store.py` — `Store` class: users, prestazioni, targets; slots (save / known-keys / touch / read with `is_new` inferred from newest `first_seen`); `richieste` (insert pending, read a user's history); daemon-side resolve helpers (create user+target, baseline slots)

## 4 — Server half (mock CUP)
- [x] `cup_server.py` — Flask HTTP server (port 5050): `/prestazione?nre=` (resolve NRE) + `/slots?code=` (current slots). _Slot generation reworked in §10.3._

## 5 — Client half (watcher)
- [x] `cup_client.py` — `CupClient`: `requests.get` wrapper → `Prestazione` / list of `Slot`
- [x] `detector.py` — diff current vs known slots → the new ones
- [x] `daemon.py` — loop: (a) resolve pending `richieste` (call CUP, create user/target, baseline slots), then (b) sweep watched prestazioni, detect + save new slots; idle heartbeat when no users

## 6 — CLI client
- [x] `cli.py` — `CLI` class (injected I/O): register, add prestazione, slots, history. _Moved to raw `sys.argv` and CF-only in §10.1/§10.2._

## 7 — PDF report
- [x] `report.py` — `SlotReport` class: build a PDF of a user's slots (fpdf2), grouped by prestazione, `[NUOVO]` marker

## 8 — Web GUI client
- [x] `web.py` — Flask app (login by CF; register → stage a `richiesta`, page auto-refreshes until the daemon resolves it; dashboard slots with new highlighted; add prestazione; history; download PDF)
- [x] `templates/` — base, index, register, richiesta, dashboard, add, history
- [x] `static/style.css` — minimal styling
- [x] `validation.py` — shared CF/NRE checks (CLI + web); `Store` context-manager

## 9 — Wrap-up & exam deliverables
- [x] `README.md` — how to run (start CUP server → daemon → CLI/web), Italian + env vars + project map
- [x] Linux audit — grep clean (no macOS-isms; pathlib/os.path.join); `.venv` excluded from zip
- [x] Config via env vars (`SALUTEBOT_DB`, `SALUTEBOT_FRAME_SECONDS`, ...) for testing + faster demo
- [x] Store self-initialises the schema
- [x] **Technical documentation PDF** (required deliverable): `documentazione.py` → `documentazione.pdf` (Oggetto, Scopo, Analisi tecnica, commenti procedure, guida I/O, Conclusioni). _Source is reworked in §10.2/§10.5; the binary is not regenerated (§10.6)._
- [x] **Self-contained zip** of the project (excludes `.venv`, `__pycache__`, `*.db`, `report/`, dev docs) — _re-zip after the refactor_

## Post-build enhancements
- [x] Slot growth anchored per-prestazione to its first fetch (registering late no longer misses new slots)
- [x] `salutebotexam.py` — single-command launcher: starts cup_server + daemon + web in background (`start`/`stop`/`status`), logs to `logs/`
- [x] Web dashboard **auto-refreshes when a new slot appears**: JS polls `/api/state/<cf>` (a slot-count + newest-first_seen signature) every 3s and reloads only when it changes (`store.slots_signature`)

---

## 10 — Exam refactor (professor requirements)

Scope of the current refactor pass. Everything below is `[ ]` todo unless marked
done. Re-read the relevant `log.md` section before starting each item.

### 10.1 — Code style & architecture (all files)
- [ ] **Single return** — exactly one `return` per function/method; no early returns anywhere
- [ ] **CLI on raw `sys.argv`** — refactor `cli.py` off argparse to read `sys.argv` directly
- [ ] **Strict encapsulation** — every attribute `__private` (name-mangling) by default; `_protected`/public only where explicitly required, justified case-by-case
- [ ] **Internal helpers underscored** — every internal function/helper module gets a leading `_` (e.g. `_helper`); only the public API meant for external import stays unprefixed
- [ ] **No** `from __future__ import annotations` in any file
- [ ] **Simplicity** — avoid `while True` except the daemon background loop

### 10.2 — Email removal (complete)
- [ ] Remove the notification email field + all email logic **everywhere**: forms, `cli.py`, DB schema (`database.py`), `store.py`, `report.py`, `templates/`, and `documentazione.py`
- [ ] Drop email from `validation.py` (CF/NRE only)
- [ ] **Clean up every mention of email from the docs** — `README.md` (usage line & structure map), `log.md`, the technical PDF text, and any stray comments/docstrings
- [ ] Discard existing demo databases — no data migration required

### 10.3 — Dynamic slot generation (CUP server)
- [ ] Each service starts with **exactly 3** baseline slots
- [ ] Generate **infinite** new slots "at clock time" only for services `8901.20` and `8702.1`
- [ ] Exactly **one new slot per `SALUTEBOT_FRAME_SECONDS`**; on missed intervals, catch up together on the next request — one slot per missed interval
- [ ] `Faker` with `it_IT` locale + a **fixed seed = 0** (repeatable demos); add `Faker` to `requirements.txt`
- [ ] Fields generated: `date`, `time`, `facility`, `CAP`, `address`
- [ ] Appointment date range: random between **today** and **2027-12-31**
- [ ] Show only **currently available** slots
- [ ] Slots **expire 60s** after creation (auto-disappear), baseline included
- [ ] A regenerated expired slot counts as **brand-new** (no historical persistence)
- [ ] **Remove `data/fixtures.json`** — generate all slots dynamically in Python; the only immutable data are the two services and the NRE map: `{"010A31234500001": "8901.20", "020B45678900002": "8702.1"}`

### 10.4 — Type coverage fixes
- [ ] Add return annotations to all Flask routes (`web.py`, `cup_server.py`)
- [ ] Add parameter types to injected CLI/clock callables
- [ ] Keep annotations clean/simple — avoid complex `Callable`/`Union` unless necessary

### 10.5 — Documentation & notices
- [ ] Add the exact disclaimer `local demonstration only; CF-only access, no authentication` to: `README.md` (*Demo limitations and security*), technical doc (*Analisi tecnica*), and the web login page (short, clearly visible UI notice)
- [x] Review `log.md` — fully updated and aligned with these changes
- [x] Update `CLAUDE.md` — new design decisions, single-return rule, encapsulation requirements
- [x] Update `TODO.md` — this section (done first, before any other work)
- [x] Correct the false "tested" claims and align the test path across `TODO.md`/`CLAUDE.md`/`log.md` (no suite exists yet; it lands in §10.6)

### 10.6 — Testing & filesystem
- [ ] Stdlib `unittest` suite in `salutebotexam/tests/` covering: Faker generation, slot expiry logic, email-removal compliance, route behavior
- [ ] Re-run the manual end-to-end flow after the refactor (register CF+NRE → a new slot appears then expires at 60s → history → PDF)
- [x] Remove stale `tests/__pycache__` (foreign `.pyc` artifacts from another project)
- [ ] Read `assignment.md` and `ref_exercises/` for style matching — do **not** commit them
- [ ] Do **not** regenerate or commit `documentazione.pdf`
