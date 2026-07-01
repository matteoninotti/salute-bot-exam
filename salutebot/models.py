"""Core domain types.

The `Slot` is the unit the watcher diffs cycle-to-cycle. Its identity is a
*natural key* built from business fields (D16), because the CUP engine exposes
no stable backend slot id — row ids are positional ICEfaces dataTable indices
re-numbered on every render. The key is deliberately narrow (date, time,
struttura, CAP); doctor/unit and the full address are descriptive only, kept
out of the key because they are the most cosmetically volatile fields and would
cause false "new slot" alerts.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

# Unit separator — a byte that cannot appear in any of the joined fields, so the
# key is unambiguous (no "a|b" vs "a" + "|b" collision).
_KEY_SEP = "\x1f"


@dataclass(frozen=True)
class Slot:
    """One bookable appointment parsed from the slots page.

    Key fields (feed `slot_key`, per D16):
        iso_date   -- ISO date, weekday dropped (e.g. "2026-06-22")
        time       -- "HH:MM" (e.g. "16:00")
        struttura  -- facility name, whitespace-collapsed + upper-cased
        cap        -- postal code from data-address, or None when absent ("null")

    Descriptive fields (NOT part of the key; for --list and the alert email):
        prestazione_code, prestazione_desc, status, doctor_unit, address
    """

    iso_date: str
    time: str
    struttura: str
    cap: str | None

    prestazione_code: str
    prestazione_desc: str
    status: str
    doctor_unit: str | None
    address: str | None

    @property
    def slot_key(self) -> str:
        """Stable dedup identity: SHA-256 of the normalized key tuple.

        SHA-256 (not Python's salted ``hash()``) so the key is identical across
        processes and runs — the whole de-dup scheme depends on it. This is not
        a secret, so no keyed HMAC is needed here (that's only for CF, D29).
        """
        raw = _KEY_SEP.join([self.iso_date, self.time, self.struttura, self.cap or ""])
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
