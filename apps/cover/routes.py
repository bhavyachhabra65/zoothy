from flask import Blueprint, render_template

cover_bp = Blueprint(
    "cover",
    __name__,
    url_prefix="/"
)

@cover_bp.get("/")
def index():
    return render_template("cover/cover.html")