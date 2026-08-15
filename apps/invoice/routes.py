import json

from flask import Blueprint, render_template, request, jsonify

from .services import InvoiceService
from .validators import ValidationError


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
        try:

            data = request.form.to_dict()

            data["items"] = json.loads(
                request.form.get("items", "[]")
            )

            invoice = InvoiceService.build_invoice(data)

        except ValidationError as e:

            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        except ValueError as e:

            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        except Exception as e:
            print(Exception)
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

        return render_template(
            "invoice/print.html",
            invoice=invoice
        )

    return render_template("invoice/invoice.html")