"""Slot detection: split a fresh scrape into new vs already-known.

Given the slots the CUP server currently returns for a prestazione, compare
them to what the store already knows. Known slots get their last_seen bumped;
the new ones are returned (the daemon is what actually saves them).
"""

from models import Slot
from store import Store


def detect_new_slots(store: Store, code: str, current_slots: list[Slot],
                     now: str | None = None) -> list[Slot]:
    """Return the slots that are new for this prestazione.

    Side effect: known slots that are still present have their last_seen bumped.
    New slots are NOT saved here -- the daemon saves them so the timestamp of the
    whole new batch is written together.

    Args:
        store: the Store to check known slots against.
        code: the prestazione code being checked.
        current_slots: the slots the CUP server currently returns.
        now: ISO timestamp used for the last_seen bump; defaults to now.
    Returns:
        The subset of current_slots whose key was not already known.
    """
    known = store.known_slot_keys(code)
    new_slots = []
    for slot in current_slots:
        if slot.key in known:
            store.touch_slot(code, slot.key, now)
        else:
            new_slots.append(slot)
    return new_slots
