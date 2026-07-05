"""The mock CUP server: the "server" half of the client/server pair.

It stands in for the real Piemonte CUP website. It answers two HTTP requests:
what prestazione an NRE unlocks, and what slots a prestazione currently has.

The only fixed data are the two services and the NRE map; every slot is
generated on the fly with Faker (it_IT, fixed seed). Each service starts with 3
baseline slots and gains one more per FRAME_SECONDS (missed intervals are caught
up on the next request). A slot disappears 60 seconds after it is created, so the
watcher can observe both new slots appearing and old ones expiring.

Run:  python cup_server.py
"""

import time
from collections.abc import Callable
from datetime import date

from faker import Faker
from flask import Flask, jsonify, request
from flask.typing import ResponseReturnValue

from config import CUP_HOST, CUP_PORT, FRAME_SECONDS

# The only immutable server data: the two services and the NRE -> code map.
_PRESTAZIONI = {
    "8901.20": "VISITA UROLOGICA DI CONTROLLO",
    "8702.1": "ELETTROCARDIOGRAMMA",
}
_NRE_TO_CODE = {
    "010A31234500001": "8901.20",
    "020B45678900002": "8702.1",
}
# A small curated pool of real Turin-area facilities; Faker picks from it.
_FACILITIES = [
    "OSPEDALE MOLINETTE",
    "OSPEDALE MAURIZIANO",
    "OSPEDALE SAN GIOVANNI BOSCO",
    "OSPEDALE DI RIVOLI",
    "OSPEDALE MARTINI",
    "PRESIDIO SANITARIO GRADENIGO",
    "OSPEDALE REGINA MARGHERITA",
    "OSPEDALE SANT'ANNA",
]
_BASELINE = 3            # slots visible at the very first request
_EXPIRY_SECONDS = 60     # a slot disappears this long after it is created
_SEED = 0                # fixed Faker seed, so a fresh run repeats the sequence
_LAST_DAY = date(2027, 12, 31)


class CupData:
    """Generates and expires the slots each prestazione currently offers.

    Each code is anchored on its first request. From the anchor, ``baseline``
    slots exist immediately and one more is due every ``frame_seconds``; each
    slot lives for ``_EXPIRY_SECONDS``. ``clock`` is injectable so the growth
    and expiry can be tested without really waiting.
    """

    def __init__(self, frame_seconds: float, clock: Callable[[], float] = time.time) -> None:
        """Build the generator.

        Args:
            frame_seconds: seconds between one new slot becoming due and the next.
            clock: a callable returning the current time in seconds (injectable).
        """
        self.__frame_seconds = frame_seconds
        self.__clock = clock
        self.__faker = Faker("it_IT")
        Faker.seed(_SEED)
        self.__anchors: dict[str, float] = {}          # code -> first-request time
        self.__slots: dict[str, list] = {}             # code -> [{created, slot}]
        self.__made: dict[str, int] = {}               # code -> slots ever created

    def resolve_nre(self, nre: str) -> dict | None:
        """Resolve an NRE to the prestazione it unlocks.

        Args:
            nre: the prescription number.
        Returns:
            A dict {code, descrizione}, or None if the NRE is unknown.
        """
        code = _NRE_TO_CODE.get(nre)
        result = None
        if code is not None:
            result = {"code": code, "descrizione": _PRESTAZIONI[code]}
        return result

    def slots_for(self, code: str) -> list | None:
        """Return the slots currently available for a prestazione.

        Args:
            code: the prestazione code.
        Returns:
            The currently-available slots (baseline + one per elapsed frame, minus
            those older than 60s), or None if the code is unknown.
        """
        result = None
        if code in _PRESTAZIONI:
            self.__catch_up(code)
            now = self.__clock()
            self.__slots[code] = [
                entry for entry in self.__slots[code]
                if now - entry["created"] < _EXPIRY_SECONDS
            ]
            result = [entry["slot"] for entry in self.__slots[code]]
        return result

    def __catch_up(self, code: str) -> None:
        """Create every slot that should exist by now (baseline + one per frame).

        Args:
            code: the prestazione code to advance.
        """
        now = self.__clock()
        if code not in self.__anchors:
            self.__anchors[code] = now
            self.__slots[code] = []
            self.__made[code] = 0
        anchor = self.__anchors[code]
        due = _BASELINE + int((now - anchor) // self.__frame_seconds)
        while self.__made[code] < due:
            index = self.__made[code]
            if index < _BASELINE:
                created = anchor  # the baseline batch all share the anchor time
            else:
                created = anchor + (index - _BASELINE + 1) * self.__frame_seconds
            self.__slots[code].append({"created": created, "slot": self.__make_slot()})
            self.__made[code] += 1

    def __make_slot(self) -> dict:
        """Generate one random slot with Faker (it_IT)."""
        appointment = self.__faker.date_between(start_date=date.today(), end_date=_LAST_DAY)
        return {
            "date": appointment.isoformat(),
            "time": self.__faker.time(pattern="%H:%M"),
            "struttura": self.__faker.random_element(_FACILITIES),
            "cap": self.__faker.postcode(),
            "address": self.__faker.street_address(),
        }


app = Flask(__name__)
cup = CupData(FRAME_SECONDS)


@app.get("/")
def home() -> str:
    """Return a short banner so the server is easy to check in a browser."""
    return "CUP finto attivo. Prova /prestazione?nre=... oppure /slots?code=..."


@app.get("/prestazione")
def prestazione() -> ResponseReturnValue:
    """Resolve an NRE to the prestazione it unlocks (used during registration).

    Query params:
        nre: the prescription number.
    Returns:
        JSON {code, descrizione} with status 200, or {error} with status 404.
    """
    nre = request.args.get("nre", "")
    data = cup.resolve_nre(nre)
    if data is None:
        response = jsonify({"error": "NRE non riconosciuto"}), 404
    else:
        response = jsonify(data)
    return response


@app.get("/slots")
def slots() -> ResponseReturnValue:
    """Return the current slots for a prestazione (the daemon polls this).

    Query params:
        code: the prestazione code.
    Returns:
        JSON {code, slots} with status 200, or {error} with status 404.
    """
    code = request.args.get("code", "")
    current = cup.slots_for(code)
    if current is None:
        response = jsonify({"error": "prestazione sconosciuta"}), 404
    else:
        response = jsonify({"code": code, "slots": current})
    return response


def main() -> None:
    """Start the Flask development server."""
    app.run(host=CUP_HOST, port=CUP_PORT, debug=False)


if __name__ == "__main__":
    main()
