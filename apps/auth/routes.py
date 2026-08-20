from flask import Blueprint, request, redirect, render_template, session, url_for
from flask_login import login_user, logout_user

from apps.auth.services import AuthService
from apps.auth.email import send_password_reset_otp
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

@auth_bp.get("/forgot-password")
def forgot_password():
    return render_template(
        "auth/forgot_password.html"
    )

@auth_bp.post("/forgot-password")
def forgot_password_submit():

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    user, otp = AuthService.create_password_reset_otp(
        email
    )

    if user:
        send_password_reset_otp(
            user.email,
            otp
        )

        session["password_reset_user_id"] = user.id

    return redirect(
        url_for("auth.verify_otp")
    )

@auth_bp.get("/verify-otp")
def verify_otp():

    if "password_reset_user_id" not in session:
        return redirect(
            url_for("auth.forgot_password")
        )

    return render_template(
        "auth/verify_otp.html"
    )

@auth_bp.post("/verify-otp")
def verify_otp_submit():

    user_id = session.get(
        "password_reset_user_id"
    )

    if not user_id:
        return redirect(
            url_for("auth.forgot_password")
        )

    otp = request.form.get(
        "otp",
        ""
    ).strip()

    valid = AuthService.verify_password_reset_otp(
        user_id,
        otp
    )

    if not valid:
        return render_template(
            "auth/verify_otp.html",
            error="The code is incorrect or has expired."
        ), 400

    session["password_reset_verified"] = True

    return redirect(
        url_for("auth.reset_password")
    )

@auth_bp.get("/reset-password")
def reset_password():

    if not session.get(
        "password_reset_verified"
    ):
        return redirect(
            url_for("auth.forgot_password")
        )

    return render_template(
        "auth/reset_password.html"
    )

@auth_bp.post("/reset-password")
def reset_password_submit():

    user_id = session.get(
        "password_reset_user_id"
    )

    verified = session.get(
        "password_reset_verified"
    )

    if not user_id or not verified:
        return redirect(
            url_for("auth.forgot_password")
        )

    password = request.form.get(
        "password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )

    if len(password) < 8:
        return render_template(
            "auth/reset_password.html",
            error="Password must be at least 8 characters."
        ), 400

    if password != confirm_password:
        return render_template(
            "auth/reset_password.html",
            error="Passwords do not match."
        ), 400

    success = AuthService.reset_password(
        user_id,
        password
    )

    if not success:
        return redirect(
            url_for("auth.forgot_password")
        )

    session.pop(
        "password_reset_user_id",
        None
    )

    session.pop(
        "password_reset_verified",
        None
    )

    return redirect(
        url_for("auth.login")
    )