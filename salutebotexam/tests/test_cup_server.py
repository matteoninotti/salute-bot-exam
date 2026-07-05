"""Tests for CupData: NRE resolution, Faker slot generation, growth and expiry."""

import unittest
from datetime import date

from cup_server import _FACILITIES, CupData


class FakeClock:
    """A clock whose value is advanced manually, so growth/expiry are testable."""

    def __init__(self) -> None:
        """Start the clock at zero."""
        self.__now = 0.0

    def __call__(self) -> float:
        """Return the current fake time in seconds."""
        return self.__now

    def advance(self, seconds: float) -> None:
        """Move the clock forward."""
        self.__now += seconds


class TestResolve(unittest.TestCase):
    """NRE resolution against the two fixed services."""

    def setUp(self) -> None:
        """Build CupData with a controllable clock."""
        self.cup = CupData(frame_seconds=10, clock=FakeClock())

    def test_known_nre(self) -> None:
        """A known NRE resolves to its prestazione code."""
        self.assertEqual(self.cup.resolve_nre("010A31234500001")["code"], "8901.20")

    def test_unknown_nre(self) -> None:
        """An unknown NRE resolves to None."""
        self.assertIsNone(self.cup.resolve_nre("NONESISTE000000"))

    def test_unknown_code_has_no_slots(self) -> None:
        """An unknown prestazione code yields None."""
        self.assertIsNone(self.cup.slots_for("0000.0"))


class TestGeneration(unittest.TestCase):
    """Baseline count, growth per frame, generated fields, and 60s expiry."""

    def setUp(self) -> None:
        """Build CupData over a controllable clock (frame = 10s)."""
        self.clock = FakeClock()
        self.cup = CupData(frame_seconds=10, clock=self.clock)

    def test_first_fetch_returns_three_baseline(self) -> None:
        """The first fetch shows exactly three baseline slots."""
        self.assertEqual(len(self.cup.slots_for("8901.20")), 3)

    def test_one_more_slot_per_frame(self) -> None:
        """One extra slot becomes available each frame after the first fetch."""
        self.cup.slots_for("8901.20")  # anchors the code at t=0
        self.clock.advance(10)
        self.assertEqual(len(self.cup.slots_for("8901.20")), 4)

    def test_generated_fields(self) -> None:
        """A slot carries the five fields with plausible values."""
        slot = self.cup.slots_for("8901.20")[0]
        self.assertEqual(set(slot), {"date", "time", "struttura", "cap", "address"})
        self.assertIn(slot["struttura"], _FACILITIES)
        self.assertGreaterEqual(date.fromisoformat(slot["date"]), date.today())
        self.assertLessEqual(date.fromisoformat(slot["date"]), date(2027, 12, 31))

    def test_slots_expire_after_60_seconds(self) -> None:
        """With no new slots due, the baseline disappears once 60s pass."""
        clock = FakeClock()
        cup = CupData(frame_seconds=1000, clock=clock)  # frame huge: no growth
        self.assertEqual(len(cup.slots_for("8901.20")), 3)
        clock.advance(61)
        self.assertEqual(cup.slots_for("8901.20"), [])


class TestDeterminism(unittest.TestCase):
    """The fixed seed makes a fresh run reproduce the same slots."""

    def test_fixed_seed_repeats(self) -> None:
        """Two fresh generators produce identical baseline slots."""
        first = CupData(frame_seconds=10, clock=FakeClock()).slots_for("8901.20")
        second = CupData(frame_seconds=10, clock=FakeClock()).slots_for("8901.20")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
