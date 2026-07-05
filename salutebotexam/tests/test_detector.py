"""Tests for detect_new_slots (the new vs already-known split)."""

import os
import tempfile
import unittest

from detector import detect_new_slots
from models import Prestazione, Slot
from store import Store


class TestDetector(unittest.TestCase):
    """Detection returns only unknown slots and touches the known ones."""

    def setUp(self) -> None:
        """Open a temp Store with one prestazione and one known slot."""
        handle, self.path = tempfile.mkstemp(suffix=".db")
        os.close(handle)
        self.store = Store(self.path)
        self.store.upsert_prestazione(Prestazione("8901.20", "VISITA"))
        self.known = Slot("2026-07-14", "08:30", "OSPEDALE", "10100", "Via A 1")
        self.store.save_slot("8901.20", self.known, "2026-07-01T00:00:00")

    def tearDown(self) -> None:
        """Close the Store and delete the temporary file."""
        self.store.close()
        os.remove(self.path)

    def test_only_unknown_slots_are_returned(self) -> None:
        """A fresh slot is returned; the known one is not."""
        fresh = Slot("2026-07-15", "09:00", "OSPEDALE", "10100", "Via B 2")
        new_slots = detect_new_slots(self.store, "8901.20", [self.known, fresh])
        self.assertEqual([s.key for s in new_slots], [fresh.key])

    def test_known_slot_is_not_new_again(self) -> None:
        """A slot already stored is never returned as new."""
        new_slots = detect_new_slots(self.store, "8901.20", [self.known])
        self.assertEqual(new_slots, [])


if __name__ == "__main__":
    unittest.main()
