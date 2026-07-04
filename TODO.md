# salute-bot — project TODO

Shared build tracker (Matteo + Claude). Ordered by build strategy **D** (parse-half tested first → deterministic core → live drive last), tagged by MoSCoW. Decision IDs (`D#`) point to `salute-bot-log.md`. **Deadline: 2026-07-04.**

Legend: `[ ]` todo · `[~]` in progress · `[x]` done · **(M)** Must · **(S)** Should · **(C)** Could

---

## Phase 0 — scaffolding & docs

- [x] Align docs (log §3 resolved, feasibility updated, D29 addendum: separate HMAC/AEAD env keys)
- [x] Rebuild venv on Python 3.14.6, add `requirements.txt` + `pyproject.toml`
- [x] Guardrails: build-mode, encapsulation (professor req), no `__future__` annotations
- [x] **(M)** Config/secrets bootstrap — read `SALUTEBOT_ENC_KEY` + `SALUTEBOT_HMAC_KEY` from env; fail loudly if missing
- [x] **(M)** CF/NRE validation helpers (format checks; never log values) — NRE format is loose/unverified (no captured form page); tighten once confirmed

## Phase 1 — parse half (trustworthy, offline)

- [x] `Slot` model + D16 natural key (`iso_date, time, struttura, cap` → sha256 `slot_key`)
- [x] Slots parser (JSF CDATA extract, structural card parse) + 8 ground-truth tests vs real recon capture
- [x] **(M)** Parse the `epPrestazioni` confirmation page (prestazione code + descrizione) for registration acknowledgment — fixture: `recon/epPrestazioni_redacted.xhtml`

## Phase 2 — deterministic core (offline-testable)

- [x] **(M)** Store: SQLite schema — 4 tables `users`/`targets`/`prestazioni`/`slots` (D20) + `users.checknow_requested_at`/`last_checknow_at` (D26)
- [x] **(M)** Crypto layer (D29): `cf_hash = HMAC-SHA256(cf, hmac_key)` blind index (PK/FK); `cf_enc`/`nre` AEAD; two separate env keys
- [x] **(M)** Detector: per-prestazione dedup (D8/D20) — `new = current − known` in memory, `last_seen` bumped on present keys; `first_seen` persisted post-send by the fan-out (D36), not by the detector
- [x] **(M)** Alert fan-out: `slots(new) → targets → users` join; SES email adapter (D10/D15); at-least-once send-then-persist (D36); D32 email (full set, new highlighted)
- [x] **(M)** CLI management commands (D37): `-u [CF]` (optional, prompt when omitted), `--list`, `--disable` (numbered menu, D35), `--disable-all`, `--delete-user` (erases user rows only, shared `slots` kept per D20), returning-user menu — no-scrape surface (D27), injected-I/O testable
## Phase 3 — daemon / service

- [x] **(M)** Scraper seam (Protocol + `ScrapeResult` + typed `NREInvalidError` vs transient `ScrapeError`) so the daemon is testable with a fake before the Phase 4 drive exists (D5/D14/D28)
- [x] **(M)** `flock` single-instance guard (D27); systemd-friendly long-running process
- [x] **(M)** Self-clocking serial loop (D21/D22/D27): non-dormant sweep, N=1, 2-min per-prestazione floor (advances on every *attempt* so a failing scrape can't busy-loop), scrape→detect→fan-out; sleeps exactly until next-due
- [x] **(M)** Representative-NRE lifecycle (D28): first active target drives; rotate on permanent NRE-invalid (deactivate + email owner in Italian), retry next subscriber; prestazione dormant if none valid
- [x] **(M)** Robustness (D11): in-attempt retry + exponential backoff on transient `ScrapeError`; N=3 consecutive failed cycles → subscribers notified; dead-man heartbeat emitted + stale-check/broadcast primitives (external checker wiring → Phase 5)
- [x] **(M)** Fan-out partial-failure fix (D38, amends D36): persist on ≥1 delivered (kills the one-dead-mailbox spam loop); bounded inline per-recipient send retry + backoff; abandoned recipients surfaced in `FanOutResult.failed`; total-failure batch stays unpersisted (self-heal)
- [x] **(M)** `--check-now` end-to-end (D24/D26/D25/D39): CLI-owned cooldown + block-poll; daemon serving via the two `users` timestamps; check-now lane served before the sweep each tick; per-prestazione coalescing realized by an **atomic scrape claim** (D39, N>1-safe) rather than an explicit job-queue; idle sleep capped at a 2 s poll tick so the block-poll is answered promptly
- [x] **(M)** New-user registration + add-prestazione (D14/D40): daemon-driven acknowledgment scrape (NRE→prestazione + initial slots) via a 5th `pending_registrations` staging table; CLI stages an unresolved (CF, NRE), block-polls, confirms, then persists user/target; add-prestazione is an interactive returning-user-menu action (not a flag, D37); brand-new prestazioni are baselined (no alert)

## Phase 4 — live drive (riskiest, needs valid NRE)

- [x] **(M)** Scraper drive (D42): `LiveScraper` — Playwright headless Chromium through the stateful JSF flow (seed → form → **two-click** proceed/`nreButton` → epPrestazioni → "Avanti" → `altre disponibilità` → `estendi area`/`nextArea` → harvest `availableAppointmentsContainer`); browser harvests ViewState/p_auth/ice.* itself. **Confirmed working end-to-end 2026-07-04** against a real ricetta (14 slots harvested + parsed); SMOKE-CONFIRM points resolved (proceed = 2 clicks; altre-disp→estendi both fire; warning dialog absent → wait trimmed)
- [x] **(M)** Live smoke run — valid ricetta full flow confirmed (`python -m salutebot.scraper.drive`, ~28–36 s/scrape: ~17 s of it is the CUP loading the slots page). — [ ] dead-ricetta run still pending for the invalid signal (below)
- [x] NRE input box count = 1, format = 15-char (§3/D42). — [ ] exact "NRE invalid" wire signal (D28): capture from the physical dead ricetta → wire `_check_invalid_nre` (rotation dormant until then)
- [ ] **(C)** HAR-replay harness for offline drive testing (`recon/flow.har`)

## Phase 5 — demo / ship

- [ ] **(M)** Walking skeleton: fake scraper adapter → real detector/store/SES → demoable end-to-end (deadline insurance)
- [ ] **(M)** Demo/test fixture strategy — scrubbed saved markup, deterministic exam run
- [ ] **(M)** Run on Ubuntu amd64 (platform constraint, D12)
- [ ] **(M)** CI: GitHub ubuntu-amd64 runner + LocalStack; one real-AWS SES smoke to a verified address (D15)
- [ ] **(S)** systemd service unit (`Restart=always`, D21)
- [ ] **(M)** Dead-man checker wiring (D11): external cron/systemd that reads the heartbeat, calls `notify_watcher_down` when stale, with once-per-outage de-dup (primitives already built in Phase 3)
- [ ] **(S)** EC2 t3.small (amd64) 24/7 deploy (D13)
- [x] **(S)** Rebuild the PRD doc from log D1–D30 + feasibility (only doc not yet rebuilt)

## Backlog — Should / Could / Won't-this-MVP

- [ ] **(S)** SMS via Twilio plain number; email 6-digit verification; Web-UI-ready Client seam
- [ ] **(C)** Vertical worker-pool scaling (raise N) — gated on global rate cap; Telegram channel; change notification email/phone
- [ ] **Won't (MVP):** auto-booking · real Web UI · custom SMS sender-ID · slot field filters
