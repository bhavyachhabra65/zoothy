from datetime import datetime, timezone

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from flask_login import (
    login_user,
    logout_user
)

from apps.auth.email import send_otp
from apps.auth.schemas import RegisterData
from apps.auth.services import AuthService
from apps.auth.validators import (
    validate_login,
    validate_registration
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

    remember = (
        request.form.get("remember") == "1"
    )

    login_user(
        user,
        remember=remember
    )

    session.permanent = True

    session["last_activity"] = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    next_page = request.args.get(
        "next"
    )

    if (
        next_page
        and next_page.startswith("/")
    ):

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

        if user and not user.is_active:

            session["otp_user_id"] = user.id
            session["otp_purpose"] = (
                AuthService.REGISTRATION_OTP
            )

            otp = AuthService.create_otp(
                user,
                AuthService.REGISTRATION_OTP
            )

            send_otp(
                user.email,
                otp,
                AuthService.REGISTRATION_OTP
            )

            flash(
                "We've sent a new verification code to your email.",
                "success"
            )

            return redirect(
                url_for("auth.verify_otp")
            )

        return render_template(
            "auth/register.html",
            error=error,
            name=name,
            email=email
        ), 409

    otp = AuthService.create_otp(
        user,
        AuthService.REGISTRATION_OTP
    )

    send_otp(
        user.email,
        otp,
        AuthService.REGISTRATION_OTP
    )

    session["otp_user_id"] = user.id

    session["otp_purpose"] = (
        AuthService.REGISTRATION_OTP
    )

    session["otp_expires_at"] = (
        datetime.now(
            timezone.utc
        ).timestamp()
        + (
            AuthService.OTP_EXPIRY_MINUTES
            * 60
        )
    )

    flash(
        "We've sent a verification code to your email.",
        "success"
    )

    return redirect(
        url_for("auth.verify_otp")
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

    user, otp = (
        AuthService.create_password_reset_otp(
            email
        )
    )

    session["otp_purpose"] = (
        AuthService.PASSWORD_RESET_OTP
    )

    session["otp_expires_at"] = (
        datetime.now(
            timezone.utc
        ).timestamp()
        + (
            AuthService.OTP_EXPIRY_MINUTES
            * 60
        )
    )

    if user:

        session["otp_user_id"] = user.id

        send_otp(
            user.email,
            otp,
            AuthService.PASSWORD_RESET_OTP
        )

    else:

        session.pop(
            "otp_user_id",
            None
        )

        session.pop(
            "otp_expires_at",
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

    purpose = session.get(
        "otp_purpose"
    )

    if purpose not in (
        AuthService.REGISTRATION_OTP,
        AuthService.PASSWORD_RESET_OTP
    ):

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/verify_otp.html",
        purpose=purpose,
        expires_at=session.get(
            "otp_expires_at"
        )
    )


@auth_bp.post("/verify-otp")
def verify_otp_submit():

    user_id = session.get(
        "otp_user_id"
    )

    purpose = session.get(
        "otp_purpose"
    )

    if (
        not user_id
        or purpose not in (
            AuthService.REGISTRATION_OTP,
            AuthService.PASSWORD_RESET_OTP
        )
    ):

        return redirect(
            url_for("auth.login")
        )

    otp = request.form.get(
        "otp",
        ""
    ).strip()

    valid = AuthService.verify_otp(
        user_id,
        purpose,
        otp
    )

    if not valid:

        return render_template(
            "auth/verify_otp.html",
            error="The code is incorrect or has expired.",
            purpose=purpose,
            expires_at=session.get(
                "otp_expires_at"
            )
        ), 400

    # ------------------------------------------------------
    # REGISTRATION
    # ------------------------------------------------------

    if purpose == AuthService.REGISTRATION_OTP:

        user = AuthService.activate_user(
            user_id
        )

        if not user:
            return redirect(
                url_for("auth.login")
            )

        login_user(
            user
        )

        session.permanent = True

        session["last_activity"] = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        session.pop(
            "otp_user_id",
            None
        )

        session.pop(
            "otp_purpose",
            None
        )

        session.pop(
            "otp_expires_at",
            None
        )

        flash(
            "Your account has been verified successfully.",
            "success"
        )

        return redirect(
            url_for("dashboard.index")
        )

    # ------------------------------------------------------
    # PASSWORD RESET
    # ------------------------------------------------------

    session["password_reset_user_id"] = user_id

    session["password_reset_verified"] = True

    session.pop(
        "otp_user_id",
        None
    )

    session.pop(
        "otp_purpose",
        None
    )

    session.pop(
        "otp_expires_at",
        None
    )

    return redirect(
        url_for("auth.reset_password")
    )


# ==========================================================
# RESEND OTP
# ==========================================================

@auth_bp.post("/resend-otp")
def resend_otp():

    user_id = session.get(
        "otp_user_id"
    )

    purpose = session.get(
        "otp_purpose"
    )

    if (
        not user_id
        or purpose not in (
            AuthService.REGISTRATION_OTP,
            AuthService.PASSWORD_RESET_OTP
        )
    ):

        return redirect(
            url_for("auth.login")
        )

    user, otp = AuthService.resend_otp(
        user_id,
        purpose
    )

    if not user:

        return redirect(
            url_for("auth.login")
        )

    send_otp(
        user.email,
        otp,
        purpose
    )

    session["otp_expires_at"] = (
        datetime.now(
            timezone.utc
        ).timestamp()
        + (
            AuthService.OTP_EXPIRY_MINUTES
            * 60
        )
    )

    if purpose == AuthService.REGISTRATION_OTP:

        message = (
            "A new verification code has been sent to your email."
        )

    else:

        message = (
            "A new password reset code has been sent to your email."
        )

    flash(
        message,
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

    session.pop(
        "password_reset_user_id",
        None
    )

    session.pop(
        "password_reset_verified",
        None
    )

    session.pop(
        "otp_user_id",
        None
    )

    session.pop(
        "otp_purpose",
        None
    )

    session.pop(
        "otp_expires_at",
        None
    )

    flash(
        "Your password has been reset successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )