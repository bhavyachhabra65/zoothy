from flask import Blueprint, render_template
from flask_login import login_required
from .services import modules

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

@dashboard_bp.get("/dashboard")
@login_required
def index():
    return render_template(
        "dashboard/dashboard.html",
        modules=modules,
    )