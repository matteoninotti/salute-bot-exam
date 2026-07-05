"""Low-level database helpers (the DAO layer).

Only this module knows how to open a connection and create the schema; the
Store class on top of it holds the actual queries. We use plain sqlite3 with
``sqlite3.Row`` so rows can be read by column name.
"""

import sqlite3

from config import DB_PATH

# The whole schema. CF and NRE are stored in clear text (exam simplification).
SCHEMA = """
CREATE TABLE IF NOT EXISTS utenti (
    cf     TEXT PRIMARY KEY,
    email  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prestazioni (
    code         TEXT PRIMARY KEY,
    descrizione  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS targets (
    cf    TEXT NOT NULL REFERENCES utenti(cf) ON DELETE CASCADE,
    code  TEXT NOT NULL REFERENCES prestazioni(code) ON DELETE CASCADE,
    nre   TEXT NOT NULL,
    PRIMARY KEY (cf, code)
);

CREATE TABLE IF NOT EXISTS slots (
    code        TEXT NOT NULL REFERENCES prestazioni(code) ON DELETE CASCADE,
    slot_key    TEXT NOT NULL,
    date        TEXT,
    time        TEXT,
    struttura   TEXT,
    cap         TEXT,
    address     TEXT,
    first_seen  TEXT,
    last_seen   TEXT,
    PRIMARY KEY (code, slot_key)
);

-- The request log. It is both the daemon's registration work-queue and the
-- per-user request history. A client inserts a row with status 'pending'; the
-- daemon looks the NRE up on the CUP server and fills in code/descrizione and
-- flips status to 'ok' or 'invalid'. email is NULL when an existing user adds
-- another prestazione (their email is already stored in utenti).
CREATE TABLE IF NOT EXISTS richieste (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    cf            TEXT NOT NULL,
    email         TEXT,
    nre           TEXT NOT NULL,
    code          TEXT,
    descrizione   TEXT,
    status        TEXT NOT NULL DEFAULT 'pending',
    requested_at  TEXT NOT NULL,
    resolved_at   TEXT
);
"""


def get_connection(db_path=DB_PATH):
    """Open a connection with row-by-name access and foreign keys on."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=DB_PATH):
    """Create every table if it does not exist yet."""
    conn = get_connection(db_path)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
