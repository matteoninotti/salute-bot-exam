"""The watcher daemon — the long-running Service (D21) that scrapes and alerts.

This module currently provides the **single-instance guard** (D27); the
self-clocking serial loop, representative-NRE rotation, robustness, and
`--check-now`/registration serving land on top of it in later Phase 3 modules.

Single-instance guard (D27): the daemon takes an **exclusive, non-blocking
`flock`** on a lockfile at startup and refuses to start if the lock is already
held. This is a *kernel-owned* lock tied to the open file description, so it
**auto-releases on any exit — crash included** — with no stale-PID-file problem.
It composes with systemd (`Restart=always`, one instance, D21): even a stray
manual launch alongside the managed service cannot spawn a second competing
scraper, which is what keeps single-flight structural (D27).
"""

import fcntl
import os
from contextlib import contextmanager

_DEFAULT_LOCK_PATH = "/tmp/salute-bot.lock"


class DaemonAlreadyRunningError(RuntimeError):
    """Raised when the single-instance `flock` is already held by another daemon."""


@contextmanager
def single_instance_lock(lock_path: str = _DEFAULT_LOCK_PATH):
    """Hold an exclusive `flock` for the duration of the `with` block (D27).

    Raises `DaemonAlreadyRunningError` immediately (non-blocking) if another holder
    exists. The lock is released when the block exits — the fd is closed in
    `finally`, and the kernel also drops it on process death, so no cleanup of the
    lockfile itself is needed (its mere existence is not the lock; the `flock` is).
    """
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as err:
        os.close(fd)
        raise DaemonAlreadyRunningError(
            f"another salute-bot daemon already holds {lock_path} — refusing to "
            "start a second scraper (D27)."
        ) from err
    try:
        yield
    finally:
        os.close(fd)  # releases the flock (kernel would too, on any exit)
