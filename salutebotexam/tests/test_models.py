"""Tests for the domain models (Slot, Prestazione)."""

import unittest

from models import Prestazione, Slot


class TestSlot(unittest.TestCase):
    """The Slot natural key and dict round-trip."""

    def test_key_is_stable_for_same_fields(self) -> None:
        """Two slots with identical key fields share one key."""
        a = Slot("2026-07-14", "08:30", "OSPEDALE", "10100", "Via A 1")
        b = Slot("2026-07-14", "08:30", "OSPEDALE", "10100", "Via A 1")
        self.assertEqual(a.key, b.key)

    def test_address_is_excluded_from_key(self) -> None:
        """A different address alone does not change the key."""
        a = Slot("2026-07-14", "08:30", "OSPEDALE", "10100", "Via A 1")
        b = Slot("2026-07-14", "08:30", "OSPEDALE", "10100", "Via Diversa 9")
        self.assertEqual(a.key, b.key)

    def test_different_time_changes_key(self) -> None:
        """A different appointment time yields a different key."""
        a = Slot("2026-07-14", "08:30", "OSPEDALE", "10100", "Via A 1")
        b = Slot("2026-07-14", "09:00", "OSPEDALE", "10100", "Via A 1")
        self.assertNotEqual(a.key, b.key)

    def test_dict_round_trip(self) -> None:
        """to_dict / from_dict rebuilds an equivalent slot."""
        original = Slot("2026-07-14", "08:30", "OSPEDALE", "10100", "Via A 1")
        rebuilt = Slot.from_dict(original.to_dict())
        self.assertEqual(original.key, rebuilt.key)
        self.assertEqual(rebuilt.address, "Via A 1")


class TestPrestazione(unittest.TestCase):
    """The Prestazione getters and dict round-trip."""

    def test_getters(self) -> None:
        """The code and descrizione are exposed read-only."""
        p = Prestazione("8901.20", "VISITA UROLOGICA")
        self.assertEqual(p.code, "8901.20")
        self.assertEqual(p.descrizione, "VISITA UROLOGICA")

    def test_dict_round_trip(self) -> None:
        """to_dict / from_dict rebuilds an equivalent prestazione."""
        p = Prestazione("8901.20", "VISITA UROLOGICA")
        q = Prestazione.from_dict(p.to_dict())
        self.assertEqual(q.code, p.code)
        self.assertEqual(q.descrizione, p.descrizione)


if __name__ == "__main__":
    unittest.main()
