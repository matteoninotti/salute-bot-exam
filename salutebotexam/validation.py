"""Format validation for user-supplied identifiers.

Shared by the CLI and the web client so both accept the same inputs. These are
structural checks only (length + character classes), not real CF/NRE checksums.
"""


def valid_cf(cf: str) -> bool:
    """Return True if cf looks like a codice fiscale (16 alphanumeric chars)."""
    return len(cf) == 16 and cf.isalnum()


def valid_nre(nre: str) -> bool:
    """Return True if nre looks like an NRE (15 alphanumeric chars)."""
    return len(nre) == 15 and nre.isalnum()


def valid_email(email: str) -> bool:
    """Return True if email has a single @ and a dotted domain."""
    return email.count("@") == 1 and "." in email.split("@")[1]
