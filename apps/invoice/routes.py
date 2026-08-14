import json

from flask import Blueprint, render_template, request

from .services import InvoiceService

invoice_bp = Blueprint(
    "invoice",
    __name__,
    url_prefix="/invoice"
)


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