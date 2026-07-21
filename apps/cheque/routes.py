from flask import Blueprint, render_template, request
from apps.cheque.layouts import default

from .services import build_cheque_data
from .validators import validate_cheque

cheque_bp = Blueprint(
    "cheque",
    __name__,
    url_prefix="/cheque"
)

@cheque_bp.route("/")
def index():
    return render_template("cheque/print.html")

@cheque_bp.post("/print")
def print_cheque():

    cheque = build_cheque_data(request.form)

    validate_cheque(cheque)

    return render_template(
        "cheque/cheque_sheet.html",
        cheque=cheque,
        layout=default,
    )