from flask import (
    Blueprint,
    request,
    redirect,
    render_template,
    session,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user
)

from datetime import (
    datetime,
    timezone
)

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


# ==========================================================
# LOGIN
# ==========================================================

@auth_bp.get("/login")
def login():

    return render_template(
        "auth/login.html"
    )


@auth_bp.post("/login")
def login_submit():

    email = request.form.get(
        "email",
        ""
    )

    password = request.form.get(
        "password",
        ""
    )

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

    remember = request.form.get(
        "remember"
    ) == "1"

    login_user(
        user,
        remember=remember
    )

    session.permanent = True

    session["last_activity"] = (
        datetime.now(timezone.utc).isoformat()
    )

    next_page = request.args.get(
        "next"
    )

    if next_page and next_page.startswith("/"):

        return redirect(
            next_page
        )

    return redirect(
        url_for("dashboard.index")
    )


# ==========================================================
# REGISTER
# ==========================================================

@auth_bp.get("/register")
def register():

    return render_template(
        "auth/register.html"
    )


@auth_bp.post("/register")
def register_submit():

    name = request.form.get(
        "name",
        ""
    )

    email = request.form.get(
        "email",
        ""
    )

    password = request.form.get(
        "password",
        ""
    )

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

    user, error = AuthService.register(
        data
    )

    if error:

        return render_template(
            "auth/register.html",
            error=error,
            name=name,
            email=email
        ), 409

    login_user(
        user
    )

    session.permanent = True

    session["last_activity"] = (
        datetime.now(timezone.utc).isoformat()
    )

    return redirect(
        url_for("dashboard.index")
    )


# ==========================================================
# LOGOUT
# ==========================================================

@auth_bp.post("/logout")
def logout():

    logout_user()

    session.clear()

    return redirect(
        url_for("auth.login")
    )


# ==========================================================
# FORGOT PASSWORD
# ==========================================================

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

    # Start a new password-reset flow.
    session["password_reset_flow"] = True
    session["password_reset_verified"] = False

    if user:

        send_password_reset_otp(
            user.email,
            otp
        )

        session["password_reset_user_id"] = (
            user.id
        )

        # OTP is valid for 10 minutes.
        session["password_reset_expires_at"] = (
            datetime.now(timezone.utc).timestamp()
            + 600
        )

    else:

        # Do not reveal whether the email
        # exists in our system.

        session.pop(
            "password_reset_user_id",
            None
        )

        session.pop(
            "password_reset_expires_at",
            None
        )

    flash(
        "If an account exists with this email, we've sent a verification code.",
        "success"
    )

    return redirect(
        url_for("auth.verify_otp")
    )


# ==========================================================
# VERIFY OTP
# ==========================================================

@auth_bp.get("/verify-otp")
def verify_otp():

    if not session.get(
        "password_reset_flow"
    ):

        return redirect(
            url_for("auth.forgot_password")
        )

    return render_template(
        "auth/verify_otp.html",
        expires_at=session.get(
            "password_reset_expires_at"
        )
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
            error="The code is incorrect or has expired.",
            expires_at=session.get(
                "password_reset_expires_at"
            )
        ), 400

    session["password_reset_verified"] = True

    return redirect(
        url_for("auth.reset_password")
    )


# ==========================================================
# RESEND OTP
# ==========================================================

@auth_bp.post("/resend-otp")
def resend_otp():

    user_id = session.get(
        "password_reset_user_id"
    )

    if not user_id:

        return redirect(
            url_for("auth.forgot_password")
        )

    user, otp = AuthService.resend_password_reset_otp(
        user_id
    )

    if not user:

        return redirect(
            url_for("auth.forgot_password")
        )

    send_password_reset_otp(
        user.email,
        otp
    )

    # Reset the OTP timer to 10 minutes.
    session["password_reset_expires_at"] = (
        datetime.now(timezone.utc).timestamp()
        + 600
    )

    session["password_reset_verified"] = False

    flash(
        "A new verification code has been sent to your email.",
        "success"
    )

    return redirect(
        url_for("auth.verify_otp")
    )


# ==========================================================
# RESET PASSWORD
# ==========================================================

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

    # Completely clear the password reset flow.
    session.pop(
        "password_reset_flow",
        None
    )

    session.pop(
        "password_reset_user_id",
        None
    )

    session.pop(
        "password_reset_verified",
        None
    )

    session.pop(
        "password_reset_expires_at",
        None
    )

    return redirect(
        url_for("auth.login")
    )