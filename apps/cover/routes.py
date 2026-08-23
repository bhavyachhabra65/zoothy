from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

cover_bp = Blueprint(
    "cover",
    __name__,
    url_prefix="/"
)

@cover_bp.get("/")
def index():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    return render_template("cover/cover.html")