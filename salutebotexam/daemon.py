"""The watcher daemon: the client half of the client/server pair.

A background loop that, every POLL_INTERVAL seconds:
  1. resolves any pending registration requests (looks the NRE up on the CUP
     server, creates the user/subscription, baselines the current slots);
  2. sweeps every watched prestazione, saving newly-appeared slots.

It is the only part of the app that talks to the CUP server. Run it in its own
terminal:  python daemon.py
"""

import time
from datetime import datetime

from config import POLL_INTERVAL
from cup_client import CupClient, CupError
from detector import detect_new_slots
from store import Store


def _now() -> str:
    """Return the current time as an ISO string."""
    return datetime.now().isoformat()


class Daemon:
    """Owns a Store and a CupClient (both private). Both are injectable for tests."""

    def __init__(self, store: Store | None = None, client: CupClient | None = None,
                 poll_interval: float = POLL_INTERVAL) -> None:
        """Build the daemon.

        Args:
            store: the Store to use; None creates the default one.
            client: the CupClient to use; None creates the default one.
            poll_interval: seconds to wait between cycles.
        """
        self.__store = store if store is not None else Store()
        self.__client = client if client is not None else CupClient()
        self.__poll_interval = poll_interval

    # ----- registration lane -----

    def resolve_registrations(self) -> None:
        """Resolve every pending registration request left by the clients."""
        for req in self.__store.pending_richieste():
            self.__resolve_one(req)

    def __resolve_one(self, req: dict) -> None:
        """Resolve a single pending request.

        Args:
            req: a dict with keys id, cf, nre (from pending_richieste).
        """
        rid, cf, nre = req["id"], req["cf"], req["nre"]
        try:
            prestazione = self.__client.resolve_prestazione(nre)
            reachable = True
        except CupError:
            prestazione = None
            reachable = False
        if not reachable:
            # Leave it pending and try again next loop (the server may be down).
            print(f"[daemon] richiesta {rid}: CUP non raggiungibile, riprovo dopo")
        elif prestazione is None:
            self.__store.resolve_richiesta(rid, "invalid")
            print(f"[daemon] richiesta {rid}: NRE non valido")
        else:
            self.__store.upsert_prestazione(prestazione)
            # Brand-new prestazione: record its current slots as already-seen so the
            # user is not "alerted" for slots that existed before they subscribed.
            if not self.__store.has_slots(prestazione.code):
                self.__baseline_slots(prestazione.code)
            self.__store.add_user(cf)
            self.__store.add_target(cf, prestazione.code, nre)
            self.__store.resolve_richiesta(rid, "ok", prestazione.code, prestazione.descrizione)
            print(f"[daemon] richiesta {rid}: {cf} ora segue "
                  f"{prestazione.code} - {prestazione.descrizione}")

    def __baseline_slots(self, code: str) -> None:
        """Record a brand-new prestazione's current slots as already-seen.

        Args:
            code: the prestazione code to baseline.
        """
        try:
            slots = self.__client.fetch_slots(code)
        except CupError:
            slots = []
        now = _now()
        for slot in slots:
            self.__store.save_slot(code, slot, now)

    # ----- watching lane -----

    def sweep(self) -> None:
        """Run one pass over every watched prestazione."""
        for code in self.__store.watched_codes():
            self.__check_code(code)

    def __check_code(self, code: str) -> None:
        """Check one prestazione: fetch, detect new slots, save them.

        Args:
            code: the prestazione code to check.
        """
        try:
            slots = self.__client.fetch_slots(code)
        except CupError:
            slots = None
        if slots is None:
            print(f"[daemon] {code}: CUP non raggiungibile")
        else:
            now = _now()
            new_slots = detect_new_slots(self.__store, code, slots, now)
            for slot in new_slots:
                self.__store.save_slot(code, slot, now)
            if new_slots:
                print(f"[daemon] {code}: {len(new_slots)} nuovo/i posto/i "
                      f"(totale disponibili: {len(slots)})")
            else:
                print(f"[daemon] {code}: nessun nuovo posto (totale: {len(slots)})")

    # ----- the loop -----

    def tick(self) -> None:
        """Run one full cycle: resolve registrations, then sweep."""
        self.resolve_registrations()
        if self.__store.watched_codes():
            self.sweep()
        else:
            print("[daemon] nessun utente da servire, in attesa...")

    def run(self) -> None:
        """Loop until interrupted (Ctrl-C)."""
        print(f"[daemon] avviato — controllo ogni {self.__poll_interval}s. "
              "Premi Ctrl-C per fermare.")
        try:
            while True:
                self.tick()
                time.sleep(self.__poll_interval)
        except KeyboardInterrupt:
            print("\n[daemon] fermato.")


def main() -> None:
    """Create and run the daemon."""
    Daemon().run()


if __name__ == "__main__":
    main()
