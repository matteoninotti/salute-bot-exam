"""Web GUI client (Flask): the graphical face of the client side.

Like the CLI, it never talks to the CUP server. Registration stages a request
in the database and the user watches a page that refreshes until the daemon
resolves it. Everything else (dashboard, history, PDF) is a read of the shared
database. Run it in its own terminal:  python web.py

Note: Flask view functions are module-level (the framework's idiom), so the OOP
work lives in the Store / SlotReport classes they call.
"""

from flask import Flask, abort, redirect, render_template, request, send_file, url_for
from flask.typing import ResponseReturnValue

from config import WEB_PORT
from report import SlotReport
from store import Store
from validation import valid_cf, valid_nre

app = Flask(__name__)


@app.get("/")
def index() -> str:
    """The login page (enter a CF)."""
    return render_template("index.html")


@app.post("/login")
def login() -> ResponseReturnValue:
    """Validate the CF and go to that user's dashboard."""
    cf = request.form.get("cf", "").strip().upper()
    if valid_cf(cf):
        response = redirect(url_for("dashboard", cf=cf))
    else:
        response = render_template("index.html", error="Formato CF non valido (16 caratteri).")
    return response


@app.get("/register")
def register_form() -> str:
    """The registration form."""
    return render_template("register.html")


@app.post("/register")
def register() -> ResponseReturnValue:
    """Validate the form and stage a registration request for the daemon."""
    cf = request.form.get("cf", "").strip().upper()
    nre = request.form.get("nre", "").strip().upper()
    errors = []
    if not valid_cf(cf):
        errors.append("CF non valido.")
    if not valid_nre(nre):
        errors.append("NRE non valido.")
    if errors:
        response = render_template("register.html", error=" ".join(errors), cf=cf)
    else:
        with Store() as store:
            if store.user_exists(cf):
                response = render_template("register.html",
                                           error="Sei gia' registrato. Accedi dalla home.")
            else:
                rich_id = store.add_richiesta(cf, nre)
                response = redirect(url_for("richiesta", rich_id=rich_id))
    return response


@app.get("/richiesta/<int:rich_id>")
def richiesta(rich_id: int) -> str:
    """Show a staged request's status; the template refreshes while pending."""
    with Store() as store:
        req = store.get_richiesta(rich_id)
    if req is None:
        abort(404)
    return render_template("richiesta.html", req=req)


@app.get("/dashboard/<cf>")
def dashboard(cf: str) -> str:
    """Show a user's followed prestazioni and their current slots."""
    cf = cf.strip().upper()
    with Store() as store:
        known = store.user_exists(cf)
        if known:
            targets = store.get_user_targets(cf)
            rows = store.slots_for_user(cf)
            signature = store.slots_signature(cf)  # for the auto-refresh script
    if not known:
        response = render_template("index.html",
                                   error="Nessun utente con questo CF. Registrati.")
    else:
        slots_by_code: dict[str, list] = {}
        for row in rows:
            slots_by_code.setdefault(row["code"], []).append(row)
        response = render_template("dashboard.html", cf=cf,
                                   targets=targets, slots_by_code=slots_by_code,
                                   signature=signature)
    return response


@app.get("/api/state/<cf>")
def api_state(cf: str) -> ResponseReturnValue:
    """Return the user's slot signature as JSON (polled by the dashboard).

    The signature changes when a new slot appears, so the page can reload only
    when there is actually something new to show.
    """
    cf = cf.strip().upper()
    with Store() as store:
        return {"signature": store.slots_signature(cf)}


@app.get("/add/<cf>")
def add_form(cf: str) -> str:
    """The form to add another prestazione for an existing user."""
    return render_template("add.html", cf=cf.strip().upper())


@app.post("/add/<cf>")
def add(cf: str) -> ResponseReturnValue:
    """Stage an add-prestazione request for the daemon."""
    cf = cf.strip().upper()
    nre = request.form.get("nre", "").strip().upper()
    if not valid_nre(nre):
        response = render_template("add.html", cf=cf, error="NRE non valido.")
    else:
        with Store() as store:
            if not store.user_exists(cf):
                response = render_template("index.html", error="Nessun utente con questo CF.")
            else:
                rich_id = store.add_richiesta(cf, None, nre)
                response = redirect(url_for("richiesta", rich_id=rich_id))
    return response


@app.get("/history/<cf>")
def history(cf: str) -> str:
    """Show a user's request history."""
    cf = cf.strip().upper()
    with Store() as store:
        rows = store.history_for_user(cf)
    return render_template("history.html", cf=cf, rows=rows)


@app.get("/report/<cf>")
def report(cf: str) -> ResponseReturnValue:
    """Build and download a PDF report of the user's current slots."""
    cf = cf.strip().upper()
    with Store() as store:
        if not store.user_exists(cf):
            abort(404)
        rows = store.slots_for_user(cf)
    path = SlotReport(cf, rows).build()
    return send_file(path, as_attachment=True, download_name=f"report_{cf}.pdf")


def main() -> None:
    """Start the Flask development server."""
    app.run(host="127.0.0.1", port=WEB_PORT, debug=False)


if __name__ == "__main__":
    main()
