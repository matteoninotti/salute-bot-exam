# salute-bot (versione esame) — TODO

Build tracker for the stripped-down exam version. Ordered by build sequence.
Keep in sync at each step: check items off (`[x]`) as they land.

Legend: `[ ]` todo · `[~]` in progress · `[x]` done

**Style reminder (all files):** English light docstrings, 4-space indent, Italian UI text, heavy encapsulation (`__private` + getters) on every class unless explicitly justified. Decisions live in `log.md`.

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
- [ ] `cup_server.py` — Flask HTTP server: `/prestazione?nre=` (resolve NRE, no advance) + `/slots?code=` (frame chosen by wall-clock since startup, `FRAME_SECONDS`)

## 5 — Client half (watcher)
- [ ] `cup_client.py` — `CupClient`: `requests.get` wrapper → `Prestazione` / list of `Slot`
- [ ] `detector.py` — diff current vs known slots → the new ones
- [ ] `daemon.py` — loop: (a) resolve pending `richieste` (call CUP, create user/target, baseline slots), then (b) sweep watched prestazioni, detect + save new slots; idle heartbeat when no users

## 6 — CLI client
- [ ] `cli.py` — register (CF+email+NRE → stage a `richiesta`, block-poll until the daemon resolves it, show result), add prestazione, list slots, view history

## 7 — PDF report
- [ ] `report.py` — build a PDF of a user's slots (fpdf2)

## 8 — Web GUI client
- [ ] `web.py` — Flask app (login by CF; register → stage a `richiesta` & poll until resolved; dashboard slots with new highlighted; history; download PDF)
- [ ] `templates/` — base, index, register, dashboard, history
- [ ] `static/style.css` — minimal styling

## 9 — Wrap-up
- [ ] `README.md` — how to run (start CUP server → daemon → CLI/web), Italian
- [ ] Manual end-to-end run: register a user (daemon resolves it), watch the daemon detect a new slot after `FRAME_SECONDS`, view history, export PDF
