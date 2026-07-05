"""Tests for the Store (SQL persistence) against a temporary database."""

import os
import tempfile
import unittest

from models import Prestazione, Slot
from store import Store


class StoreTestCase(unittest.TestCase):
    """Base case: a fresh Store on a throwaway database file."""

    def setUp(self) -> None:
        """Open a Store on a temporary database file."""
        handle, self.path = tempfile.mkstemp(suffix=".db")
        os.close(handle)
        self.store = Store(self.path)

    def tearDown(self) -> None:
        """Close the Store and delete the temporary file."""
        self.store.close()
        os.remove(self.path)


class TestUsers(StoreTestCase):
    """Users are added once and looked up by CF."""

    def test_add_and_find_user(self) -> None:
        """A stored user is found and its email read back."""
        self.store.add_user("RSSMRA80A01H501U", "a@b.it")
        self.assertTrue(self.store.user_exists("RSSMRA80A01H501U"))
        self.assertEqual(self.store.get_email("RSSMRA80A01H501U"), "a@b.it")

    def test_unknown_user(self) -> None:
        """An unknown CF is reported missing."""
        self.assertFalse(self.store.user_exists("NOPE"))
        self.assertIsNone(self.store.get_email("NOPE"))


class TestTargets(StoreTestCase):
    """A target subscribes a user to a prestazione."""

    def setUp(self) -> None:
        """Seed one user and one prestazione for the subscription."""
        super().setUp()
        self.store.add_user("RSSMRA80A01H501U", "a@b.it")
        self.store.upsert_prestazione(Prestazione("8901.20", "VISITA"))

    def test_add_target_and_read(self) -> None:
        """A subscription is listed for the user and its code is watched."""
        self.store.add_target("RSSMRA80A01H501U", "8901.20", "010A31234500001")
        targets = self.store.get_user_targets("RSSMRA80A01H501U")
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0]["code"], "8901.20")
        self.assertEqual(self.store.watched_codes(), ["8901.20"])


class TestSlots(StoreTestCase):
    """Slots persist per prestazione and carry the is_new flag."""

    def setUp(self) -> None:
        """Seed the prestazione the slots belong to."""
        super().setUp()
        self.store.upsert_prestazione(Prestazione("8901.20", "VISITA"))

    def _slot(self, time: str) -> Slot:
        """Build a slot that differs only by its time."""
        return Slot("2026-07-14", time, "OSPEDALE", "10100", "Via A 1")

    def test_save_and_known_keys(self) -> None:
        """A saved slot is present and its key is known."""
        slot = self._slot("08:30")
        self.store.save_slot("8901.20", slot, "2026-07-01T00:00:00")
        self.assertTrue(self.store.has_slots("8901.20"))
        self.assertIn(slot.key, self.store.known_slot_keys("8901.20"))

    def test_baseline_not_new_but_later_slot_is(self) -> None:
        """A shared-timestamp baseline is never new; a later slot is."""
        for time in ("08:30", "09:00", "09:30"):
            self.store.save_slot("8901.20", self._slot(time), "2026-07-01T00:00:00")
        rows = self.store.slots_for_code("8901.20")
        self.assertTrue(all(not row["is_new"] for row in rows))
        self.store.save_slot("8901.20", self._slot("10:00"), "2026-07-01T00:01:00")
        new_rows = [row for row in self.store.slots_for_code("8901.20") if row["is_new"]]
        self.assertEqual(len(new_rows), 1)
        self.assertEqual(new_rows[0]["time"], "10:00")


class TestRichieste(StoreTestCase):
    """A richiesta is staged, resolved, and read back as history."""

    def test_lifecycle(self) -> None:
        """A pending request resolves to ok and appears in history."""
        rid = self.store.add_richiesta("RSSMRA80A01H501U", "a@b.it", "010A31234500001")
        pending = self.store.pending_richieste()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["id"], rid)
        self.store.resolve_richiesta(rid, "ok", "8901.20", "VISITA")
        req = self.store.get_richiesta(rid)
        self.assertEqual(req["status"], "ok")
        self.assertEqual(req["code"], "8901.20")
        self.assertEqual(self.store.pending_richieste(), [])
        self.assertEqual(len(self.store.history_for_user("RSSMRA80A01H501U")), 1)


if __name__ == "__main__":
    unittest.main()
