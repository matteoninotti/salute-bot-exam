"""Live Playwright drive of the CUP no-login JSF flow (Phase 4).

The real `Scraper` behind the seam (`base.py`). Drives headless Chromium through the
stateful Liferay/ICEfaces flow: a **real browser** harvests `ViewState` / `p_auth` /
`ice.*` itself, so we never replay raw POSTs (D18; recon discovery 3 — replaying would
mean re-harvesting and re-injecting every token at every step).

Flow — verified against `recon/flow.har` + the public form DOM:
    GET  cup.isan.csi.it/                          seed cookies
    GET  .../web/guest/ricetta-dematerializzata    form (CFInput + nreInput0)
    click the VISIBLE "Avanti" (`nreButton` div; the real submit is the hidden
        `epPrestazioniForwardNavigate` input) ..... epPrestazioni.xhtml (confirmation)
    click "Avanti" (`epPrestazioni-nextButton-main`) appuntamentiPrimaDisp.xhtml
    leave the geo selectors empty, click "Estendi area di ricerca" (`nextArea`) so the
        search always reaches the WIDEST area before harvesting (D17) ...............
        the `availableAppointmentsContainer` partial-response with the slots

Outcomes map to the seam's types (`base.py`): a parsed prestazione + slots →
`ScrapeResult`; any flow/timeout/parse failure → `ScrapeError` (transient, D11).
`NREInvalidError` is **not raised yet**: the exact invalid-NRE wire signal (D28) is
unconfirmed, so per the 2026-07-04 decision every failure stays transient until the
signal is captured from a dead ricetta in the live smoke run (`nreError0`/`cfError`
are the likely hook — see `_check_invalid_nre`). Parsing reuses the offline-tested
`parse_prestazione_confirmation` / `parse_available_slots`.

Points still needing the live smoke run are marked `SMOKE-CONFIRM`.
"""

import os
import re
from collections.abc import Mapping

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from salutebot.scraper.base import NREInvalidError, ScrapeError, ScrapeResult
from salutebot.scraper.confirmation import parse_prestazione_confirmation
from salutebot.scraper.parser import parse_available_slots

_SEED_URL = "https://cup.isan.csi.it/"
_FORM_URL = "https://cup.isan.csi.it/web/guest/ricetta-dematerializzata"

# JSF element ids (confirmed from the public form DOM + the two redacted captures).
# The portlet prefix is constant; the real submit inputs are display:none, so we click
# the VISIBLE proceed buttons (recon §1) and let ICEfaces fire the hidden submit.
_P = "_ricettaelettronica_WAR_cupprenotazione_:"
_CF_INPUT = _P + "ePrescriptionSearchForm:CFInput"
_NRE_INPUT = _P + "ePrescriptionSearchForm:nreInput0"        # single NRE box (box-count = 1)
_SEARCH_BTN = _P + "ePrescriptionSearchForm:nreButton"       # visible "Avanti" div
_NRE_ERROR = _P + "ePrescriptionSearchForm:nreError0"        # invalid-NRE hook (SMOKE-CONFIRM)
_CF_ERROR = _P + "ePrescriptionSearchForm:cfError"
_CONFIRM_NEXT = _P + "navigation-epPrestazioni-main:epPrestazioni-nextButton-main"  # "Avanti"
_APPUNTAMENTI_FORM = _P + "appuntamentiForm"                 # the slots page is up
_NEXT_AREA = _P + "appuntamentiForm:nextArea"               # "Estendi area di ricerca"
_WARNING_CONFIRM = _P + "appuntamentiForm:dialogAppuntamentiWarningConfirmButton"
_SLOTS_CONTAINER = _P + "appuntamentiForm:availableAppointmentsContainer"
_CONFIRM_ROW = ".prestazioneRow"                             # confirmation parse target (D14)
# "altre disponibilità" is a positional j_idt button (id renumbers per render, HAR
# source `_t385`), so it is matched by its visible label, not its id (SMOKE-CONFIRM).
_MORE_AVAIL_RE = re.compile(r"altre disponibilit", re.I)


def _sel(element_id: str) -> str:
    """CSS attribute selector for a JSF id (colons make `#id` unusable)."""
    return f'[id="{element_id}"]'


class LiveScraper:
    """Drives the CUP flow for one `(CF, NRE)` via headless Chromium (D5/D18).

    Attributes private (encapsulation guardrail). A fresh browser + context is used per
    scrape, so each run is a clean session (matches D4: tokens/cookies re-harvested every
    cycle, never persisted) with no state leaking between scrapes."""

    def __init__(self, headless: bool = True, timeout_s: float = 60.0,
                 action_s: float = 10.0) -> None:
        self.__headless = headless
        # The CUP site is slow (a proceed can take ~30 s incl. reCAPTCHA; the slots page
        # ~15 s), so the page-transition timeout is generous.
        self.__timeout_ms = int(timeout_s * 1000)
        # Shorter wait for CONDITIONAL controls (the extend-area buttons, the warning
        # dialog): present on some ricette, absent on others — don't burn the full
        # timeout when they legitimately aren't there.
        self.__action_ms = int(action_s * 1000)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "LiveScraper":
        """Build from env: `SALUTEBOT_HEADFUL` (truthy → show the browser, for debugging);
        `SALUTEBOT_SCRAPE_TIMEOUT` (seconds, default 30)."""
        src = os.environ if env is None else env
        headful = (src.get("SALUTEBOT_HEADFUL", "").strip().lower() in ("1", "true", "yes"))
        timeout = float(src.get("SALUTEBOT_SCRAPE_TIMEOUT", "60"))
        return cls(headless=not headful, timeout_s=timeout)

    def scrape(self, cf: str, nre: str) -> ScrapeResult:
        """Run the full flow once and return the prestazione + current slots.

        Any browser/flow error becomes a transient `ScrapeError` (D11) so the daemon
        retries rather than crashing on the fragile JSF flow. Secrets are typed into the
        page but never logged; error text carries only the exception type, never a value."""
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=self.__headless)
                try:
                    page = browser.new_context().new_page()
                    page.set_default_timeout(self.__timeout_ms)
                    return self.__run_flow(page, cf, nre)
                finally:
                    browser.close()
        except NREInvalidError:
            raise  # permanent (D28) — let it propagate for rotation
        except ScrapeError:
            raise  # already the transient type
        except Exception as exc:  # any Playwright/other failure → transient (D11)
            raise ScrapeError(f"live drive failed: {type(exc).__name__}") from exc

    # ----- flow steps (each grounded in the HAR; SMOKE-CONFIRM where dynamic) -----

    def __run_flow(self, page, cf: str, nre: str) -> ScrapeResult:
        page.goto(_SEED_URL, wait_until="domcontentloaded")   # seed session cookies
        page.goto(_FORM_URL, wait_until="domcontentloaded")   # the CF+NRE form

        page.fill(_sel(_CF_INPUT), cf)
        page.fill(_sel(_NRE_INPUT), nre)
        page.click(_sel(_SEARCH_BTN))                         # visible "Avanti" (proceed)
        self.__await_confirmation(page)
        self.__check_invalid_nre(page)                        # no-op until the signal is confirmed

        prestazione = parse_prestazione_confirmation(page.content())
        if prestazione is None:
            # Could be an invalid NRE OR a real flow glitch — treated as transient until
            # the invalid signal is wired (D28 / 2026-07-04 decision). SMOKE-CONFIRM.
            raise ScrapeError("confirmation page had no parseable prestazione")

        page.click(_sel(_CONFIRM_NEXT))                       # "Avanti" → appuntamenti page
        page.wait_for_selector(_sel(_APPUNTAMENTI_FORM))      # the slots page is up
        self.__extend_to_widest_area(page)                    # D17

        page.wait_for_selector(_sel(_SLOTS_CONTAINER))
        container_html = page.locator(_sel(_SLOTS_CONTAINER)).inner_html()
        slots = parse_available_slots(container_html)         # may be [] (valid "no slots")
        return ScrapeResult(prestazione=prestazione, slots=slots)

    def __await_confirmation(self, page) -> None:
        """Wait for the epPrestazioni confirmation to render. SMOKE-CONFIRM: recon notes
        the proceed may take two clicks (the first is an input-validation pass), so the
        visible button is retried once before giving up. If it never appears, any text in
        the `nreError0`/`cfError` spans is surfaced in the error — that message is the
        likely invalid-NRE signal (D28), so a dead-ricetta smoke run captures it for free."""
        for attempt in range(2):
            try:
                page.wait_for_selector(_CONFIRM_ROW, timeout=self.__timeout_ms)
                return
            except PlaywrightTimeoutError:
                if attempt == 0:
                    page.click(_sel(_SEARCH_BTN))             # second proceed click
                    continue
                spans = self.__error_spans(page)
                raise ScrapeError(
                    "confirmation never appeared"
                    + (f" — page said: {spans}" if spans else "")
                ) from None

    def __error_spans(self, page) -> str:
        """Combined visible text of the form's validation spans (never a CF/NRE value)."""
        parts = []
        for element_id in (_NRE_ERROR, _CF_ERROR):
            try:
                text = page.locator(_sel(element_id)).inner_text(timeout=1000).strip()
            except Exception:
                text = ""
            if text:
                parts.append(text)
        return " | ".join(parts)

    def __extend_to_widest_area(self, page) -> None:
        """Always advance to the widest search area before harvesting (D17).

        The geo selectors are left empty (they submit NO_VALUE); reaching the wide list is
        a **two-step, conditional** branch (recon; HAR sources `_t385` → `nextArea`): first
        "altre disponibilità", then "Estendi area di ricerca". Both are best-effort — a
        ricetta with near-home availability may show neither — so each is clicked only if
        present, then the ICEfaces partial-response is allowed to settle. An optional
        warning dialog is confirmed if it appears. SMOKE-CONFIRM: the exact labels + waits."""
        if self.__click_if_present(page, page.get_by_text(_MORE_AVAIL_RE)):
            self.__settle(page)
        if self.__click_if_present(page, page.locator(_sel(_NEXT_AREA))):
            self.__click_if_present(page, page.locator(_sel(_WARNING_CONFIRM)))  # optional dialog
            self.__settle(page)

    def __click_if_present(self, page, locator) -> bool:
        """Click the first match if it becomes visible within the short action window;
        return whether it was clicked. Used for the conditional extend-area controls."""
        target = locator.first
        try:
            target.wait_for(state="visible", timeout=self.__action_ms)
        except PlaywrightTimeoutError:
            return False
        target.click()
        return True

    def __settle(self, page) -> None:
        """Let the ICEfaces partial-response finish. Best-effort: the app keeps a poll
        channel open, so networkidle may not fire — the container is read regardless."""
        try:
            page.wait_for_load_state("networkidle", timeout=self.__timeout_ms)
        except PlaywrightTimeoutError:
            pass

    def __check_invalid_nre(self, page) -> None:
        """Hook for the permanent invalid-NRE signal (D28) — DISABLED until confirmed.

        SMOKE-CONFIRM: run this with a known-dead ricetta, read the `nreError0`/`cfError`
        span text, and, once the exact message is known, raise `NREInvalidError` on it so
        D28 rotation activates. Until then every failure stays transient (2026-07-04
        decision), so no ricetta is ever wrongly deactivated.

            err = page.locator(_sel(_NRE_ERROR)).inner_text().strip()
            if err and <confirmed-invalid-substring> in err.lower():
                raise NREInvalidError(err)
        """
        return


def _smoke(argv: list[str] | None = None) -> None:
    """Live smoke run (D-Phase-4): one real scrape, secrets from env or a no-echo prompt,
    printing only the resolved prestazione + slot summary (never the CF/NRE).

    Usage: `SALUTEBOT_SMOKE_CF=... SALUTEBOT_SMOKE_NRE=... python -m salutebot.scraper.drive`
    (or run bare and type them at the prompts). Prompts are **visible** — this is a local
    dev tool, and a prompt is not shell history / argv / a log, so it keeps D35's actual
    guarantees. `SALUTEBOT_HEADFUL=1` shows the browser so you can watch the flow."""
    from salutebot.validation import validate_cf, validate_nre

    cf_raw = os.environ.get("SALUTEBOT_SMOKE_CF") or input("Codice Fiscale: ")
    nre_raw = os.environ.get("SALUTEBOT_SMOKE_NRE") or input("NRE (full 15-char code, e.g. 010A3 + 10 digits): ")
    try:
        cf, nre = validate_cf(cf_raw), validate_nre(nre_raw)
    except ValueError as err:
        print(f"input rejected: {err}")
        return

    print("driving the CUP flow (headless) — this can take a few seconds...")
    try:
        result = LiveScraper.from_env().scrape(cf, nre)
    except ScrapeError as err:
        print(f"scrape failed (transient): {err}")
        return

    p = result.prestazione
    print(f"\nprestazione: {p.descrizione} ({p.code})  quantità={p.quantita}")
    print(f"slots found: {len(result.slots)}")
    for slot in result.slots[:5]:
        print(f"  {slot.iso_date} {slot.time} — {slot.struttura} [{slot.cap}]")
    if len(result.slots) > 5:
        print(f"  … and {len(result.slots) - 5} more")


if __name__ == "__main__":
    _smoke()
