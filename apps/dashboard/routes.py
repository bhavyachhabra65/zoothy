from flask import Blueprint, render_template
from .services import modules

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

@dashboard_bp.get("/")
def index():
    return render_template(
        "dashboard/dashboard.html",
        modules=modules,
    )