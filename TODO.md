# salute-bot (versione esame) — TODO

Legend: `[ ]` todo · `[~]` in progress · `[x]` done

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
- [x] **Technical documentation** (required deliverable): `documentazione.md` (Oggetto, Scopo, Analisi tecnica, commenti procedure, guida I/O, Conclusioni). _Replaces the old `documentazione.py` → `documentazione.pdf` generator; content reworked in §10.2/§10.5._
- [x] **Self-contained zip** of the project (excludes `.venv`, `__pycache__`, `*.db`, `report/`, dev docs) — _re-zip after the refactor_

## Post-build enhancements
- [x] Slot growth anchored per-prestazione to its first fetch (registering late no longer misses new slots)
- [x] `salutebotexam.py` — single-command launcher: starts cup_server + daemon + web in background (`start`/`stop`/`status`), logs to `logs/`
- [x] Web dashboard **auto-refreshes when a new slot appears**: JS polls `/api/state/<cf>` (a slot-count + newest-first_seen signature) every 3s and reloads only when it changes (`store.slots_signature`)

---

## 10 — Exam refactor (professor requirements)

**Execution — one subsection at a time on a `phase-10` branch (workflow in `log.md` §8):**
write tests where they pay off. The stable modules (`models`, `validation`, `store`,
`detector`) are already covered and guard every later change. The volatile server/client
modules (`cup_server`, `daemon`, `cli`, `web`) get their **real** `unittest` coverage in
the subsection where their behaviour settles (10.2 email, 10.3 slots, 10.4 types) — **no
throwaway characterization tests up front**; each interim style change is guarded by
**compile + a manual smoke run**. Keep code **as simple and readable as possible**; tick
boxes, sync this file, and commit per subsection (no push/merge without an explicit
request). §10.6 = fill any gaps + full green.

### 10.1 — Code style & architecture (all files)
- [x] **Radical simplicity** — make ALL code much simpler: the most straightforward, readable implementation that just works; no cleverness or needless abstraction (readability first)
- [x] **Single return** — exactly one `return` per function/method; no early returns anywhere
- [x] **CLI on raw `sys.argv`** — refactor `cli.py` off argparse to read `sys.argv` directly
- [x] **Strict encapsulation** — every attribute `__private` (name-mangling) by default; `_protected`/public only where explicitly required, justified case-by-case
- [x] **Internal helpers underscored** — every internal function/helper module gets a leading `_` (e.g. `_helper`); only the public API meant for external import stays unprefixed
- [x] **No** `from __future__ import annotations` in any file
- [x] **Simplicity** — avoid `while True` except the daemon background loop

### 10.2 — Email removal (complete)
- [x] Remove the notification email field + all email logic **everywhere**: forms, `cli.py`, DB schema (`database.py`), `store.py`, `report.py`, `templates/`, and `documentazione.py`
- [x] Drop email from `validation.py` (CF/NRE only)
- [x] **Clean up every mention of email from the docs** — `README.md` (usage line & structure map), the technical PDF text, and stray comments/docstrings (`log.md`/`CLAUDE.md` keep the *decision record* that email was removed)
- [x] Discard existing demo databases — no data migration required

### 10.3 — Dynamic slot generation (CUP server)
- [x] Each service starts with **exactly 3** baseline slots
- [x] Generate **infinite** new slots "at clock time" only for services `8901.20` and `8702.1`
- [x] Exactly **one new slot per `SALUTEBOT_FRAME_SECONDS`**; on missed intervals, catch up together on the next request — one slot per missed interval
- [x] `Faker` with `it_IT` locale + a **fixed seed = 0** (repeatable demos); add `Faker` to `requirements.txt`
- [x] Fields generated: `date`, `time`, `facility` (Faker-picked from a curated hospital pool), `CAP`, `address`
- [x] Appointment date range: random between **today** and **2027-12-31**
- [x] Show only **currently available** slots
- [x] Slots **expire 60s** after creation (auto-disappear), baseline included
- [x] A regenerated expired slot counts as **brand-new** (no historical persistence)
- [x] **Remove `data/fixtures.json`** — generate all slots dynamically in Python; the only immutable data are the two services and the NRE map: `{"010A31234500001": "8901.20", "020B45678900002": "8702.1"}`

### 10.4 — Type coverage fixes
- [x] Add return annotations to all Flask routes (`web.py`, `cup_server.py`)
- [x] Add parameter types to injected CLI/clock callables
- [x] Keep annotations clean/simple — avoid complex `Callable`/`Union` unless necessary

### 10.5 — Documentation & notices
- [x] Add the exact disclaimer `local demonstration only; CF-only access, no authentication` to: `README.md` (*Demo limitations and security*), technical doc (*Analisi tecnica*), and the web login page (short, clearly visible UI notice)
- [x] Review `log.md` — fully updated and aligned with these changes
- [x] Update `CLAUDE.md` — new design decisions, single-return rule, encapsulation requirements
- [x] Update `TODO.md` — this section (done first, before any other work)
- [x] Correct the false "tested" claims and align the test path across `TODO.md`/`CLAUDE.md`/`log.md` (no suite exists yet; it lands in §10.6)

### 10.6 — Verification & filesystem (final step)
- [x] All per-subsection `unittest` coverage green (`salutebotexam/tests/`: models, validation, store + expiry, detector, cup_server generation/growth/expiry, daemon resolve, cli flows) — 34 tests
- [x] Re-run the manual end-to-end flow after the refactor (register CF+NRE → a new slot appears → PDF → history; 60s expiry covered by unit tests)
- [x] Remove stale `tests/__pycache__` (foreign `.pyc` artifacts from another project)
- [x] Read `assignment.md` and `ref_exercises/` for style matching — do **not** commit them (read; left as-is)
- [x] Do **not** regenerate or commit `documentazione.pdf` (untouched)
