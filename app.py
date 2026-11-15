"""Library reservation system: book a time slot at a university library."""

import json
import os
import re
import secrets
from datetime import date, datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

LIBRARIES = [
    "İstanbul Üniversitesi Kütüphanesi",
    "Hacettepe Üniversitesi Kütüphanesi",
    "Boğaziçi Üniversitesi Kütüphanesi",
    "ODTÜ Kütüphanesi",
    "Ege Üniversitesi Kütüphanesi",
]

EMAIL_PATTERN = re.compile(r"^[^@\s]+@([^@\s]+)$")


def is_allowed_email(email: str) -> bool:
    """Accept university addresses: the domain is edu.tr or ends with .edu.tr (e.g. bilgi.edu.tr)."""
    match = EMAIL_PATTERN.match(email.strip())
    if not match:
        return False
    domain = match.group(1).lower()
    return domain == "edu.tr" or domain.endswith(".edu.tr")


def parse_slot(day: str, time: str):
    """Return (date, time) or None when either is missing or malformed."""
    try:
        return datetime.strptime(day, "%Y-%m-%d").date(), datetime.strptime(time, "%H:%M").time()
    except ValueError:
        return None


class ReservationStore:
    """Reservations kept in a JSON file, so they survive a restart."""

    def __init__(self, path: Path):
        self.path = path

    def all(self) -> list:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as f:
            return json.load(f)

    def save(self, reservations: list) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(reservations, f, ensure_ascii=False, indent=2)
        tmp.replace(self.path)


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATA_FILE=os.environ.get("DATA_FILE", str(Path(__file__).parent / "data" / "reservations.json")),
    )
    if config:
        app.config.update(config)
    store = ReservationStore(Path(app.config["DATA_FILE"]))

    @app.get("/")
    def index():
        return render_template("index.html", reservations=store.all())

    @app.route("/reserve", methods=["GET", "POST"])
    def reserve():
        if request.method == "GET":
            return render_template("reserve.html", libraries=LIBRARIES, form={})

        form = {key: request.form.get(key, "").strip() for key in ("name", "email", "date", "time", "library")}
        error = validate(form, store.all())
        if error:
            flash(error, "danger")
            return render_template("reserve.html", libraries=LIBRARIES, form=form)

        reservations = store.all()
        reservations.append(form)
        store.save(reservations)
        flash("Reservation successful!", "success")
        return redirect(url_for("index"))

    @app.post("/delete/<int:index>")
    def delete(index: int):
        reservations = store.all()
        if 0 <= index < len(reservations):
            reservations.pop(index)
            store.save(reservations)
            flash("Reservation deleted.", "success")
        return redirect(url_for("index"))

    return app


def validate(form: dict, existing: list) -> str | None:
    if not form["name"]:
        return "Please enter your name."
    if not is_allowed_email(form["email"]):
        return "Please use your university email (an address ending in .edu.tr)."
    slot = parse_slot(form["date"], form["time"])
    if slot is None:
        return "Please choose a valid date and time."
    if slot[0] < date.today():
        return "Reservations cannot be made for past dates."
    if form["library"] not in LIBRARIES:
        return "Choose one of the listed libraries."
    for res in existing:
        if (res["date"], res["time"], res["library"]) == (form["date"], form["time"], form["library"]):
            return "This slot is already reserved at the selected library. Please choose another."
    return None


if __name__ == "__main__":
    create_app().run(port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("FLASK_DEBUG") == "1")
