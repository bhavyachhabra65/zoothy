from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from flask_login import current_user, login_required

from apps.suppliers.services import SupplierService
from apps.suppliers.validators import validate_supplier


suppliers_bp = Blueprint(
    "suppliers",
    __name__,
    url_prefix="/suppliers"
)


def _form_data():

    return {
        "name": request.form.get("name", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "email": request.form.get("email", "").strip(),
        "gstin": request.form.get("gstin", "").strip().upper(),
        "address": request.form.get("address", "").strip(),
        "notes": request.form.get("notes", "").strip()
    }


@suppliers_bp.get("/")
@login_required
def index():

    search = request.args.get(
        "search",
        ""
    ).strip()

    suppliers = SupplierService.list_suppliers(
        current_user.id,
        search
    )

    return render_template(
        "suppliers/suppliers.html",
        suppliers=suppliers,
        search=search
    )


@suppliers_bp.get("/add")
@login_required
def add():

    return render_template(
        "suppliers/add_supplier.html",
        form_data={}
    )


@suppliers_bp.post("/add")
@login_required
def add_submit():

    form_data = _form_data()

    error = validate_supplier(
        **form_data
    )

    if error:

        return render_template(
            "suppliers/add_supplier.html",
            form_data=form_data,
            error=error
        ), 400

    supplier = SupplierService.create_supplier(
        current_user.id,
        **form_data
    )

    flash(
        "Supplier added successfully.",
        "success"
    )

    return redirect(
        url_for(
            "suppliers.view",
            supplier_id=supplier.id
        )
    )


@suppliers_bp.get("/<int:supplier_id>")
@login_required
def view(supplier_id):

    supplier = SupplierService.get_supplier(
        current_user.id,
        supplier_id
    )

    if not supplier:

        return redirect(
            url_for("suppliers.index")
        )

    return render_template(
        "suppliers/supplier.html",
        supplier=supplier
    )


@suppliers_bp.get("/<int:supplier_id>/edit")
@login_required
def edit(supplier_id):

    supplier = SupplierService.get_supplier(
        current_user.id,
        supplier_id
    )

    if not supplier:

        return redirect(
            url_for("suppliers.index")
        )

    return render_template(
        "suppliers/edit_supplier.html",
        supplier=supplier,
        form_data={}
    )


@suppliers_bp.post("/<int:supplier_id>/edit")
@login_required
def edit_submit(supplier_id):

    supplier = SupplierService.get_supplier(
        current_user.id,
        supplier_id
    )

    if not supplier:

        return redirect(
            url_for("suppliers.index")
        )

    form_data = _form_data()

    error = validate_supplier(
        **form_data
    )

    if error:

        return render_template(
            "suppliers/edit_supplier.html",
            supplier=supplier,
            form_data=form_data,
            error=error
        ), 400

    SupplierService.update_supplier(
        supplier,
        **form_data
    )

    flash(
        "Supplier updated successfully.",
        "success"
    )

    return redirect(
        url_for(
            "suppliers.view",
            supplier_id=supplier.id
        )
    )


@suppliers_bp.post("/<int:supplier_id>/delete")
@login_required
def delete(supplier_id):

    supplier = SupplierService.get_supplier(
        current_user.id,
        supplier_id
    )

    if not supplier:

        return redirect(
            url_for("suppliers.index")
        )

    SupplierService.delete_supplier(
        supplier
    )

    flash(
        "Supplier deleted successfully.",
        "success"
    )

    return redirect(
        url_for("suppliers.index")
    )
