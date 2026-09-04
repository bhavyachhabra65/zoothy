from decimal import Decimal

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from flask_login import current_user, login_required

from apps.inventory.services import InventoryService
from apps.inventory.validators import (
    validate_low_stock_level,
    validate_stock_adjustment
)
from apps.products.services import ProductService


inventory_bp = Blueprint(
    "inventory",
    __name__,
    url_prefix="/inventory"
)


def _form_data():

    return {
        "movement_type": request.form.get(
            "movement_type",
            "add"
        ).strip().lower(),
        "quantity": request.form.get(
            "quantity",
            ""
        ).strip(),
        "reason": request.form.get(
            "reason",
            ""
        ).strip(),
        "low_stock_level": request.form.get(
            "low_stock_level",
            "0"
        ).strip()
    }


def _product_options(user_id):

    return ProductService.list_products(
        user_id
    )


@inventory_bp.get("/")
@login_required
def index():

    search = request.args.get(
        "search",
        ""
    ).strip()

    inventory = InventoryService.list_inventory(
        current_user.id,
        search
    )

    return render_template(
        "inventory/inventory.html",
        inventory=inventory,
        search=search
    )


@inventory_bp.get("/add")
@login_required
def add():

    products = _product_options(
        current_user.id
    )

    return render_template(
        "inventory/adjust_stock.html",
        products=products,
        form_data={
            "movement_type": "add",
            "quantity": "",
            "reason": "",
            "low_stock_level": "0"
        },
        selected_product_id=request.args.get(
            "product_id",
            ""
        )
    )


@inventory_bp.post("/add")
@login_required
def add_submit():

    product_id = request.form.get(
        "product_id",
        ""
    ).strip()

    form_data = _form_data()

    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        product_id = None

    if not product_id:
        error = "Select a product."
    else:
        error = validate_stock_adjustment(
            **form_data
        )

    products = _product_options(
        current_user.id
    )

    if error:
        return render_template(
            "inventory/adjust_stock.html",
            products=products,
            form_data=form_data,
            selected_product_id=product_id or "",
            error=error
        ), 400

    try:
        InventoryService.adjust_stock(
            current_user.id,
            product_id,
            form_data["movement_type"],
            Decimal(form_data["quantity"]),
            form_data["reason"],
            Decimal(form_data["low_stock_level"] or 0)
        )
    except ValueError as exc:
        return render_template(
            "inventory/adjust_stock.html",
            products=products,
            form_data=form_data,
            selected_product_id=product_id,
            error=str(exc)
        ), 400

    flash(
        "Stock updated successfully.",
        "success"
    )

    return redirect(
        url_for(
            "inventory.view",
            product_id=product_id
        )
    )


@inventory_bp.get("/<int:product_id>")
@login_required
def view(product_id):

    inventory = InventoryService.get_product_inventory(
        current_user.id,
        product_id
    )

    if not inventory:
        return redirect(
            url_for("inventory.index")
        )

    movements = InventoryService.get_movements(
        current_user.id,
        product_id
    )

    return render_template(
        "inventory/stock.html",
        inventory=inventory,
        movements=movements
    )


@inventory_bp.post("/<int:product_id>/low-stock")
@login_required
def update_low_stock(product_id):

    low_stock_level = request.form.get(
        "low_stock_level",
        "0"
    ).strip()

    error = validate_low_stock_level(
        low_stock_level
    )

    if error:
        flash(
            error,
            "error"
        )
        return redirect(
            url_for(
                "inventory.view",
                product_id=product_id
            )
        )

    inventory = InventoryService.get_product_inventory(
        current_user.id,
        product_id
    )

    if not inventory:
        return redirect(
            url_for("inventory.index")
        )

    InventoryService.update_low_stock_level(
        current_user.id,
        product_id,
        Decimal(low_stock_level or 0)
    )

    flash(
        "Low-stock level updated.",
        "success"
    )

    return redirect(
        url_for(
            "inventory.view",
            product_id=product_id
        )
    )
