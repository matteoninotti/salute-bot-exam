# salute-bot (versione esame) — design log

Living design doc for the stripped-down exam version. Section 1 describes the architecture as currently imagined; the later sections record the schema, the API, and the open questions we still need to analyze together before finalizing the build.

---

## 1 — Architecture overview

The app keeps the _shape_ of the real salute-bot — a watcher that polls a booking site and records when appointment slots appear — but strips it down to the essentials the exam asks for: a client/server pair over HTTP, a client GUI, a PDF export, and a database with per-user history.

There are **three runnable programs** plus a **shared SQLite file** they all read/write:

1. **Mock CUP server** (`cup_server.py`, Flask, port 5000) — the _server_. It stands in for the real Piemonte CUP website. It reads canned data from `data/fixtures.json` and answers two HTTP requests: "what prestazione does this NRE unlock?" and "what slots are currently available for this prestazione?". Its trick is that the slot list **grows over time** (scripted frames), so the watcher can actually observe a _new slot appearing_.

2. **Daemon / watcher** (`daemon.py`) — the _client_ in the client/server pair, and the **only** program that ever talks to the CUP server. A background loop that, every few seconds: (a) resolves any pending _registration requests_ the clients have left in the DB — looks the NRE up on the CUP server, creates the user/subscription, and baselines the prestazione's current slots; then (b) asks the CUP server for the current slots of every watched prestazione and saves the newly-appeared ones. It talks to the server through `cup_client.py` (a thin `requests` wrapper) and to the DB through `store.py`.

3. **The client UIs** — how a person actually uses the tool. Two of them, both reading/writing the same SQLite file (no network between them and the daemon — that is the "no _true_ client/server management" the exam allows):
   - **CLI** (`cli.py`) — register, add a prestazione, list current slots, view history.
   - **Web GUI** (`web.py`, Flask, port 5001) — the graphical client: log in by CF, register, see your slots, see your history, download the PDF report.

Supporting modules shared by the above: `config.py` (paths/URLs/settings), `database.py` (connection + schema), `store.py` (all the SQL), `models.py` (`Slot`, `Prestazione`), `detector.py` (the new-vs-known diff), `report.py` (PDF).

### The core idea in one picture

```
   data/fixtures.json
          │  (scripted frames, grows over time)
          ▼
   ┌───────────────┐   HTTP GET /slots?code=…    ┌──────────────┐
   │  CUP server   │◄────────────────────────────│    daemon    │
   │ (Flask :5000) │────────────────────────────►│  (poll loop) │
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

- **Registration** (through the daemon — the client never calls the CUP server itself). The user gives a CF, an email, and an NRE. The client inserts a **request** row into `richieste` (`status = 'pending'`) and then polls it. The daemon picks the pending request up, asks the CUP server `GET /prestazione?nre=…`, and writes the outcome back: on success it creates the `utenti`/`prestazioni`/`targets` rows, baselines the prestazione's current slots as _already seen_, and sets `status = 'ok'` (with the resolved code + description); on an unknown NRE it sets `status = 'invalid'`. The client sees the resolved row and shows the result. That same `richieste` row is what the user later reads back as their **request history**.

- **Watching** (the daemon loop) — for each distinct prestazione that has at least one subscriber: `GET /slots?code=…` → build `Slot` objects → `detector` splits them into _already known_ (bump `last_seen`) and _new_ (insert with `first_seen = now`). Because the current slots were baselined at registration, nothing is flagged new until the CUP server's scripted frames actually grow — at which point only the freshly-appeared slot carries the newest `first_seen`.

- **Viewing** — the CLI or web client reads straight from the DB: the user's current slots (join `targets → slots`, new ones highlighted), and their history (their own `richieste` rows — what they asked to watch, when, and the outcome). The web client can also render the slots to a PDF.

---

## 2 — Database schema (SQLite, secrets in clear text)

- **utenti** (`cf` PK, `email`) — one row per person.
- **prestazioni** (`code` PK, `descrizione`) — the services, shared across users.
- **targets** (`cf`, `code`, `nre`, PK `(cf, code)`) — a subscription: user _cf_ watches prestazione _code_ with their _nre_.
- **slots** (`code`, `slot_key`, `date`, `time`, `struttura`, `cap`, `address`, `first_seen`, `last_seen`, PK `(code, slot_key)`) — the appointments found for a prestazione, **shared per prestazione** (not per user). `slot_key` is a SHA-256 of the natural key so the same slot is recognised across checks. A slot is shown as **new** when its `first_seen` equals the newest `first_seen` for that prestazione _and_ that value differs from the oldest — so the baseline batch (all sharing one timestamp) is never highlighted, but a later-appearing slot is.
- **richieste** (`id` PK, `cf`, `email`, `nre`, `code`, `descrizione`, `status`, `requested_at`, `resolved_at`) — the **request log**, which doubles as the daemon's registration work-queue. A client inserts a row (`status = 'pending'`); the daemon fills in `code`/`descrizione` and flips `status` to `'ok'`/`'invalid'`. **This is the per-user "request history"** — the user reads back their own rows (`WHERE cf = ?`).

---

## 3 — Mock CUP HTTP API

- `GET /prestazione?nre=<nre>` → `{"code": "...", "descrizione": "..."}` (404 if the NRE is unknown). Does **not** advance the frame.
- `GET /slots?code=<code>` → `{"code": "...", "slots": [ {date,time,struttura,cap,address}, ... ]}`. The frame returned is chosen by **wall-clock time since the server started**: `frame = min((now - server_start) // FRAME_SECONDS, last_frame)`. So the slot list grows on a fixed real-time schedule regardless of how often it is polled, and sticks on the last frame.

The only state the server keeps is its **start time** (in memory); restarting it restarts the growth from the baseline. For a clean demo: start the server, register a user right away (baseline = frame 0), then watch the new slot appear after `FRAME_SECONDS`.

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
- **Baseline = already seen.** At registration the daemon records the prestazione's current slots as seen, so they are never flagged new. When the frames later grow, the whole list is shown again with only the freshly-appeared slot(s) highlighted.
- **"New" is inferred from `first_seen`** (option i): a slot is new when its `first_seen` is the newest for that prestazione and differs from the oldest. Same highlight for everyone; no per-user "last viewed" tracking.
- **Slots are shared per prestazione**, de-duplicated by a natural-key hash — the cleanest model when several users watch the same service.
- **Secrets (CF/NRE) in clear text** — no crypto, per the agreed exam simplification.
- **Scripted, wall-clock frame growth** — the slot list advances on a real-time schedule (not per poll), so growth is deterministic and independent of poll frequency.
- **Heavy encapsulation on _all_ classes** (`__private` + getters), with exceptions only where explicitly justified case by case (e.g. a frozen data-carrier). The professor's requirement.

---

## 6 — Resolved decisions (were the open questions)

1. **Registration path** → **through the daemon**, via a `pending` row in `richieste`. The client never calls the CUP server; only the daemon does.
2. **History semantics** → **B, a personal action-log.** One `richieste` row per user request-to-watch; history is per-user, not the shared check-log.
3. **Baseline slots** → **baseline = already seen.** The daemon records current slots as seen at registration; when a new slot later appears, the whole list is reprinted with the new one highlighted.
4. **What "new" means** → **(i) inferred from `first_seen`** — newest `first_seen` for the prestazione, and only when it differs from the oldest (so the baseline is never highlighted).
5. **Frame growth model** → **wall-clock** (`(now - server_start) // FRAME_SECONDS`), not per poll. Start-time is in-memory; server restart resets growth.
6. **SQLite from multiple processes** → **accepted.** Each process opens its own short-lived connection; contention is negligible at exam scale (noted as a known limit).
7. **Daemon with no users** → **idles** (nothing to poll); prints a quiet heartbeat line so the demo shows it is alive.
8. **CLI vs web overlap** → **both fully featured** (register / list slots / history), each a complete client.

_Nothing open right now — this section stays as a record; new questions get appended here as they come up._
