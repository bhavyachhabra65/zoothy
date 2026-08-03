from flask import Blueprint, render_template, request, jsonify
from apps.cheque.layouts import ausmallfinance, axis, bandhan, bob, boi, fb, hdfc, icici, indusind, kotak, pnb, sbi, ub, uco

from .services import build_cheque_data
from .validators import validate_cheque, ValidationError

cheque_bp = Blueprint(
    "cheque",
    __name__,
    url_prefix="/cheque"
)

LAYOUTS = {
    "sbi": sbi,
    "hdfc": hdfc,
    "icici": icici,
    "ausmallfinance": ausmallfinance,
    "axis": axis,
    "bandhan": bandhan,
    "bob": bob,
    "boi": boi,
    "fb": fb,
    "indusind": indusind,
    "kotak": kotak,
    "pnb": pnb,
    "ub": ub, 
    "uco": uco
}

@cheque_bp.route("/")
def index():
    return render_template("cheque/print.html")

@cheque_bp.post("/print")
def print_cheque():

    try:
        cheque = build_cheque_data(request.form)
        validate_cheque(cheque)
    except ValidationError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    return render_template(
        "cheque/cheque_sheet.html",
        cheque=cheque,
        layout = LAYOUTS[cheque.bank],
    )