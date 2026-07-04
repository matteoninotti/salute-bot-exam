"""Tests for the terminal CLI management surface (D5/D14/D27/D35).

Drives `cli.main` with an injected in-memory Store and scripted `read`/`write`,
so the whole flow is exercised without a TTY. Covers only the no-scrape commands
the CLI owns (D27); new-user registration is deferred and asserted to say so.
"""

import pytest
from cryptography.fernet import Fernet

from salutebot.cli import main
from salutebot.crypto import Crypto
from salutebot.models import Prestazione, Slot
from salutebot.store import Store

_CF = "RSSMRA85T10A562S"
_CF2 = "BNCLGU80A01L219T"
_UNREGISTERED = "VRDLGU90A01L219T"
_CODE = "8901.20"
_PREST = Prestazione(code=_CODE, descrizione="VISITA UROLOGICA DI CONTROLLO", quantita=1)
_PREST2 = Prestazione(code="7001.10", descrizione="ECOGRAFIA", quantita=1)


def _slot():
    return Slot(
        iso_date="2026-06-22", time="16:00", struttura="POLIAMBULATORIO MONGINEVRO",
        cap="10141", prestazione_code=_CODE, prestazione_desc="VISITA UROLOGICA DI CONTROLLO",
        status="PRENOTABILE", doctor_unit="UROLOGIA", address="Via Monginevro 130, 10141",
    )


def _scripted(*responses):
    """A fake `read` that returns the given answers in order."""
    it = iter(responses)
    return lambda _prompt="": next(it)


class _Writer:
    """A fake `write` that captures all output as one searchable string."""

    def __init__(self):
        self.lines: list[str] = []

    def __call__(self, msg=""):
        self.lines.append(str(msg))

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


@pytest.fixture
def store():
    crypto = Crypto(Fernet.generate_key().decode("ascii"), "hmac-secret")
    with Store(":memory:", crypto) as s:
        s.add_user(_CF, "a@b.it")
        s.add_target(_CF, _PREST, "1111111111111111")
        yield s


def _run(store, argv, read=None):
    out = _Writer()
    main(argv, store=store, read=read or _scripted(), write=out)
    return out.text


# ----- login / -u -----

def test_login_shows_watched_prestazioni(store):
    text = _run(store, ["-u", _CF])
    assert _CODE in text and "VISITA UROLOGICA" in text
    assert "a@b.it" in text


def test_login_unknown_cf_is_rejected(store):
    text = _run(store, ["-u", _UNREGISTERED])
    assert "No user found" in text


def test_login_invalid_cf_format_is_rejected(store):
    text = _run(store, ["-u", "not-a-cf"])
    assert "CF format invalid" in text


def test_login_prompts_when_cf_omitted(store):
    text = _run(store, ["-u"], read=_scripted(_CF))
    assert _CODE in text


# ----- --list -----

def test_list_shows_slots(store):
    store.record_new_slots(_CODE, [_slot()], now=1000.0)
    text = _run(store, ["-u", _CF, "--list"])
    assert "2026-06-22" in text and "MONGINEVRO" in text


def test_list_empty_is_friendly(store):
    text = _run(store, ["-u", _CF, "--list"])
    assert "No slots found yet" in text


# ----- --disable (menu, D35) -----

def test_disable_menu_deactivates_picked_target(store):
    store.add_target(_CF, _PREST2, "2222222222222222")
    text = _run(store, ["-u", _CF, "--disable"], read=_scripted("1"))
    assert "Disabled notifications" in text
    states = {t["code"]: t["active"] for t in store.get_user_targets(_CF)}
    # Targets are ordered by code; "7001.10" sorts before "8901.20".
    assert states["7001.10"] == 0
    assert states["8901.20"] == 1


def test_disable_menu_cancel_changes_nothing(store):
    _run(store, ["-u", _CF, "--disable"], read=_scripted(""))
    assert store.get_user_targets(_CF)[0]["active"] == 1


def test_disable_menu_rejects_out_of_range(store):
    text = _run(store, ["-u", _CF, "--disable"], read=_scripted("9"))
    assert "Not a valid choice" in text
    assert store.get_user_targets(_CF)[0]["active"] == 1


# ----- --disable-all -----

def test_disable_all_turns_off_every_target(store):
    store.add_target(_CF, _PREST2, "2222222222222222")
    _run(store, ["-u", _CF, "--disable-all"])
    assert all(t["active"] == 0 for t in store.get_user_targets(_CF))


# ----- --delete-user (D35 confirm) -----

def test_delete_user_requires_matching_cf(store):
    text = _run(store, ["-u", _CF, "--delete-user"], read=_scripted(_CF))
    assert "permanently deleted" in text
    assert store.user_exists(_CF) is False


def test_delete_user_aborts_on_cf_mismatch(store):
    text = _run(store, ["-u", _CF, "--delete-user"], read=_scripted(_CF2))
    assert "nothing was deleted" in text
    assert store.user_exists(_CF) is True


# ----- --check-now (D24/D26) -----

def _boom_sleep(_seconds):
    raise AssertionError("check-now must not block while on cooldown")


def test_check_now_queues_then_prints_results_when_served(store):
    store.record_new_slots(_CODE, [_slot()], now=900.0)  # slots already present
    out = _Writer()

    # A stand-in daemon: the first block-poll sleep marks the request complete, so
    # the CLI unblocks on its next check and prints the user's slots (D24).
    def fake_sleep(_seconds):
        store.mark_checknow_done(store._Store__crypto.hash_cf(_CF), now=1001.0)

    main(["-u", _CF, "--check-now"], store=store, read=_scripted(), write=out,
         clock=lambda: 1000.0, sleep=fake_sleep)

    assert "queued" in out.text.lower()
    assert "2026-06-22" in out.text and "MONGINEVRO" in out.text  # results after completion
    assert store._Store__conn.execute(
        "SELECT checknow_requested_at FROM users WHERE cf_hash = ?",
        (store._Store__crypto.hash_cf(_CF),)).fetchone()[0] == 1000.0  # fire recorded


def test_check_now_on_cooldown_prints_only_remaining(store):
    store.accept_checknow(_CF, now=1000.0)  # a recent accepted fire
    out = _Writer()

    main(["-u", _CF, "--check-now"], store=store, read=_scripted(), write=out,
         clock=lambda: 1100.0, sleep=_boom_sleep)  # 100s later -> 200s remaining

    assert "cooldown" in out.text.lower() and "200s" in out.text
    assert "queued" not in out.text.lower()  # rejected: no request, no block (D24)


# ----- registration (deferred, D27) -----

def test_new_user_registration_is_deferred(store):
    text = _run(store, [], read=_scripted(_UNREGISTERED))
    assert "isn't available yet" in text


def test_bare_invocation_existing_user_shows_menu(store):
    text = _run(store, [], read=_scripted(_CF))
    assert "Welcome back" in text and _CODE in text
