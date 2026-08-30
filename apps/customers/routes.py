from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from flask_login import current_user, login_required

from apps.customers.services import CustomerService
from apps.customers.validators import validate_customer


customers_bp = Blueprint(
    "customers",
    __name__,
    url_prefix="/customers"
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


@customers_bp.get("/")
@login_required
def index():

    search = request.args.get(
        "search",
        ""
    ).strip()

    customers = CustomerService.list_customers(
        current_user.id,
        search
    )

    return render_template(
        "customers/customers.html",
        customers=customers,
        search=search
    )


@customers_bp.get("/add")
@login_required
def add():

    return render_template(
        "customers/add_customer.html",
        form_data={}
    )


@customers_bp.post("/add")
@login_required
def add_submit():

    form_data = _form_data()

    error = validate_customer(
        **form_data
    )

    if error:

        return render_template(
            "customers/add_customer.html",
            form_data=form_data,
            error=error
        ), 400

    customer = CustomerService.create_customer(
        current_user.id,
        **form_data
    )

    flash(
        "Customer added successfully.",
        "success"
    )

    return redirect(
        url_for(
            "customers.view",
            customer_id=customer.id
        )
    )


@customers_bp.get("/<int:customer_id>")
@login_required
def view(customer_id):

    customer = CustomerService.get_customer(
        current_user.id,
        customer_id
    )

    if not customer:
        return redirect(
            url_for("customers.index")
        )

    return render_template(
        "customers/customer.html",
        customer=customer
    )


@customers_bp.get("/<int:customer_id>/edit")
@login_required
def edit(customer_id):

    customer = CustomerService.get_customer(
        current_user.id,
        customer_id
    )

    if not customer:
        return redirect(
            url_for("customers.index")
        )

    return render_template(
        "customers/edit_customer.html",
        customer=customer,
        form_data={}
    )


@customers_bp.post("/<int:customer_id>/edit")
@login_required
def edit_submit(customer_id):

    customer = CustomerService.get_customer(
        current_user.id,
        customer_id
    )

    if not customer:
        return redirect(
            url_for("customers.index")
        )

    form_data = _form_data()

    error = validate_customer(
        **form_data
    )

    if error:

        return render_template(
            "customers/edit_customer.html",
            customer=customer,
            form_data=form_data,
            error=error
        ), 400

    CustomerService.update_customer(
        customer,
        **form_data
    )

    flash(
        "Customer updated successfully.",
        "success"
    )

    return redirect(
        url_for(
            "customers.view",
            customer_id=customer.id
        )
    )


@customers_bp.post("/<int:customer_id>/delete")
@login_required
def delete(customer_id):

    customer = CustomerService.get_customer(
        current_user.id,
        customer_id
    )

    if not customer:
        return redirect(
            url_for("customers.index")
        )

    CustomerService.delete_customer(
        customer
    )

    flash(
        "Customer deleted successfully.",
        "success"
    )

    return redirect(
        url_for("customers.index")
    )
