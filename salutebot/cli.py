"""Terminal CLI client — the management surface over the store (D5/D14/D35).

Per D27 the CLI **never scrapes**; it only reads/writes SQLite rows. So this
module implements the commands that need no scrape: login (`-u`), `--list`,
`--disable` (menu), `--disable-all`, `--delete-user`, and the returning-user
display. New-user registration and adding a prestazione require the D14
acknowledgment scrape, which per D27 is **daemon-driven** — deferred until the
watcher daemon (Phase 3) exists.

Secret hygiene (D35): no secret is ever a command-line argument. `-u`'s CF value
is **optional** (prompt when omitted, so it need not enter shell history / the
process table); `--disable` uses a **numbered menu** (no NRE typed); nothing here
echoes `argv` or a secret. The CF is treated as identifying-but-not-terminal-
secret, so it is prompted in the clear; no NRE is ever handled by this surface.

I/O is injected (`read`/`write` default to `input`/`print`) so the whole flow is
driftless to test without a TTY.
"""

import argparse
import os

from salutebot.config import EnvConfig
from salutebot.crypto import Crypto
from salutebot.store import Store
from salutebot.validation import validate_cf

_DB_PATH_VAR = "SALUTEBOT_DB"
_DEFAULT_DB = "salute-bot.db"


def main(argv: list[str] | None = None, *, store: Store | None = None,
         read=input, write=print) -> None:
    """Entry point. Builds a real `Store` from env unless one is injected (tests)."""
    args = _build_parser().parse_args(argv)
    own_store = store is None
    if own_store:
        store = Store(os.environ.get(_DB_PATH_VAR, _DEFAULT_DB), Crypto.from_env(EnvConfig()))
    try:
        _dispatch(args, store, read, write)
    finally:
        if own_store:
            store.close()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="salute-bot",
        description="Alert-first slot-watcher for the Piemonte SSN CUP no-login flow.",
    )
    # -u takes an OPTIONAL CF (D35): `-u CF` uses it, bare `-u` prompts. Absent =>
    # None. A management flag without -u also prompts, via _resolve_cf.
    parser.add_argument("-u", "--user", nargs="?", const="", default=None, metavar="CF",
                        help="log in as that CF (value optional; prompted if omitted)")
    parser.add_argument("--list", action="store_true",
                        help="list all slots found to date for your watched prestazioni")
    parser.add_argument("--disable", action="store_true",
                        help="disable notifications for one prestazione (numbered menu)")
    parser.add_argument("--disable-all", action="store_true",
                        help="disable all of your notifications")
    parser.add_argument("--delete-user", action="store_true",
                        help="permanently erase all your records (re-type CF to confirm)")
    return parser


def _dispatch(args, store: Store, read, write) -> None:
    if args.list:
        _with_user(args.user, store, read, write, _cmd_list)
    elif args.disable:
        _with_user(args.user, store, read, write,
                   lambda s, cf, w: _cmd_disable(s, cf, read, w))
    elif args.disable_all:
        _with_user(args.user, store, read, write, _cmd_disable_all)
    elif args.delete_user:
        _with_user(args.user, store, read, write,
                   lambda s, cf, w: _cmd_delete_user(s, cf, read, w))
    elif args.user is not None:  # -u given, no other flag => log in + show menu
        _with_user(args.user, store, read, write, _returning_user_menu)
    else:  # bare invocation => registration / menu
        _registration(store, read, write)


# ----- CF resolution + guard -----

def _resolve_cf(user_arg, read, write) -> str | None:
    """A validated CF from the `-u` value, or a prompt when it was omitted."""
    raw = user_arg if user_arg else read("Codice Fiscale: ")
    try:
        return validate_cf(raw)
    except ValueError as err:
        write(str(err))
        return None


def _with_user(user_arg, store: Store, read, write, action) -> None:
    """Resolve + require an existing user, then run `action(store, cf, write)`."""
    cf = _resolve_cf(user_arg, read, write)
    if cf is None:
        return
    if not store.user_exists(cf):
        write("No user found for that CF. Run salute-bot with no arguments to register.")
        return
    action(store, cf, write)


# ----- commands (all read-only or row-level; no scrape, D27) -----

def _cmd_list(store: Store, cf: str, write) -> None:
    rows = store.list_user_slots(cf)
    if not rows:
        write("No slots found yet for your watched prestazioni.")
        return
    current_code = None
    for row in rows:
        if row["code"] != current_code:
            current_code = row["code"]
            write(f"\n{row['code']} — {row['descrizione']}")
        where = row["struttura"] or "?"
        if row["address"]:
            where = f"{where}, {row['address']}"
        write(f"  {row['iso_date']} {row['time']} — {where}")


def _cmd_disable(store: Store, cf: str, read, write) -> None:
    targets = store.get_user_targets(cf)
    if not targets:
        write("You have no watched prestazioni.")
        return
    write("Which prestazione's notifications do you want to disable?")
    for i, target in enumerate(targets, 1):
        off = "" if target["active"] else "  (already off)"
        write(f"  {i}) {target['code']} — {target['descrizione']}{off}")
    choice = read("Number (blank to cancel): ").strip()
    if not choice:
        write("Cancelled.")
        return
    if not choice.isdigit() or not (1 <= int(choice) <= len(targets)):
        write("Not a valid choice — nothing changed.")
        return
    picked = targets[int(choice) - 1]
    store.deactivate_target(cf, picked["code"])
    write(f"Disabled notifications for {picked['code']}.")


def _cmd_disable_all(store: Store, cf: str, write) -> None:
    n = store.deactivate_all_targets(cf)
    write(f"Disabled notifications for {n} prestazione(s).")


def _cmd_delete_user(store: Store, cf: str, read, write) -> None:
    write("This ERASES all your data (CF, email, NRE, found slots). This cannot be undone.")
    confirm = read("Re-type your CF to confirm: ")
    try:
        confirmed = validate_cf(confirm)
    except ValueError:
        confirmed = None
    if confirmed != cf:
        write("CF did not match — nothing was deleted.")
        return
    store.delete_user(cf)
    write("Your records have been permanently deleted.")


# ----- registration / menu -----

def _registration(store: Store, read, write) -> None:
    cf = _resolve_cf(None, read, write)
    if cf is None:
        return
    if store.user_exists(cf):
        _returning_user_menu(store, cf, write)
        return
    # New-user onboarding needs the D14 acknowledgment scrape (NRE -> prestazione
    # + initial slots), which per D27 is daemon-driven -- not built yet (Phase 3).
    write("Registering a new user needs the watcher service, which isn't available yet.")
    write("Available now: -u [CF], --list, --disable, --disable-all, --delete-user.")


def _returning_user_menu(store: Store, cf: str, write) -> None:
    write(f"Welcome back. Notifications go to {store.get_email(cf)}.")
    targets = store.get_user_targets(cf)
    if not targets:
        write("You are not watching any prestazioni yet.")
    else:
        write("You are watching:")
        for target in targets:
            state = "on" if target["active"] else "off"
            write(f"  {target['code']} — {target['descrizione']}  [{state}]")
    write("Manage with: --list, --disable, --disable-all, --delete-user.")


if __name__ == "__main__":
    main()
