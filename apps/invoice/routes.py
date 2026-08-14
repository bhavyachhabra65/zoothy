import json

from flask import Blueprint, render_template, request

from .services import InvoiceService

from datetime import datetime

invoice_bp = Blueprint(
    "invoice",
    __name__,
    url_prefix="/invoice"
)

@invoice_bp.app_template_filter("invoice_date")
def format_invoice_date(value):

    if not value:
        return ""

    try:
        date = datetime.strptime(
            value,
            "%Y-%m-%d"
        )

        return date.strftime(
            "%d %b %Y"
        )

    except (ValueError, TypeError):
        return value


@invoice_bp.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        data = request.form.to_dict()

        data["items"] = json.loads(
            request.form.get("items", "[]")
        )

        invoice = InvoiceService.build_invoice(data)

        return render_template(
            "invoice/print.html",
            invoice=invoice
        )

    return render_template("invoice/invoice.html")