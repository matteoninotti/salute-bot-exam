"""Tests for the dead-man heartbeat primitives (D11).

The daemon emits a heartbeat each loop pass; an external checker (Phase 5) reads
it and broadcasts if it goes stale. These lock the primitives that checker uses —
the write/stale-check round-trip and the all-users broadcast — without the
external scheduling, which a dead daemon can't do for itself.
"""

import pytest
from cryptography.fernet import Fernet

from salutebot.crypto import Crypto
from salutebot.daemon import (
    HEARTBEAT_MAX_AGE,
    heartbeat_is_stale,
    notify_watcher_down,
    write_heartbeat,
)
from salutebot.models import Prestazione
from salutebot.store import Store

_PREST = Prestazione(code="8901.20", descrizione="VISITA UROLOGICA DI CONTROLLO", quantita=1)


class _FakeMailer:
    def __init__(self):
        self.sent = []

    def send(self, to_addr, content):
        self.sent.append((to_addr, content))


@pytest.fixture
def store():
    crypto = Crypto(Fernet.generate_key().decode("ascii"), "hmac-secret")
    with Store(":memory:", crypto) as s:
        yield s


# ----- heartbeat write / stale-check -----

def test_fresh_heartbeat_is_not_stale(tmp_path):
    path = str(tmp_path / "hb")
    write_heartbeat(path, now=1000.0)
    assert heartbeat_is_stale(path, now=1000.0 + HEARTBEAT_MAX_AGE - 1) is False


def test_old_heartbeat_is_stale(tmp_path):
    path = str(tmp_path / "hb")
    write_heartbeat(path, now=1000.0)
    assert heartbeat_is_stale(path, now=1000.0 + HEARTBEAT_MAX_AGE + 1) is True


def test_missing_heartbeat_is_stale(tmp_path):
    assert heartbeat_is_stale(str(tmp_path / "nope"), now=1000.0) is True


def test_heartbeat_write_is_atomic_leaves_no_temp(tmp_path):
    path = tmp_path / "hb"
    write_heartbeat(str(path), now=1000.0)
    assert path.exists()
    assert not (tmp_path / "hb.tmp").exists()  # temp renamed away


# ----- dead-man broadcast -----

def test_notify_watcher_down_emails_every_user(store):
    store.add_user("RSSMRA85T10A562S", "a@b.it")
    store.add_user("BNCLGU80A01L219T", "b@b.it")
    mailer = _FakeMailer()

    notify_watcher_down(store, mailer)

    assert {addr for addr, _ in mailer.sent} == {"a@b.it", "b@b.it"}
    assert all("temporaneamente sospeso" in c.subject for _, c in mailer.sent)


def test_notify_watcher_down_with_no_users_is_a_noop(store):
    mailer = _FakeMailer()
    notify_watcher_down(store, mailer)
    assert mailer.sent == []
