"""Command-line client.

The CLI never talks to the CUP server itself: to register (or add a
prestazione) it stages a request in the database and waits for the daemon to
resolve it. Listing slots and history are plain reads of the shared database.

Usage:
    python cli.py register        # new user: CF + email + NRE
    python cli.py add             # existing user: add another prestazione (CF + NRE)
    python cli.py slots [CF]      # current slots for the prestazioni you follow
    python cli.py history [CF]    # your request history
"""

import argparse
import sys
import time

from store import Store
from validation import valid_cf, valid_email, valid_nre

# How long the CLI waits for the daemon to resolve a staged request.
_POLL_TRIES = 30
_POLL_WAIT = 1.0


class CLI:
    """The command-line client. I/O is injected so the flows are testable."""

    def __init__(self, store: Store, read=input, write=print, sleep=time.sleep) -> None:
        """Build the CLI.

        Args:
            store: the shared Store.
            read: function used to read a line of input (default input).
            write: function used to print a line (default print).
            sleep: function used to wait between polls (default time.sleep).
        """
        self.__store = store
        self.__read = read
        self.__write = write
        self.__sleep = sleep

    # ----- commands -----

    def register(self) -> None:
        """Register a new user and their first prestazione (staged for the daemon)."""
        cf = self.__ask_cf()
        if cf is None:
            return
        if self.__store.user_exists(cf):
            self.__write("Sei gia' registrato. Usa 'add' per seguire un'altra prestazione.")
            return
        email = self.__read("Email per le notifiche: ").strip()
        if not valid_email(email):
            self.__write("Email non valida. Nulla e' stato salvato.")
            return
        nre = self.__ask_nre()
        if nre is None:
            return
        self.__submit(cf, email, nre)

    def add(self) -> None:
        """Add another prestazione for an already-registered user."""
        cf = self.__ask_cf()
        if cf is None:
            return
        if not self.__store.user_exists(cf):
            self.__write("Nessun utente con questo CF. Usa 'register' per registrarti.")
            return
        nre = self.__ask_nre()
        if nre is None:
            return
        self.__submit(cf, None, nre)

    def slots(self, cf: str | None = None) -> None:
        """Print the current slots for the prestazioni a user follows."""
        cf = self.__resolve_cf(cf)
        if cf is None:
            return
        rows = self.__store.slots_for_user(cf)
        if not rows:
            self.__write("Nessun posto disponibile per ora per le prestazioni che segui.")
            return
        current_code = None
        for row in rows:
            if row["code"] != current_code:
                current_code = row["code"]
                self.__write(f"\n{row['code']} - {row['descrizione']}")
            mark = "  >> NUOVO" if row["is_new"] else ""
            where = row["struttura"] or "?"
            if row["address"]:
                where = f"{where}, {row['address']}"
            self.__write(f"  {row['date']} {row['time']} - {where}{mark}")

    def history(self, cf: str | None = None) -> None:
        """Print a user's request history (works even for a rejected request)."""
        cf = self.__resolve_cf(cf, require_user=False)
        if cf is None:
            return
        rows = self.__store.history_for_user(cf)
        if not rows:
            self.__write("Nessuna richiesta nella cronologia.")
            return
        self.__write("Cronologia richieste:")
        for row in rows:
            esito = {"ok": "ok", "invalid": "NRE non valido", "pending": "in attesa"}
            what = f"{row['descrizione']} ({row['code']})" if row["code"] else "-"
            self.__write(f"  {row['requested_at'][:19]} | {esito.get(row['status'], row['status'])} | {what}")

    # ----- helpers -----

    def __submit(self, cf: str, email: str | None, nre: str) -> None:
        """Stage a request, wait for the daemon, and report the outcome."""
        rich_id = self.__store.add_richiesta(cf, email, nre)
        self.__write("Richiesta inviata al watcher, attendo la verifica della ricetta...")
        req = self.__poll(rich_id)
        if req["status"] == "pending":
            self.__write("Il watcher non ha ancora risposto. E' in esecuzione? "
                         "La richiesta resta in coda: riprova 'slots'/'history' piu' tardi.")
        elif req["status"] == "invalid":
            self.__write("La ricetta (NRE) non e' valida. Nulla e' stato salvato.")
        else:
            self.__write(f"Fatto: ora segui {req['descrizione']} ({req['code']}).")

    def __poll(self, rich_id: int) -> dict:
        """Poll a staged request until the daemon resolves it or we time out.

        Args:
            rich_id: the request id to watch.
        Returns:
            The request row (status may still be 'pending' on timeout).
        """
        for _ in range(_POLL_TRIES):
            req = self.__store.get_richiesta(rich_id)
            if req["status"] != "pending":
                return req
            self.__sleep(_POLL_WAIT)
        return self.__store.get_richiesta(rich_id)

    def __ask_cf(self) -> str | None:
        """Prompt for a CF and validate it; return the normalised CF or None."""
        cf = self.__read("Codice Fiscale: ").strip().upper()
        if not valid_cf(cf):
            self.__write("Formato CF non valido (attesi 16 caratteri alfanumerici).")
            return None
        return cf

    def __ask_nre(self) -> str | None:
        """Prompt for an NRE and validate it; return the normalised NRE or None."""
        nre = self.__read("NRE (numero ricetta, 15 caratteri): ").strip().upper()
        if not valid_nre(nre):
            self.__write("Formato NRE non valido (attesi 15 caratteri alfanumerici).")
            return None
        return nre

    def __resolve_cf(self, cf: str | None, require_user: bool = True) -> str | None:
        """Return a validated CF from the arg or a prompt.

        Args:
            cf: the CF passed on the command line, or None to prompt.
            require_user: if True, the CF must belong to an existing user.
        Returns:
            The normalised CF, or None if invalid (or unknown when required).
        """
        if cf is None:
            cf = self.__read("Codice Fiscale: ").strip().upper()
        else:
            cf = cf.strip().upper()
        if not valid_cf(cf):
            self.__write("Formato CF non valido.")
            return None
        if require_user and not self.__store.user_exists(cf):
            self.__write("Nessun utente con questo CF. Usa 'register' per registrarti.")
            return None
        return cf


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with one sub-command per action."""
    parser = argparse.ArgumentParser(
        prog="salute-bot",
        description="Client CLI: registrati e controlla i posti disponibili.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("register", help="registra un nuovo utente (CF + email + NRE)")
    sub.add_parser("add", help="aggiungi un'altra prestazione (CF + NRE)")
    p_slots = sub.add_parser("slots", help="mostra i posti trovati")
    p_slots.add_argument("cf", nargs="?", help="codice fiscale (altrimenti richiesto)")
    p_hist = sub.add_parser("history", help="mostra la cronologia delle richieste")
    p_hist.add_argument("cf", nargs="?", help="codice fiscale (altrimenti richiesto)")
    return parser


def main(argv: list[str] | None = None) -> None:
    """Parse the command line and run the chosen command.

    Args:
        argv: argument list (defaults to sys.argv[1:]).
    """
    args = _build_parser().parse_args(sys.argv[1:] if argv is None else argv)
    store = Store()
    try:
        cli = CLI(store)
        if args.command == "register":
            cli.register()
        elif args.command == "add":
            cli.add()
        elif args.command == "slots":
            cli.slots(args.cf)
        elif args.command == "history":
            cli.history(args.cf)
    finally:
        store.close()


if __name__ == "__main__":
    main()
