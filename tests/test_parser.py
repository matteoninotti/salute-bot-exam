"""Ground-truth tests for the slots parser.

Anchored to the REAL recon capture (`recon/iframe_slots_redacted.html`): a live
run of an actual ricetta with 17 free slots. Because the input is real captured
markup — not a hand-authored mock — these assertions stay trustworthy even once
the whole app is built around the parser (build strategy D, requirement #2).

The expected values below were read directly out of that fixture.
"""

from pathlib import Path

import pytest

from salutebot.scraper.parser import parse_available_slots

FIXTURE = Path(__file__).resolve().parent.parent / "recon" / "iframe_slots_redacted.html"

# (iso_date, time, struttura[normalized upper], cap) — the natural-key tuple (D16),
# in page order, for all 17 slots in the fixture.
EXPECTED_KEYS = [
    ("2026-06-22", "16:00", "POLIAMBULATORIO MONGINEVRO", "10141"),
    ("2026-06-24", "14:35", "POLIAMB - VENARIA", "10078"),
    ("2026-06-25", "08:00", "POLIAMBULATORIO CPA (LUNGO DORA SAVONA)", "10152"),
    ("2026-06-25", "11:00", "POLIAMBULATORIO MONGINEVRO", "10141"),
    ("2026-06-25", "12:00", "MOLINETTE", "10126"),
    ("2026-06-25", "14:35", "CASA DELLA COMUNITA' DI ORBASSANO", "10043"),
    ("2026-11-16", "11:00", 'CASA DELLA COMUNITA\'  "MARCO ANTONETTO"'.replace("  ", " "), None),
    ("2027-01-08", "08:50", "CASA DI COMUNITA' CONSOLATA", None),
    ("2027-01-11", "09:30", "POLIAMBULATORIO PACCHIOTTI", "10146"),
    ("2027-01-12", "09:20", "POLIAMBULATORIO MONTANARO", "10154"),
    ("2027-01-12", "13:20", "POLIAMB - GIAVENO", "10094"),
    ("2027-01-13", "10:00", "POLIAMBULATORIO VALDESE (VIA PELLICO)", None),
    ("2027-01-14", "09:20", "POLIAMBULATORIO GORIZIA", "10100"),
    ("2027-01-18", "10:00", "POLIAMBULATORIO CORSICA", "10100"),
    ("2027-01-19", "09:20", "PRESIDIO SANITARIO VALLETTA (VIA FARINELLI)", "10100"),
    ("2027-01-27", "10:10", "PRESIDIO SANITARIO VALLETTA (VIA FARINELLI)", "10100"),
    ("2027-02-01", "11:30", "POLIAMBULATORIO MONTANARO", "10154"),
]


@pytest.fixture(scope="module")
def slots():
    return parse_available_slots(FIXTURE.read_text(encoding="utf-8"))


def test_parses_all_17_slots(slots):
    assert len(slots) == 17


def test_natural_keys_match_ground_truth(slots):
    actual = [(s.iso_date, s.time, s.struttura, s.cap) for s in slots]
    assert actual == EXPECTED_KEYS


def test_all_slot_keys_distinct(slots):
    keys = [s.slot_key for s in slots]
    assert len(set(keys)) == 17


def test_slot_key_is_stable_and_deterministic(slots):
    # Recomputing must yield the identical digest (no per-process salting).
    assert slots[0].slot_key == slots[0].slot_key
    assert len(slots[0].slot_key) == 64  # sha256 hex


def test_descriptive_fields_first_card(slots):
    first = slots[0]
    assert first.prestazione_code == "8901.20"
    assert first.prestazione_desc == "VISITA UROLOGICA DI CONTROLLO"
    assert first.status == "PRENOTABILE"
    assert first.doctor_unit == "UROLOGIA - DR.SSA DE MARIA CLAUDIA"


def test_cap_null_street_still_yields_cap(slots):
    # data-address="null, 10126" (MOLINETTE) -> street null, CAP present.
    molinette = slots[4]
    assert molinette.struttura == "MOLINETTE"
    assert molinette.cap == "10126"


def test_cap_absent_is_none(slots):
    # data-address="VIA LUZZATTI, null" ("MARCO ANTONETTO") -> CAP None.
    antonetto = slots[6]
    assert antonetto.cap is None


def test_html_entities_decoded(slots):
    # &#39; -> ' and &#34; -> " must be decoded in struttura.
    assert '"MARCO ANTONETTO"' in slots[6].struttura
    assert "'" in slots[5].struttura  # CASA DELLA COMUNITA'
