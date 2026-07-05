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
            pass
        elif self.__store.user_exists(cf):
            self.__write("Sei gia' registrato. Usa 'add' per seguire un'altra prestazione.")
        else:
            email = self.__read("Email per le notifiche: ").strip()
            if not valid_email(email):
                self.__write("Email non valida. Nulla e' stato salvato.")
            else:
                nre = self.__ask_nre()
                if nre is not None:
                    self.__submit(cf, email, nre)

    def add(self) -> None:
        """Add another prestazione for an already-registered user."""
        cf = self.__ask_cf()
        if cf is None:
            pass
        elif not self.__store.user_exists(cf):
            self.__write("Nessun utente con questo CF. Usa 'register' per registrarti.")
        else:
            nre = self.__ask_nre()
            if nre is not None:
                self.__submit(cf, None, nre)

    def slots(self, cf: str | None = None) -> None:
        """Print the current slots for the prestazioni a user follows."""
        cf = self.__resolve_cf(cf)
        if cf is not None:
            rows = self.__store.slots_for_user(cf)
            if not rows:
                self.__write("Nessun posto disponibile per ora per le prestazioni che segui.")
            else:
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
        if cf is not None:
            rows = self.__store.history_for_user(cf)
            if not rows:
                self.__write("Nessuna richiesta nella cronologia.")
            else:
                esito = {"ok": "ok", "invalid": "NRE non valido", "pending": "in attesa"}
                self.__write("Cronologia richieste:")
                for row in rows:
                    what = f"{row['descrizione']} ({row['code']})" if row["code"] else "-"
                    stato = esito.get(row["status"], row["status"])
                    self.__write(f"  {row['requested_at'][:19]} | {stato} | {what}")

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
        req = self.__store.get_richiesta(rich_id)
        tries = 0
        while req["status"] == "pending" and tries < _POLL_TRIES:
            self.__sleep(_POLL_WAIT)
            req = self.__store.get_richiesta(rich_id)
            tries += 1
        return req

    def __ask_cf(self) -> str | None:
        """Prompt for a CF and validate it; return the normalised CF or None."""
        cf = self.__read("Codice Fiscale: ").strip().upper()
        result = None
        if valid_cf(cf):
            result = cf
        else:
            self.__write("Formato CF non valido (attesi 16 caratteri alfanumerici).")
        return result

    def __ask_nre(self) -> str | None:
        """Prompt for an NRE and validate it; return the normalised NRE or None."""
        nre = self.__read("NRE (numero ricetta, 15 caratteri): ").strip().upper()
        result = None
        if valid_nre(nre):
            result = nre
        else:
            self.__write("Formato NRE non valido (attesi 15 caratteri alfanumerici).")
        return result

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
        result = None
        if not valid_cf(cf):
            self.__write("Formato CF non valido.")
        elif require_user and not self.__store.user_exists(cf):
            self.__write("Nessun utente con questo CF. Usa 'register' per registrarti.")
        else:
            result = cf
        return result


def _run(cli: CLI, command: str, cf: str | None) -> None:
    """Dispatch the parsed command to the matching CLI method.

    Args:
        cli: the CLI instance to drive.
        command: the sub-command name (register/add/slots/history).
        cf: the optional codice fiscale argument (slots/history).
    """
    if command == "register":
        cli.register()
    elif command == "add":
        cli.add()
    elif command == "slots":
        cli.slots(cf)
    elif command == "history":
        cli.history(cf)
    else:
        print("Uso: python cli.py [register | add | slots [CF] | history [CF]]")


def main() -> None:
    """Read the command from sys.argv and run it."""
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    cf = sys.argv[2] if len(sys.argv) > 2 else None
    store = Store()
    try:
        _run(CLI(store), command, cf)
    finally:
        store.close()


if __name__ == "__main__":
    main()
