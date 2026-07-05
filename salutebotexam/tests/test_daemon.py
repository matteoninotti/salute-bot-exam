"""Tests for the daemon registration-resolve flow (with a fake CUP client)."""

import os
import tempfile
import unittest

from daemon import Daemon
from models import Prestazione, Slot
from store import Store


class FakeClient:
    """A stand-in CupClient: resolves one known NRE and returns fixed slots."""

    def resolve_prestazione(self, nre: str) -> Prestazione | None:
        """Resolve only the one known NRE, else None."""
        result = None
        if nre == "010A31234500001":
            result = Prestazione("8901.20", "VISITA")
        return result

    def fetch_slots(self, code: str) -> list[Slot]:
        """Return a single fixed slot for any code."""
        return [Slot("2026-07-14", "08:30", "OSPEDALE", "10100", "Via A 1")]


class TestDaemonResolve(unittest.TestCase):
    """Resolving a pending richiesta creates the user/target and marks it ok."""

    def setUp(self) -> None:
        """Open a temp Store and a Daemon driven by the fake client."""
        handle, self.path = tempfile.mkstemp(suffix=".db")
        os.close(handle)
        self.store = Store(self.path)
        self.daemon = Daemon(store=self.store, client=FakeClient())

    def tearDown(self) -> None:
        """Close the Store and delete the temporary file."""
        self.store.close()
        os.remove(self.path)

    def test_valid_registration_is_resolved(self) -> None:
        """A valid NRE creates the user + subscription and marks the request ok."""
        rid = self.store.add_richiesta("RSSMRA80A01H501U", "010A31234500001")
        self.daemon.resolve_registrations()
        req = self.store.get_richiesta(rid)
        self.assertEqual(req["status"], "ok")
        self.assertEqual(req["code"], "8901.20")
        self.assertTrue(self.store.user_exists("RSSMRA80A01H501U"))
        self.assertEqual(self.store.watched_codes(), ["8901.20"])

    def test_invalid_nre_is_marked_invalid(self) -> None:
        """An unknown NRE leaves no user and marks the request invalid."""
        rid = self.store.add_richiesta("RSSMRA80A01H501U", "999999999999999")
        self.daemon.resolve_registrations()
        self.assertEqual(self.store.get_richiesta(rid)["status"], "invalid")
        self.assertFalse(self.store.user_exists("RSSMRA80A01H501U"))


if __name__ == "__main__":
    unittest.main()
