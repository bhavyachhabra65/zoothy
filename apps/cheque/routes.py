from flask import Blueprint, render_template

cheque_bp = Blueprint(
    "cheque",
    __name__,
    url_prefix="/cheque"
)

@cheque_bp.route("/")
def print_cheque():
    return render_template("cheque/print.html")