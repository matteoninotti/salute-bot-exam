"""Domain models: Slot and Prestazione.

These are the objects that travel through the whole app (server -> client ->
database -> web page -> PDF). Attributes are private (name-mangled ``__attr``)
and exposed through read-only ``@property`` getters, so nothing outside the
class can mutate the state directly -- the encapsulation style used in the
course.
"""

import hashlib


class Slot:
    """One available appointment for a prestazione.

    A slot is identified by a *natural key* built from its business fields
    (date, time, struttura, cap): the CUP has no stable id for a slot, so we
    hash those fields to recognise the same slot across two checks.
    """

    def __init__(self, date, time, struttura, cap, address):
        self.__date = date
        self.__time = time
        self.__struttura = struttura
        self.__cap = cap
        self.__address = address

    @property
    def date(self):
        return self.__date

    @property
    def time(self):
        return self.__time

    @property
    def struttura(self):
        return self.__struttura

    @property
    def cap(self):
        return self.__cap

    @property
    def address(self):
        return self.__address

    @property
    def key(self):
        """Stable identity of the slot: SHA-256 of its key fields.

        Used to tell a brand-new slot from one we have already seen.
        """
        raw = f"{self.__date}|{self.__time}|{self.__struttura}|{self.__cap}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def to_dict(self):
        """Plain dict, for JSON responses and for saving into the database."""
        return {
            "date": self.__date,
            "time": self.__time,
            "struttura": self.__struttura,
            "cap": self.__cap,
            "address": self.__address,
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a Slot from a dict (JSON payload or database row)."""
        return cls(
            date=data["date"],
            time=data["time"],
            struttura=data["struttura"],
            cap=data["cap"],
            address=data["address"],
        )

    def __str__(self):
        return f"{self.__date} {self.__time} - {self.__struttura} ({self.__address})"


class Prestazione:
    """A bookable medical service, identified by its national code."""

    def __init__(self, code, descrizione):
        self.__code = code
        self.__descrizione = descrizione

    @property
    def code(self):
        return self.__code

    @property
    def descrizione(self):
        return self.__descrizione

    def to_dict(self):
        return {"code": self.__code, "descrizione": self.__descrizione}

    @classmethod
    def from_dict(cls, data):
        return cls(code=data["code"], descrizione=data["descrizione"])

    def __str__(self):
        return f"{self.__code} - {self.__descrizione}"
