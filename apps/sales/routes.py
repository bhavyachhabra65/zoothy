from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from apps.customers.services import CustomerService
from apps.products.services import ProductService
from apps.sales.services import SalesService
from apps.sales.validators import validate_sale_date, validate_sale_items


sales_bp = Blueprint(
    "sales",
    __name__,
    url_prefix="/sales"
)


def _options(user_id):
    return (
        CustomerService.list_customers(user_id),
        ProductService.list_products(user_id)
    )


def _parse_items():
    product_ids = request.form.getlist("product_id")
    quantities = request.form.getlist("quantity")
    prices = request.form.getlist("unit_price")

    items = []
    for index in range(max(len(product_ids), len(quantities), len(prices))):
        items.append({
            "product_id": product_ids[index].strip() if index < len(product_ids) else "",
            "quantity": quantities[index].strip() if index < len(quantities) else "",
            "unit_price": prices[index].strip() if index < len(prices) else ""
        })
    return items


def _parse_customer_id(value):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        raise ValueError("Select a valid customer.")


def _parse_sale_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Enter a valid sale date.")


@sales_bp.get("/")
@login_required
def index():
    search = request.args.get("search", "").strip()
    sales = SalesService.list_sales(current_user.id, search)
    return render_template(
        "sales/sales.html",
        sales=sales,
        search=search
    )


@sales_bp.get("/add")
@login_required
def add():
    customers, products = _options(current_user.id)
    return render_template(
        "sales/add_sale.html",
        customers=customers,
        products=products,
        sale_date=date.today().isoformat(),
        selected_customer_id="",
        form_items=[{
            "product_id": "",
            "quantity": "1",
            "unit_price": ""
        }],
        notes="",
        error=None
    )


@sales_bp.post("/add")
@login_required
def add_submit():
    customers, products = _options(current_user.id)

    sale_date_value = request.form.get("sale_date", "").strip()
    customer_id_value = request.form.get("customer_id", "").strip()
    notes = request.form.get("notes", "").strip()
    form_items = _parse_items()

    error = validate_sale_date(sale_date_value)
    if not error:
        error = validate_sale_items(form_items)

    customer_id = None
    sale_date = None

    if not error:
        try:
            sale_date = _parse_sale_date(sale_date_value)
        except ValueError as exc:
            error = str(exc)

    if not error:
        try:
            customer_id = _parse_customer_id(customer_id_value)
        except ValueError as exc:
            error = str(exc)

    if error:
        return render_template(
            "sales/add_sale.html",
            customers=customers,
            products=products,
            sale_date=sale_date_value,
            selected_customer_id=customer_id_value,
            form_items=form_items,
            notes=notes,
            error=error
        ), 400

    try:
        sale = SalesService.create_sale(
            user_id=current_user.id,
            customer_id=customer_id,
            sale_date=sale_date,
            items=form_items,
            notes=notes
        )
    except (ValueError, ArithmeticError) as exc:
        return render_template(
            "sales/add_sale.html",
            customers=customers,
            products=products,
            sale_date=sale_date_value,
            selected_customer_id=customer_id_value,
            form_items=form_items,
            notes=notes,
            error=str(exc)
        ), 400

    flash("Sale recorded successfully.", "success")
    return redirect(url_for("sales.view", sale_id=sale.id))


@sales_bp.get("/<int:sale_id>")
@login_required
def view(sale_id):
    sale = SalesService.get_sale(current_user.id, sale_id)
    if not sale:
        return redirect(url_for("sales.index"))

    return render_template(
        "sales/sale.html",
        sale=sale,
        customer=sale.customer
    )


@sales_bp.get("/<int:sale_id>/edit")
@login_required
def edit(sale_id):
    sale = SalesService.get_sale(current_user.id, sale_id)
    if not sale:
        return redirect(url_for("sales.index"))

    customers, products = _options(current_user.id)

    form_items = [
        {
            "product_id": str(item.product_id),
            "quantity": str(item.quantity),
            "unit_price": str(item.unit_price)
        }
        for item in sale.items
    ]

    return render_template(
        "sales/edit_sale.html",
        sale=sale,
        customers=customers,
        products=products,
        sale_date=sale.sale_date.isoformat(),
        selected_customer_id=str(sale.customer_id or ""),
        form_items=form_items,
        notes=sale.notes or "",
        error=None
    )


@sales_bp.post("/<int:sale_id>/edit")
@login_required
def edit_submit(sale_id):
    sale = SalesService.get_sale(current_user.id, sale_id)
    if not sale:
        return redirect(url_for("sales.index"))

    customers, products = _options(current_user.id)

    sale_date_value = request.form.get("sale_date", "").strip()
    customer_id_value = request.form.get("customer_id", "").strip()
    notes = request.form.get("notes", "").strip()
    form_items = _parse_items()

    error = validate_sale_date(sale_date_value)
    if not error:
        error = validate_sale_items(form_items)

    customer_id = None
    sale_date = None

    if not error:
        try:
            sale_date = _parse_sale_date(sale_date_value)
        except ValueError as exc:
            error = str(exc)

    if not error:
        try:
            customer_id = _parse_customer_id(customer_id_value)
        except ValueError as exc:
            error = str(exc)

    if error:
        return render_template(
            "sales/edit_sale.html",
            sale=sale,
            customers=customers,
            products=products,
            sale_date=sale_date_value,
            selected_customer_id=customer_id_value,
            form_items=form_items,
            notes=notes,
            error=error
        ), 400

    try:
        updated_sale = SalesService.update_sale(
            user_id=current_user.id,
            sale_id=sale_id,
            customer_id=customer_id,
            sale_date=sale_date,
            items=form_items,
            notes=notes
        )
    except (ValueError, ArithmeticError) as exc:
        return render_template(
            "sales/edit_sale.html",
            sale=sale,
            customers=customers,
            products=products,
            sale_date=sale_date_value,
            selected_customer_id=customer_id_value,
            form_items=form_items,
            notes=notes,
            error=str(exc)
        ), 400

    flash("Sale updated successfully.", "success")
    return redirect(url_for("sales.view", sale_id=updated_sale.id))
