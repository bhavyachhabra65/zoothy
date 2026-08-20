from flask import Blueprint, request, redirect, render_template, request, url_for
from flask_login import login_user, logout_user

from apps.auth.services import AuthService
from apps.auth.schemas import RegisterData
from apps.auth.validators import (
    validate_login,
    validate_registration,
)


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth_bp.get("/login")
def login():
    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_submit():

    email = request.form.get("email", "")
    password = request.form.get("password", "")

    error = validate_login(
        email,
        password
    )

    if error:
        return render_template(
            "auth/login.html",
            error=error,
            email=email
        ), 400

    user = AuthService.authenticate(
        email,
        password
    )

    if not user:
        return render_template(
            "auth/login.html",
            error="Email or password is incorrect.",
            email=email
        ), 401

    login_user(user)

    next_page = request.args.get("next")

    if next_page and next_page.startswith("/"):
        return redirect(next_page)

    return redirect(
        url_for("dashboard.index")
    )


@auth_bp.get("/register")
def register():
    return render_template("auth/register.html")


@auth_bp.post("/register")
def register_submit():

    name = request.form.get("name", "")
    email = request.form.get("email", "")
    password = request.form.get("password", "")
    confirm_password = request.form.get(
        "confirm_password",
        ""
    )

    error = validate_registration(
        name,
        email,
        password,
        confirm_password
    )

    if error:
        return render_template(
            "auth/register.html",
            error=error,
            name=name,
            email=email
        ), 400

    data = RegisterData(
        name=name.strip(),
        email=email.strip().lower(),
        password=password
    )

    user, error = AuthService.register(data)

    if error:
        return render_template(
            "auth/register.html",
            error=error,
            name=name,
            email=email
        ), 409

    login_user(user)

    return redirect(
        url_for("dashboard.index")
    )

@auth_bp.post("/logout")
def logout():

    logout_user()

    return redirect(
        url_for("auth.login")
    )