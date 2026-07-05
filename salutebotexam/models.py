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

    def __init__(self, date: str, time: str, struttura: str, cap: str, address: str) -> None:
        """Build a slot.

        Args:
            date: appointment date, ISO format ("2026-07-20").
            time: appointment time, "HH:MM".
            struttura: facility name.
            cap: postal code (CAP).
            address: human-readable address (descriptive only, not in the key).
        """
        self.__date = date
        self.__time = time
        self.__struttura = struttura
        self.__cap = cap
        self.__address = address

    @property
    def date(self) -> str:
        return self.__date

    @property
    def time(self) -> str:
        return self.__time

    @property
    def struttura(self) -> str:
        return self.__struttura

    @property
    def cap(self) -> str:
        return self.__cap

    @property
    def address(self) -> str:
        return self.__address

    @property
    def key(self) -> str:
        """Stable identity of the slot.

        Returns:
            The SHA-256 hex digest of the key fields (date, time, struttura,
            cap). The address is deliberately excluded, so a cosmetic address
            change does not make the slot look new.
        """
        raw = f"{self.__date}|{self.__time}|{self.__struttura}|{self.__cap}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        """Return the slot as a plain dict (for JSON responses and DB rows)."""
        return {
            "date": self.__date,
            "time": self.__time,
            "struttura": self.__struttura,
            "cap": self.__cap,
            "address": self.__address,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Slot":
        """Rebuild a Slot from a dict.

        Args:
            data: a dict with keys date, time, struttura, cap, address (a JSON
                payload from the CUP server or a database row).
        Returns:
            The reconstructed Slot.
        """
        return cls(
            date=data["date"],
            time=data["time"],
            struttura=data["struttura"],
            cap=data["cap"],
            address=data["address"],
        )

    def __str__(self) -> str:
        return f"{self.__date} {self.__time} - {self.__struttura} ({self.__address})"


class Prestazione:
    """A bookable medical service, identified by its national code."""

    def __init__(self, code: str, descrizione: str) -> None:
        """Build a prestazione.

        Args:
            code: national/regional code (e.g. "8901.20").
            descrizione: human-readable name.
        """
        self.__code = code
        self.__descrizione = descrizione

    @property
    def code(self) -> str:
        return self.__code

    @property
    def descrizione(self) -> str:
        return self.__descrizione

    def to_dict(self) -> dict:
        """Return the prestazione as a plain dict."""
        return {"code": self.__code, "descrizione": self.__descrizione}

    @classmethod
    def from_dict(cls, data: dict) -> "Prestazione":
        """Rebuild a Prestazione from a dict with keys code, descrizione."""
        return cls(code=data["code"], descrizione=data["descrizione"])

    def __str__(self) -> str:
        return f"{self.__code} - {self.__descrizione}"
