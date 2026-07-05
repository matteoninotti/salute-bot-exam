"""Tests for the shared format validation (CF and NRE)."""

import unittest

from validation import valid_cf, valid_nre


class TestValidation(unittest.TestCase):
    """CF and NRE are structural checks only (length + alphanumeric)."""

    def test_valid_cf_accepts_16_alnum(self) -> None:
        """A 16-character alphanumeric CF is accepted."""
        self.assertTrue(valid_cf("RSSMRA80A01H501U"))

    def test_valid_cf_rejects_wrong_length(self) -> None:
        """A CF that is not 16 characters is rejected."""
        self.assertFalse(valid_cf("RSSMRA80A01H501"))

    def test_valid_cf_rejects_symbols(self) -> None:
        """A CF with a non-alphanumeric character is rejected."""
        self.assertFalse(valid_cf("RSSMRA80A01H501-"))

    def test_valid_nre_accepts_15_alnum(self) -> None:
        """A 15-character alphanumeric NRE is accepted."""
        self.assertTrue(valid_nre("010A31234500001"))

    def test_valid_nre_rejects_wrong_length(self) -> None:
        """An NRE that is not 15 characters is rejected."""
        self.assertFalse(valid_nre("010A3123450000"))


if __name__ == "__main__":
    unittest.main()
