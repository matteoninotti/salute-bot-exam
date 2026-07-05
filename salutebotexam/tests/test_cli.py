"""Tests for the CLI flows, with an injected store and fake I/O."""

import os
import tempfile
import unittest

from cli import CLI
from store import Store


class FakeIO:
    """Scripted input answers and captured output lines."""

    def __init__(self, answers: list) -> None:
        """Queue the answers the CLI will read, in order."""
        self.__answers = list(answers)
        self.lines: list = []

    def read(self, prompt: str = "") -> str:
        """Return the next scripted answer."""
        return self.__answers.pop(0)

    def write(self, text: str = "") -> None:
        """Capture a printed line."""
        self.lines.append(text)

    def sleep(self, seconds: float) -> None:
        """Do not actually wait during tests."""

    def output(self) -> str:
        """Return everything the CLI printed, joined."""
        return "\n".join(self.lines)


class CliTestCase(unittest.TestCase):
    """Base case: a CLI over a throwaway store with scripted I/O."""

    def setUp(self) -> None:
        """Open a Store on a temporary database file."""
        handle, self.path = tempfile.mkstemp(suffix=".db")
        os.close(handle)
        self.store = Store(self.path)

    def tearDown(self) -> None:
        """Close the Store and delete the temporary file."""
        self.store.close()
        os.remove(self.path)

    def _cli(self, answers: list) -> tuple:
        """Build a CLI wired to a fresh FakeIO; return both."""
        io = FakeIO(answers)
        return CLI(self.store, read=io.read, write=io.write, sleep=io.sleep), io


class TestRegister(CliTestCase):
    """Registration stages a richiesta (or rejects bad input)."""

    def test_register_stages_a_richiesta(self) -> None:
        """A valid CF + NRE stages one pending request."""
        cli, io = self._cli(["RSSMRA80A01H501U", "010A31234500001"])
        cli.register()
        pending = self.store.pending_richieste()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["cf"], "RSSMRA80A01H501U")
        self.assertIn("Richiesta inviata", io.output())

    def test_register_rejects_bad_cf(self) -> None:
        """An invalid CF stages nothing and reports the error."""
        cli, io = self._cli(["BADCF"])
        cli.register()
        self.assertEqual(self.store.pending_richieste(), [])
        self.assertIn("CF non valido", io.output())


class TestReads(CliTestCase):
    """Slots and history reads for a CF passed on the command line."""

    def test_slots_unknown_user(self) -> None:
        """A valid CF with no user is reported as unknown."""
        cli, io = self._cli([])
        cli.slots("RSSMRA80A01H501U")
        self.assertIn("Nessun utente", io.output())

    def test_history_shows_requests(self) -> None:
        """A user's staged request appears in the history listing."""
        self.store.add_richiesta("RSSMRA80A01H501U", "010A31234500001")
        cli, io = self._cli([])
        cli.history("RSSMRA80A01H501U")
        self.assertIn("Cronologia", io.output())


if __name__ == "__main__":
    unittest.main()
