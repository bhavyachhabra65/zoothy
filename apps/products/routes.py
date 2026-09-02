from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from flask_login import current_user, login_required

from apps.products.services import ProductService
from apps.products.validators import validate_product


products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/products"
)


def _form_data():

    return {
        "name": request.form.get("name", "").strip(),
        "sku": request.form.get("sku", "").strip(),
        "hsn_sac": request.form.get("hsn_sac", "").strip().upper(),
        "unit": request.form.get("unit", "").strip(),
        "purchase_price": request.form.get("purchase_price", "").strip(),
        "selling_price": request.form.get("selling_price", "").strip(),
        "gst_rate": request.form.get("gst_rate", "").strip(),
        "description": request.form.get("description", "").strip()
    }


@products_bp.get("/")
@login_required
def index():

    search = request.args.get(
        "search",
        ""
    ).strip()

    products = ProductService.list_products(
        current_user.id,
        search
    )

    return render_template(
        "products/products.html",
        products=products,
        search=search
    )


@products_bp.get("/add")
@login_required
def add():

    return render_template(
        "products/add_product.html",
        form_data={}
    )


@products_bp.post("/add")
@login_required
def add_submit():

    form_data = _form_data()

    error = validate_product(
        **form_data
    )

    if error:

        return render_template(
            "products/add_product.html",
            form_data=form_data,
            error=error
        ), 400

    product = ProductService.create_product(
        current_user.id,
        **form_data
    )

    flash(
        "Product added successfully.",
        "success"
    )

    return redirect(
        url_for(
            "products.view",
            product_id=product.id
        )
    )


@products_bp.get("/<int:product_id>")
@login_required
def view(product_id):

    product = ProductService.get_product(
        current_user.id,
        product_id
    )

    if not product:
        return redirect(
            url_for("products.index")
        )

    return render_template(
        "products/product.html",
        product=product
    )


@products_bp.get("/<int:product_id>/edit")
@login_required
def edit(product_id):

    product = ProductService.get_product(
        current_user.id,
        product_id
    )

    if not product:
        return redirect(
            url_for("products.index")
        )

    return render_template(
        "products/edit_product.html",
        product=product,
        form_data={}
    )


@products_bp.post("/<int:product_id>/edit")
@login_required
def edit_submit(product_id):

    product = ProductService.get_product(
        current_user.id,
        product_id
    )

    if not product:
        return redirect(
            url_for("products.index")
        )

    form_data = _form_data()

    error = validate_product(
        **form_data
    )

    if error:

        return render_template(
            "products/edit_product.html",
            product=product,
            form_data=form_data,
            error=error
        ), 400

    ProductService.update_product(
        product,
        **form_data
    )

    flash(
        "Product updated successfully.",
        "success"
    )

    return redirect(
        url_for(
            "products.view",
            product_id=product.id
        )
    )


@products_bp.post("/<int:product_id>/delete")
@login_required
def delete(product_id):

    product = ProductService.get_product(
        current_user.id,
        product_id
    )

    if not product:
        return redirect(
            url_for("products.index")
        )

    ProductService.delete_product(
        product
    )

    flash(
        "Product deleted successfully.",
        "success"
    )

    return redirect(
        url_for("products.index")
    )
