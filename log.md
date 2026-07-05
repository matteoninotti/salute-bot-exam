# salute-bot (versione esame) — design log

Living design doc for the stripped-down exam version — the single source of truth for architecture, schema, API and design decisions, kept up to date as they change. Section 1 describes the architecture; the later sections record the schema, the API, and the (now resolved) design decisions.

---

## 1 — Architecture overview

The app keeps the _shape_ of the real salute-bot — a watcher that polls a booking site and records when appointment slots appear — but strips it down to the essentials the exam asks for: a client/server pair over HTTP, a client GUI, a PDF export, and a database with per-user history.

There are **three runnable programs** plus a **shared SQLite file** they all read/write:

1. **Mock CUP server** (`cup_server.py`, Flask, port 5050) — the _server_. It stands in for the real Piemonte CUP website. Its only immutable data are the **two services** (`8901.20`, `8702.1`) and the **NRE→code map**; every slot is **generated dynamically in Python** with `Faker` (`it_IT` locale, fixed seed for repeatable demos — no `data/fixtures.json`). It answers two HTTP requests: "what prestazione does this NRE unlock?" and "what slots are currently available for this prestazione?". Its trick is that the slot list **grows over wall-clock time**: each service starts with exactly **3 baseline slots** and gains **one new slot per `FRAME_SECONDS`** (missed intervals are caught up together on the next request, one slot each), so the watcher can actually observe a _new slot appearing_. Each slot **expires 60 seconds after creation** — only currently-available slots are ever served — so a regenerated slot counts as brand new (no historical persistence).

2. **Daemon / watcher** (`daemon.py`) — the _client_ in the client/server pair, and the **only** program that ever talks to the CUP server. A background loop that, every few seconds: (a) resolves any pending _registration requests_ the clients have left in the DB — looks the NRE up on the CUP server, creates the user/subscription, and baselines the prestazione's current slots; then (b) asks the CUP server for the current slots of every watched prestazione and saves the newly-appeared ones. It talks to the server through `cup_client.py` (a thin `requests` wrapper) and to the DB through `store.py`.

3. **The client UIs** — how a person actually uses the tool. Two of them, both reading/writing the same SQLite file (no network between them and the daemon — that is the "no _true_ client/server management" the exam allows):
   - **CLI** (`cli.py`) — register, add a prestazione, list current slots, view history.
   - **Web GUI** (`web.py`, Flask, port 5001) — the graphical client: log in by CF, register, see your slots, see your history, download the PDF report.

Supporting modules shared by the above: `config.py` (paths/URLs/settings), `database.py` (connection + schema), `store.py` (all the SQL), `models.py` (`Slot`, `Prestazione`), `detector.py` (the new-vs-known diff), `report.py` (PDF).

### The core idea in one picture

```
   Faker (it_IT, seeded)
          │  3 baseline + 1 slot / FRAME_SECONDS, each expires after 60s
          ▼
   ┌───────────────┐   HTTP GET /slots?code=…    ┌──────────────┐
   │  CUP server   │◄────────────────────────────│    daemon    │
   │ (Flask :5050) │────────────────────────────►│  (poll loop) │
   └───────────────┘   [ current slots as JSON ] └──────┬───────┘
                                                        │ writes
                                                        ▼
                                                 ┌──────────────┐
                                                 │  SQLite DB   │
                                                 │ users/slots/ │
                                                 │  history     │
                                                 └──────┬───────┘
                                                        │ read
                                       ┌────────────────┴───────────────┐
                                       ▼                                ▼
                                  CLI client                      Web GUI client
                                  (cli.py)                  (web.py :5001) ──► PDF
```

### The three main flows

- **Registration** (through the daemon — the client never calls the CUP server itself). The user gives a CF and an NRE (no email — it has been removed everywhere). The client inserts a **request** row into `richieste` (`status = 'pending'`) and then polls it. The daemon picks the pending request up, asks the CUP server `GET /prestazione?nre=…`, and writes the outcome back: on success it creates the `utenti`/`prestazioni`/`targets` rows, baselines the prestazione's current slots as _already seen_, and sets `status = 'ok'` (with the resolved code + description); on an unknown NRE it sets `status = 'invalid'`. The client sees the resolved row and shows the result. That same `richieste` row is what the user later reads back as their **request history**.

- **Watching** (the daemon loop) — for each distinct prestazione that has at least one subscriber: `GET /slots?code=…` → build `Slot` objects → `detector` splits them into _already known_ (bump `last_seen`) and _new_ (insert with `first_seen = now`). Because the current slots were baselined at registration, nothing is flagged new until the CUP server's scripted frames actually grow — at which point only the freshly-appeared slot carries the newest `first_seen`.

- **Viewing** — the CLI or web client reads straight from the DB: the user's current slots (join `targets → slots`, new ones highlighted), and their history (their own `richieste` rows — what they asked to watch, when, and the outcome). The web client can also render the slots to a PDF.

---

## 2 — Database schema (SQLite, secrets in clear text)

- **utenti** (`cf` PK) — one row per person. (No `email` column — email removed everywhere.)
- **prestazioni** (`code` PK, `descrizione`) — the services, shared across users.
- **targets** (`cf`, `code`, `nre`, PK `(cf, code)`) — a subscription: user _cf_ watches prestazione _code_ with their _nre_.
- **slots** (`code`, `slot_key`, `date`, `time`, `struttura`, `cap`, `address`, `first_seen`, `last_seen`, PK `(code, slot_key)`) — the appointments found for a prestazione, **shared per prestazione** (not per user). `slot_key` is a SHA-256 of the natural key so the same slot is recognised across checks. Slots are **persisted** but read with a **60-second expiry filter**: a row is only shown while `now - first_seen < 60s` (baseline slots included), so expired slots vanish and a later regenerated slot is a fresh row. A slot is shown as **new** when its `first_seen` equals the newest `first_seen` for that prestazione _and_ that value differs from the oldest — so the baseline batch (all sharing one timestamp) is never highlighted, but a later-appearing slot is.
- **richieste** (`id` PK, `cf`, `nre`, `code`, `descrizione`, `status`, `requested_at`, `resolved_at`) — the **request log**, which doubles as the daemon's registration work-queue. A client inserts a row (`status = 'pending'`); the daemon fills in `code`/`descrizione` and flips `status` to `'ok'`/`'invalid'`. **This is the per-user "request history"** — the user reads back their own rows (`WHERE cf = ?`).

---

## 3 — Mock CUP HTTP API

- `GET /prestazione?nre=<nre>` → `{"code": "...", "descrizione": "..."}` (404 if the NRE is unknown). Does **not** advance generation.
- `GET /slots?code=<code>` → `{"code": "...", "slots": [ {date,time,struttura,cap,address}, ... ]}`. Slots are **generated dynamically** with `Faker` (`it_IT`, fixed seed): `date` (random between today and 2027-12-31), `time`, `facility`→`struttura`, `CAP`→`cap`, and `address`. Each code starts with **3 baseline** slots at its anchor and gains **one new slot every `FRAME_SECONDS`** thereafter — on a request the server catches up all missed intervals at once (one slot per missed interval). Every slot **expires 60 seconds after its creation**, so the response contains only the slots currently within their 60s window (baseline included). The anchor is set on the first `/slots` for the code (the daemon's baseline fetch at registration), so growth is measured from when watching starts, no matter how long the server has been up.

The state the server keeps is a per-code anchor + the live (unexpired) generated slots, all in memory; restarting it restarts generation from the baseline. Because the seed is fixed, a fresh run reproduces the same sequence. For a clean demo: start the server, register a user, then watch a new slot appear every `FRAME_SECONDS` while older ones expire after 60s.

---

## 4 — Mapping to the exam requirements

- **Client + server, CLI** → CUP server (Flask) ↔ daemon (HTTP client via `requests`); managed from the CLI.
- **GUI on the client only** → `web.py` (Flask + templates); the server stays headless.
- **PDF printout of slot reports** → `report.py` (fpdf2), exposed from the web client.
- **Server-side DB (users, slots) + history** → `database.py`/`store.py`, with `richieste` as the per-user request history.
- **No email / no true client-server between CLI and daemon** → dropped email entirely; CLI, web, and daemon coordinate only through the shared SQLite file.

---

## 5 — Design decisions taken so far

- **Registration goes through the daemon, via the DB.** The client only ever writes a `pending` row into `richieste`; the daemon is the sole caller of the CUP server. Keeps the client/server boundary clean and mirrors the real app's staging approach.
- **"Request history" = a personal action-log** (option B). Each user request-to-watch is one `richieste` row, so a user's history is genuinely _theirs_ (differs per user), not a shared check-log.
- **Baseline = already seen.** At registration the daemon records the prestazione's current (3) baseline slots as seen, so they are never flagged new. When generation later adds a slot, only the freshly-appeared one is highlighted. (Baseline slots also age out under the 60s expiry, so the visible list is always the currently-available window.)
- **"New" is inferred from `first_seen`** (option i): a slot is new when its `first_seen` is the newest for that prestazione and differs from the oldest. Same highlight for everyone; no per-user "last viewed" tracking.
- **Slots are shared per prestazione**, de-duplicated by a natural-key hash — the cleanest model when several users watch the same service.
- **Secrets (CF/NRE) in clear text** — no crypto, per the agreed exam simplification.
- **Dynamic, seeded, wall-clock slot generation** — no `fixtures.json`; slots are built in Python with `Faker` (`it_IT`, fixed seed). Each service starts at **3 baseline** slots and gains **one per `FRAME_SECONDS`** (missed intervals caught up together, one each), anchored per-code to its first fetch. Deterministic and independent of poll frequency.
- **60-second slot expiry, applied uniformly.** Every slot (baseline included) disappears 60s after creation; only currently-available slots are served/shown. A regenerated slot is a brand-new row — no historical persistence of expired slots.
- **Slots still persist in the DB, read through a 60s expiry filter.** Keeps the exam's "server-side DB (users, slots)" requirement and the existing `first_seen`-based "new" highlight; the filter just hides expired rows on read.
- **Email removed everywhere** — no notification email in forms, CLI, schema, store, report, templates, README, this log, or the technical PDF. Existing demo databases are discarded (no migration).
- **Strict single return** — exactly one `return` per function/method, no early returns. **CLI parses `sys.argv` directly** (no argparse). `from __future__ import annotations` is banned; internal helpers/modules take a leading underscore.
- **Local-demo disclaimer** — the exact notice `local demonstration only; CF-only access, no authentication` appears in `README.md`, the technical doc (*Analisi tecnica*), and the web login page. No authentication; access is CF-only.
- **Heavy encapsulation on _all_ classes** (`__private` + getters), with exceptions only where explicitly justified case by case (e.g. a frozen data-carrier). The professor's requirement.

---

## 6 — Resolved decisions (were the open questions)

1. **Registration path** → **through the daemon**, via a `pending` row in `richieste`. The client never calls the CUP server; only the daemon does.
2. **History semantics** → **B, a personal action-log.** One `richieste` row per user request-to-watch; history is per-user, not the shared check-log.
3. **Baseline slots** → **baseline = already seen.** The daemon records current slots as seen at registration; when a new slot later appears, the whole list is reprinted with the new one highlighted.
4. **What "new" means** → **(i) inferred from `first_seen`** — newest `first_seen` for the prestazione, and only when it differs from the oldest (so the baseline is never highlighted).
5. **Frame growth model** → **wall-clock, anchored per-code to the first request** (`(now - anchor[code]) // FRAME_SECONDS`), not per poll and not from server start — so the baseline is always the first frame and a new slot appears ~FRAME_SECONDS after watching starts, regardless of when the user registers. Anchors are in-memory; server restart resets growth. _(Revised after a bug: anchoring to server-start meant registering late could baseline an already-grown set, so no new slot ever appeared.)_
6. **SQLite from multiple processes** → **accepted.** Each process opens its own short-lived connection; contention is negligible at exam scale (noted as a known limit).
7. **Daemon with no users** → **idles** (nothing to poll); prints a quiet heartbeat line so the demo shows it is alive.
8. **CLI vs web overlap** → **both fully featured** (register / list slots / history), each a complete client.
9. **Slot source** → **dynamic Faker generation** (`it_IT`, fixed seed), not `fixtures.json`. 3 baseline + one per `FRAME_SECONDS`, anchored per-code to the first fetch, with missed-interval catch-up (one slot each). Only the two services and the NRE map stay immutable.
10. **Slot storage vs expiry** → **keep the DB `slots` table, add a 60s read filter.** Slots persist with `first_seen`/`last_seen`; the read filter hides any row older than 60s, so the "server-side DB (slots)" requirement and the `first_seen` "new" highlight both survive. _(Chosen over server-only in-memory or dropping persistence.)_
11. **Baseline expiry** → **all slots expire uniformly**, baseline included — 60s after creation. The visible list is always the currently-available window; it can briefly hold fewer than 3 depending on `FRAME_SECONDS`.
12. **Generation anchor** → **per-code, set on that code's first `/slots` request** (resets on server restart), matching the pre-existing frame model (see #5 — not anchored to server start). The fixed Faker seed keeps a fresh run reproducible. _(Chosen over an absolute wall-clock epoch.)_
13. **"New" highlight under expiry** → **keep the `first_seen` model** (newest `first_seen` for the prestazione, differing from the oldest). Preserved because slots still persist (see #10).
14. **Email** → **removed entirely** from forms, CLI, schema, store, report, templates, README, this log, and the technical PDF. Existing demo DBs discarded; no migration.
15. **CLI parsing** → **raw `sys.argv`** (argparse dropped). **Single return** per function/method enforced project-wide; no `from __future__ import annotations`; internal helpers underscored.
16. **Disclaimer** → the exact notice `local demonstration only; CF-only access, no authentication` in `README.md`, the technical doc (*Analisi tecnica*), and the web login page.

_This section stays as a record; new questions get appended here as they come up._

---

## 7 — Exam deliverables & constraints (from the assignment)

- **Runs on GNU/Linux.** "Programs that do not run will result in failure." The stack (Python 3, Flask, requests, fpdf2, sqlite3) is cross-platform; we avoid any macOS/Windows-specific calls. The delivered zip excludes the (macOS-built) `.venv`; the user recreates it on Linux via `pip install -r requirements.txt`.
- **Technical documentation** (separate from the app's slot-report PDF). Required sections: _Oggetto_, _Scopo_, _Analisi tecnica_ (libraries, algorithms, flowcharts, key code), _commenti su procedure_, _guida I/O_ (concise user guide), _Conclusioni_. Delivered as `documentazione.md` (hand-written Markdown, replacing the old `documentazione.py` PDF generator); it drops all email content and carries the disclaimer `local demonstration only; CF-only access, no authentication` under _Analisi tecnica_.
- **Self-contained compressed project** (a zip that runs on its own).
- **Code quality is graded (NOTE 2):** comments, DocStrings, **documented input/output parameter types** of functions/methods, well-structured code, **OOP**. → We use type hints on every signature + docstrings that state params and return, and heavy encapsulation throughout.
- **Oral exam:** the project is presented and defended, so the code is kept at a level the student can fully explain (matches his course style).
- **Tests:** no suite exists yet; it is written during the refactor with the standard-library `unittest` framework in `salutebotexam/tests/` (temporary DBs; injected clocks, clients, and I/O).

---

## 8 — Build workflow (this refactor)

- **TDD, one `§10` subsection at a time.** For each subsection: write its `unittest` coverage first (red), implement to green while keeping the code as simple and readable as possible, sync `TODO.md`, then commit.
- **GitHub flow.** The refactor lives on a `phase-10` branch. Commit each advanced/completed subsection with green tests and synchronized TODO status; merge with `git merge --no-ff`, keeping `main` releasable. Project-meta changes may go straight to `main`.
- **Merge, push, and delete branches only when Matteo explicitly requests them.**
