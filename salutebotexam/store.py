"""The Store: the only place that runs SQL.

Everything above (daemon, CLI, web) goes through this class instead of touching
sqlite directly. The connection is private; timestamps are ISO strings so they
sort chronologically and stay unique down to the microsecond (which is what the
"new slot" rule relies on).
"""

import sqlite3
from collections import defaultdict
from datetime import datetime

from database import SCHEMA, get_connection
from models import Prestazione, Slot


def _now() -> str:
    """Return the current time as an ISO string (microsecond precision)."""
    return datetime.now().isoformat()


class Store:
    """Persistence over SQLite. The connection is private (encapsulation)."""

    def __init__(self, db_path: str | None = None) -> None:
        """Open the store.

        Args:
            db_path: path to the SQLite file; None uses config.DB_PATH. A path
                is passed by tests to use a throwaway database.
        """
        self.__conn = get_connection() if db_path is None else get_connection(db_path)
        # Ensure the tables exist (idempotent, CREATE ... IF NOT EXISTS) so any
        # process that opens the store first works without a separate init step.
        self.__conn.executescript(SCHEMA)
        self.__conn.commit()

    def close(self) -> None:
        """Close the underlying connection."""
        self.__conn.close()

    def __enter__(self) -> "Store":
        """Enter a ``with`` block, returning self."""
        return self

    def __exit__(self, *exc: object) -> None:
        """Close the connection when leaving a ``with`` block."""
        self.close()

    # ----- users -----

    def add_user(self, cf: str, email: str) -> None:
        """Insert a user; do nothing if the CF already exists.

        Args:
            cf: the user's codice fiscale (primary key).
            email: contact email.
        """
        self.__conn.execute(
            "INSERT INTO utenti (cf, email) VALUES (?, ?) "
            "ON CONFLICT(cf) DO NOTHING",
            (cf, email),
        )
        self.__conn.commit()

    def user_exists(self, cf: str) -> bool:
        """Return True if a user with this CF exists."""
        return self.__row("SELECT 1 FROM utenti WHERE cf = ?", (cf,)) is not None

    def get_email(self, cf: str) -> str | None:
        """Return the user's email, or None if the user is unknown."""
        row = self.__row("SELECT email FROM utenti WHERE cf = ?", (cf,))
        return row["email"] if row else None

    # ----- prestazioni -----

    def upsert_prestazione(self, prestazione: Prestazione) -> None:
        """Insert the prestazione, refreshing its description on conflict.

        Args:
            prestazione: the Prestazione to store.
        """
        self.__conn.execute(
            "INSERT INTO prestazioni (code, descrizione) VALUES (?, ?) "
            "ON CONFLICT(code) DO UPDATE SET descrizione = excluded.descrizione",
            (prestazione.code, prestazione.descrizione),
        )
        self.__conn.commit()

    # ----- targets (subscriptions) -----

    def add_target(self, cf: str, code: str, nre: str) -> None:
        """Subscribe a user to a prestazione; re-adding just updates the NRE.

        Args:
            cf: the subscribing user's CF.
            code: the prestazione code to watch.
            nre: that user's prescription number for it.
        """
        self.__conn.execute(
            "INSERT INTO targets (cf, code, nre) VALUES (?, ?, ?) "
            "ON CONFLICT(cf, code) DO UPDATE SET nre = excluded.nre",
            (cf, code, nre),
        )
        self.__conn.commit()

    def get_user_targets(self, cf: str) -> list[dict]:
        """Return the prestazioni a user follows.

        Args:
            cf: the user's CF.
        Returns:
            A list of dicts with keys code, descrizione, nre.
        """
        rows = self.__rows(
            "SELECT t.code, p.descrizione, t.nre "
            "FROM targets t JOIN prestazioni p ON p.code = t.code "
            "WHERE t.cf = ? ORDER BY t.code",
            (cf,),
        )
        return [dict(r) for r in rows]

    def watched_codes(self) -> list[str]:
        """Return every distinct prestazione code that has at least one subscriber."""
        rows = self.__rows("SELECT DISTINCT code FROM targets ORDER BY code", ())
        return [r["code"] for r in rows]

    # ----- slots -----

    def known_slot_keys(self, code: str) -> set[str]:
        """Return the set of slot keys already stored for a prestazione."""
        rows = self.__rows("SELECT slot_key FROM slots WHERE code = ?", (code,))
        return {r["slot_key"] for r in rows}

    def has_slots(self, code: str) -> bool:
        """Return True if any slot is stored for this prestazione."""
        return self.__row("SELECT 1 FROM slots WHERE code = ? LIMIT 1", (code,)) is not None

    def save_slot(self, code: str, slot: Slot, now: str | None = None) -> None:
        """Insert a newly-seen slot (first_seen = last_seen = now).

        Ignores the slot if its key is already stored for this prestazione.

        Args:
            code: prestazione the slot belongs to.
            slot: the Slot to store.
            now: ISO timestamp to stamp it with; defaults to the current time.
        """
        ts = now or _now()
        d = slot.to_dict()
        self.__conn.execute(
            "INSERT INTO slots (code, slot_key, date, time, struttura, cap, address, "
            "first_seen, last_seen) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(code, slot_key) DO NOTHING",
            (code, slot.key, d["date"], d["time"], d["struttura"], d["cap"],
             d["address"], ts, ts),
        )
        self.__conn.commit()

    def touch_slot(self, code: str, slot_key: str, now: str | None = None) -> None:
        """Bump last_seen on a slot that is still present.

        Args:
            code: prestazione the slot belongs to.
            slot_key: the slot's key.
            now: ISO timestamp; defaults to the current time.
        """
        ts = now or _now()
        self.__conn.execute(
            "UPDATE slots SET last_seen = ? WHERE code = ? AND slot_key = ?",
            (ts, code, slot_key),
        )
        self.__conn.commit()

    def slots_for_code(self, code: str) -> list[dict]:
        """Return all slots of one prestazione, each tagged with is_new.

        Args:
            code: the prestazione code.
        Returns:
            A list of slot dicts (see _mark_new for the is_new field).
        """
        rows = self.__rows(
            "SELECT code, date, time, struttura, cap, address, first_seen, last_seen "
            "FROM slots WHERE code = ? ORDER BY date, time",
            (code,),
        )
        return _mark_new([dict(r) for r in rows])

    def slots_for_user(self, cf: str) -> list[dict]:
        """Return all slots for the prestazioni a user follows.

        Args:
            cf: the user's CF.
        Returns:
            A list of slot dicts, each with its prestazione descrizione and an
            is_new flag, ordered by prestazione then date/time.
        """
        rows = self.__rows(
            "SELECT s.code, p.descrizione, s.date, s.time, s.struttura, s.cap, "
            "s.address, s.first_seen, s.last_seen "
            "FROM targets t "
            "JOIN slots s ON s.code = t.code "
            "JOIN prestazioni p ON p.code = t.code "
            "WHERE t.cf = ? ORDER BY s.code, s.date, s.time",
            (cf,),
        )
        return _mark_new([dict(r) for r in rows])

    # ----- richieste (registration queue + per-user history) -----

    def add_richiesta(self, cf: str, email: str | None, nre: str, now: str | None = None) -> int:
        """Stage a pending registration/add request.

        Args:
            cf: the requesting user's CF.
            email: contact email (None when an existing user adds a prestazione).
            nre: the prescription number to resolve.
            now: ISO timestamp; defaults to the current time.
        Returns:
            The id of the new request row.
        """
        ts = now or _now()
        cur = self.__conn.execute(
            "INSERT INTO richieste (cf, email, nre, status, requested_at) "
            "VALUES (?, ?, ?, 'pending', ?)",
            (cf, email, nre, ts),
        )
        self.__conn.commit()
        return cur.lastrowid

    def pending_richieste(self) -> list[dict]:
        """Return the requests still awaiting the daemon (status = 'pending').

        Returns:
            A list of dicts with keys id, cf, email, nre.
        """
        rows = self.__rows(
            "SELECT id, cf, email, nre FROM richieste WHERE status = 'pending' "
            "ORDER BY requested_at",
            (),
        )
        return [dict(r) for r in rows]

    def resolve_richiesta(self, rich_id: int, status: str, code: str | None = None,
                          descrizione: str | None = None, now: str | None = None) -> None:
        """Write the daemon's outcome back onto a request.

        Args:
            rich_id: the request id.
            status: 'ok' or 'invalid'.
            code: resolved prestazione code (on 'ok').
            descrizione: resolved description (on 'ok').
            now: ISO timestamp; defaults to the current time.
        """
        ts = now or _now()
        self.__conn.execute(
            "UPDATE richieste SET status = ?, code = ?, descrizione = ?, resolved_at = ? "
            "WHERE id = ?",
            (status, code, descrizione, ts, rich_id),
        )
        self.__conn.commit()

    def get_richiesta(self, rich_id: int) -> dict | None:
        """Return one request row by id (the client polls this), or None."""
        row = self.__row("SELECT * FROM richieste WHERE id = ?", (rich_id,))
        return dict(row) if row else None

    def history_for_user(self, cf: str) -> list[dict]:
        """Return a user's request history, most recent first.

        Args:
            cf: the user's CF.
        Returns:
            A list of request dicts (id, nre, code, descrizione, status,
            requested_at, resolved_at).
        """
        rows = self.__rows(
            "SELECT id, nre, code, descrizione, status, requested_at, resolved_at "
            "FROM richieste WHERE cf = ? ORDER BY requested_at DESC",
            (cf,),
        )
        return [dict(r) for r in rows]

    # ----- internal query helpers -----

    def __row(self, sql: str, params: tuple) -> sqlite3.Row | None:
        """Run a query and return the first row (or None)."""
        return self.__conn.execute(sql, params).fetchone()

    def __rows(self, sql: str, params: tuple) -> list[sqlite3.Row]:
        """Run a query and return all rows."""
        return self.__conn.execute(sql, params).fetchall()


def _mark_new(rows: list[dict]) -> list[dict]:
    """Tag each slot row with an is_new flag (mutates and returns the rows).

    A slot is "new" when its first_seen is the newest for its prestazione AND
    that value differs from the oldest one. So a freshly-baselined set (all rows
    sharing one timestamp) is never highlighted, but a later-appearing slot is.

    Args:
        rows: slot dicts, each with 'code' and 'first_seen'.
    Returns:
        The same list, with an added boolean 'is_new' on every row.
    """
    firsts: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        firsts[r["code"]].append(r["first_seen"])
    newest = {code: max(vals) for code, vals in firsts.items()}
    oldest = {code: min(vals) for code, vals in firsts.items()}
    for r in rows:
        code = r["code"]
        r["is_new"] = r["first_seen"] == newest[code] and newest[code] != oldest[code]
    return rows
