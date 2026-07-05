"""The Store: the only place that runs SQL.

Everything above (daemon, CLI, web) goes through this class instead of touching
sqlite directly. The connection is private; timestamps are ISO strings so they
sort chronologically and stay unique down to the microsecond (which is what the
"new slot" rule relies on).
"""

from collections import defaultdict
from datetime import datetime

from database import get_connection
from models import Slot


def _now():
    """Current time as an ISO string (microsecond precision)."""
    return datetime.now().isoformat()


class Store:
    """Persistence over SQLite. The connection is private (encapsulation)."""

    def __init__(self, db_path=None):
        # get_connection defaults to config.DB_PATH; passing a path is for tests.
        self.__conn = get_connection() if db_path is None else get_connection(db_path)

    def close(self):
        self.__conn.close()

    # ----- users -----

    def add_user(self, cf, email):
        """Insert a user; do nothing if the CF already exists."""
        self.__conn.execute(
            "INSERT INTO utenti (cf, email) VALUES (?, ?) "
            "ON CONFLICT(cf) DO NOTHING",
            (cf, email),
        )
        self.__conn.commit()

    def user_exists(self, cf):
        return self.__row("SELECT 1 FROM utenti WHERE cf = ?", (cf,)) is not None

    def get_email(self, cf):
        row = self.__row("SELECT email FROM utenti WHERE cf = ?", (cf,))
        return row["email"] if row else None

    # ----- prestazioni -----

    def upsert_prestazione(self, prestazione):
        """Insert the prestazione, refreshing its description on conflict."""
        self.__conn.execute(
            "INSERT INTO prestazioni (code, descrizione) VALUES (?, ?) "
            "ON CONFLICT(code) DO UPDATE SET descrizione = excluded.descrizione",
            (prestazione.code, prestazione.descrizione),
        )
        self.__conn.commit()

    # ----- targets (subscriptions) -----

    def add_target(self, cf, code, nre):
        """Subscribe a user to a prestazione; re-adding just updates the NRE."""
        self.__conn.execute(
            "INSERT INTO targets (cf, code, nre) VALUES (?, ?, ?) "
            "ON CONFLICT(cf, code) DO UPDATE SET nre = excluded.nre",
            (cf, code, nre),
        )
        self.__conn.commit()

    def get_user_targets(self, cf):
        """The prestazioni a user follows: code, descrizione, nre."""
        rows = self.__rows(
            "SELECT t.code, p.descrizione, t.nre "
            "FROM targets t JOIN prestazioni p ON p.code = t.code "
            "WHERE t.cf = ? ORDER BY t.code",
            (cf,),
        )
        return [dict(r) for r in rows]

    def watched_codes(self):
        """Every distinct prestazione code that has at least one subscriber."""
        rows = self.__rows("SELECT DISTINCT code FROM targets ORDER BY code", ())
        return [r["code"] for r in rows]

    # ----- slots -----

    def known_slot_keys(self, code):
        rows = self.__rows("SELECT slot_key FROM slots WHERE code = ?", (code,))
        return {r["slot_key"] for r in rows}

    def has_slots(self, code):
        return self.__row("SELECT 1 FROM slots WHERE code = ? LIMIT 1", (code,)) is not None

    def save_slot(self, code, slot, now=None):
        """Insert a newly-seen slot (first_seen = last_seen = now). Ignores it if
        the same slot_key is already stored for this prestazione."""
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

    def touch_slot(self, code, slot_key, now=None):
        """Bump last_seen on a slot that is still present."""
        ts = now or _now()
        self.__conn.execute(
            "UPDATE slots SET last_seen = ? WHERE code = ? AND slot_key = ?",
            (ts, code, slot_key),
        )
        self.__conn.commit()

    def slots_for_code(self, code):
        """All slots of one prestazione, each tagged with is_new."""
        rows = self.__rows(
            "SELECT code, date, time, struttura, cap, address, first_seen, last_seen "
            "FROM slots WHERE code = ? ORDER BY date, time",
            (code,),
        )
        return _mark_new([dict(r) for r in rows])

    def slots_for_user(self, cf):
        """All slots for the prestazioni a user follows, each tagged with is_new
        and its prestazione description, ordered by prestazione then date/time."""
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

    def add_richiesta(self, cf, email, nre, now=None):
        """Stage a pending registration/add request; return its id."""
        ts = now or _now()
        cur = self.__conn.execute(
            "INSERT INTO richieste (cf, email, nre, status, requested_at) "
            "VALUES (?, ?, ?, 'pending', ?)",
            (cf, email, nre, ts),
        )
        self.__conn.commit()
        return cur.lastrowid

    def pending_richieste(self):
        """Requests still awaiting the daemon (status = 'pending')."""
        rows = self.__rows(
            "SELECT id, cf, email, nre FROM richieste WHERE status = 'pending' "
            "ORDER BY requested_at",
            (),
        )
        return [dict(r) for r in rows]

    def resolve_richiesta(self, rich_id, status, code=None, descrizione=None, now=None):
        """Write the daemon's outcome back onto a request (status ok/invalid)."""
        ts = now or _now()
        self.__conn.execute(
            "UPDATE richieste SET status = ?, code = ?, descrizione = ?, resolved_at = ? "
            "WHERE id = ?",
            (status, code, descrizione, ts, rich_id),
        )
        self.__conn.commit()

    def get_richiesta(self, rich_id):
        """One request row by id (the client polls this after staging)."""
        row = self.__row("SELECT * FROM richieste WHERE id = ?", (rich_id,))
        return dict(row) if row else None

    def history_for_user(self, cf):
        """A user's request history, most recent first."""
        rows = self.__rows(
            "SELECT id, nre, code, descrizione, status, requested_at, resolved_at "
            "FROM richieste WHERE cf = ? ORDER BY requested_at DESC",
            (cf,),
        )
        return [dict(r) for r in rows]

    # ----- internal query helpers -----

    def __row(self, sql, params):
        return self.__conn.execute(sql, params).fetchone()

    def __rows(self, sql, params):
        return self.__conn.execute(sql, params).fetchall()


def _mark_new(rows):
    """Tag each slot row with is_new.

    A slot is "new" when its first_seen is the newest for its prestazione AND
    that value differs from the oldest one. So a freshly-baselined set (all rows
    sharing one timestamp) is never highlighted, but a later-appearing slot is.
    """
    firsts = defaultdict(list)
    for r in rows:
        firsts[r["code"]].append(r["first_seen"])
    newest = {code: max(vals) for code, vals in firsts.items()}
    oldest = {code: min(vals) for code, vals in firsts.items()}
    for r in rows:
        code = r["code"]
        r["is_new"] = r["first_seen"] == newest[code] and newest[code] != oldest[code]
    return rows
