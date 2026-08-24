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
# HELPERS
# ==========================================================

def _set_otp_session(
    user_id,
    purpose
):

    session["otp_user_id"] = user_id
    session["otp_purpose"] = purpose


def _clear_otp_session():

    session.pop(
        "otp_user_id",
        None
    )

    session.pop(
        "otp_purpose",
        None
    )


def _set_last_activity():

    session.permanent = True

    session["last_activity"] = (
        datetime.now(
            timezone.utc
        ).isoformat()
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

    _set_last_activity()

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

            otp = AuthService.create_otp(
                user,
                AuthService.REGISTRATION_OTP
            )

            send_otp(
                user.email,
                otp,
                AuthService.REGISTRATION_OTP
            )

            _set_otp_session(
                user.id,
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

    _set_otp_session(
        user.id,
        AuthService.REGISTRATION_OTP
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

    if user:

        _set_otp_session(
            user.id,
            AuthService.PASSWORD_RESET_OTP
        )

        send_otp(
            user.email,
            otp,
            AuthService.PASSWORD_RESET_OTP
        )

        flash(
            "If an account exists with this email, we've sent a verification code.",
            "success"
        )

        return redirect(
            url_for("auth.verify_otp")
        )

    flash(
        "If an account exists with this email, we've sent a verification code.",
        "success"
    )

    return redirect(
        url_for("auth.forgot_password")
    )


# ==========================================================
# VERIFY OTP
# ==========================================================

@auth_bp.get("/verify-otp")
def verify_otp():

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

    otp_record = AuthService.get_active_otp(
        user_id,
        purpose
    )

    if not otp_record:

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/verify_otp.html",
        purpose=purpose,
        expires_at=otp_record.expires_at.timestamp()
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

        otp_record = AuthService.get_active_otp(
            user_id,
            purpose
        )

        return render_template(
            "auth/verify_otp.html",
            error="The code is incorrect or has expired.",
            purpose=purpose,
            expires_at=(
                otp_record.expires_at.timestamp()
                if otp_record
                else None
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

            _clear_otp_session()

            return redirect(
                url_for("auth.login")
            )

        login_user(
            user
        )

        _set_last_activity()

        _clear_otp_session()

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

    _clear_otp_session()

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

        _clear_otp_session()

        return redirect(
            url_for("auth.login")
        )

    send_otp(
        user.email,
        otp,
        purpose
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

        session.pop(
            "password_reset_user_id",
            None
        )

        session.pop(
            "password_reset_verified",
            None
        )

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

    flash(
        "Your password has been reset successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )