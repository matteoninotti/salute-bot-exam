"""Tests for the CupData slot logic (NRE resolution + wall-clock growth)."""

import unittest

from config import FIXTURES_PATH
from cup_server import CupData


class FakeClock:
    """A clock whose value is advanced manually, so growth is testable."""

    def __init__(self) -> None:
        """Start the clock at zero."""
        self.__now = 0.0

    def __call__(self) -> float:
        """Return the current fake time in seconds."""
        return self.__now

    def advance(self, seconds: float) -> None:
        """Move the clock forward."""
        self.__now += seconds


class TestCupData(unittest.TestCase):
    """NRE resolution and the baseline + one-slot-per-frame growth."""

    def setUp(self) -> None:
        """Build CupData over the fixtures with a controllable clock."""
        self.clock = FakeClock()
        self.cup = CupData(FIXTURES_PATH, frame_seconds=10, clock=self.clock)

    def test_resolve_known_nre(self) -> None:
        """A known NRE resolves to its prestazione code."""
        self.assertEqual(self.cup.resolve_nre("010A31234500001")["code"], "8901.20")

    def test_resolve_unknown_nre(self) -> None:
        """An unknown NRE resolves to None."""
        self.assertIsNone(self.cup.resolve_nre("NONESISTE000000"))

    def test_unknown_code_has_no_slots(self) -> None:
        """An unknown prestazione code yields None."""
        self.assertIsNone(self.cup.slots_for("0000.0"))

    def test_first_fetch_returns_baseline(self) -> None:
        """The first fetch shows exactly the baseline slots."""
        self.assertEqual(len(self.cup.slots_for("8901.20")), 3)

    def test_one_more_slot_per_frame(self) -> None:
        """One extra slot becomes visible each frame after the first fetch."""
        self.cup.slots_for("8901.20")  # anchors the code at t=0
        self.clock.advance(10)
        self.assertEqual(len(self.cup.slots_for("8901.20")), 4)


if __name__ == "__main__":
    unittest.main()
