"""The scraper seam: what the daemon requires of a scraper, independent of *how*
it scrapes.

The live Playwright drive (Phase 4) is the only real implementation; defining the
interface here lets the Phase 3 daemon (loop, rotation, robustness) be built and
tested against a fake now (build strategy D; the swappable seam of D5). A scrape of
one prestazione, driven by a `(CF, NRE)` credential, yields both the prestazione the
NRE unlocks (D33 — one per NRE) and its current slots (D16) — exactly what
registration acknowledgment (D14) and the sweep detector (D8/D20) consume.

Two failure modes are distinguished **at the type level** per D28, without pinning
the wire signal that tells them apart (that is the drive's job in Phase 4, and an
open item in the log §3):
  - `NREInvalidError` — the **permanent** "NRE invalid / expired / consumed"
    rejection. The loop deactivates that target, emails its owner, and rotates (D28).
  - `ScrapeError` — a **transient** JSF/flow failure, subject to retry + backoff (D11).
A normal "no slots" outcome is **not** an error: it is a `ScrapeResult` with an
empty slot list.
"""

from dataclasses import dataclass
from typing import Protocol

from salutebot.models import Prestazione, Slot


class ScrapeError(RuntimeError):
    """A transient failure of the scrape flow — retry with backoff (D11)."""


class NREInvalidError(RuntimeError):
    """The permanent 'NRE invalid / expired / consumed' rejection (D28) — do not
    retry; the loop rotates to the next active subscriber's NRE."""


@dataclass(frozen=True)
class ScrapeResult:
    """One prestazione's scrape output: the prestazione the NRE unlocks + its current
    slots. DTO carve-out (frozen data-carrier), as with `Slot`/`Prestazione`."""

    prestazione: Prestazione
    slots: list[Slot]


class Scraper(Protocol):
    """Drives the CUP no-login flow for one `(CF, NRE)` credential.

    Implemented for real by the Phase 4 Playwright drive; faked in tests. Raises
    `NREInvalidError` (permanent) or `ScrapeError` (transient); otherwise returns a
    `ScrapeResult` (possibly with empty `slots`)."""

    def scrape(self, cf: str, nre: str) -> ScrapeResult: ...
