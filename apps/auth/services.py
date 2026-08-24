import secrets

from datetime import datetime, timedelta, timezone

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from apps.auth.models import EmailOTP, User
from core.extensions import db


class AuthService:

    OTP_EXPIRY_MINUTES = 10
    OTP_MAX_ATTEMPTS = 5

    REGISTRATION_OTP = "registration"
    PASSWORD_RESET_OTP = "password_reset"

    # ==========================================================
    # REGISTRATION
    # ==========================================================

    @staticmethod
    def register(data):

        existing_user = User.query.filter_by(
            email=data.email
        ).first()

        if existing_user:

            if not existing_user.is_active:
                return (
                    existing_user,
                    "This email is already registered but not verified."
                )

            return (
                None,
                "An account with this email already exists."
            )

        user = User(
            name=data.name,
            email=data.email,
            password_hash=generate_password_hash(
                data.password
            ),
            is_active=False
        )

        db.session.add(user)
        db.session.commit()

        return user, None

    # ==========================================================
    # LOGIN
    # ==========================================================

    @staticmethod
    def authenticate(
        email,
        password
    ):

        email = email.strip().lower()

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:
            return None

        if not user.is_active:
            return None

        if not check_password_hash(
            user.password_hash,
            password
        ):
            return None

        return user

    # ==========================================================
    # OTP
    # ==========================================================

    @staticmethod
    def generate_otp():

        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def _create_otp(
        user,
        purpose
    ):

        EmailOTP.query.filter_by(
            user_id=user.id,
            purpose=purpose,
            is_used=False
        ).update(
            {
                EmailOTP.is_used: True
            },
            synchronize_session=False
        )

        otp = AuthService.generate_otp()

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=AuthService.OTP_EXPIRY_MINUTES
            )
        )

        otp_record = EmailOTP(
            user_id=user.id,
            purpose=purpose,
            otp_hash=generate_password_hash(otp),
            expires_at=expires_at
        )

        db.session.add(otp_record)
        db.session.commit()

        return otp_record, otp

    @staticmethod
    def create_otp(
        user,
        purpose
    ):

        if not user or not user.is_active and purpose == AuthService.PASSWORD_RESET_OTP:
            return None

        _, otp = AuthService._create_otp(
            user,
            purpose
        )

        return otp

    @staticmethod
    def verify_otp(
        user_id,
        purpose,
        otp
    ):

        record = (
            EmailOTP.query
            .filter_by(
                user_id=user_id,
                purpose=purpose,
                is_used=False
            )
            .order_by(
                EmailOTP.created_at.desc()
            )
            .first()
        )

        if not record:
            return False

        now = datetime.now(timezone.utc)

        if now >= record.expires_at:
            return False

        if record.attempts >= AuthService.OTP_MAX_ATTEMPTS:
            return False

        record.attempts += 1

        valid = check_password_hash(
            record.otp_hash,
            otp
        )

        if valid:
            record.is_used = True

        db.session.commit()

        return valid

    @staticmethod
    def resend_otp(
        user_id,
        purpose
    ):

        user = db.session.get(
            User,
            user_id
        )

        if not user:
            return None, None

        if (
            purpose == AuthService.PASSWORD_RESET_OTP
            and not user.is_active
        ):
            return None, None

        _, otp = AuthService._create_otp(
            user,
            purpose
        )

        return user, otp


    # ==========================================================
    # PASSWORD RESET
    # ==========================================================

    @staticmethod
    def create_password_reset_otp(
        email
    ):

        email = email.strip().lower()

        user = User.query.filter_by(
            email=email
        ).first()

        if not user or not user.is_active:
            return None, None

        otp = AuthService.create_otp(
            user,
            AuthService.PASSWORD_RESET_OTP
        )

        return user, otp

    @staticmethod
    def verify_password_reset_otp(
        user_id,
        otp
    ):

        return AuthService.verify_otp(
            user_id,
            AuthService.PASSWORD_RESET_OTP,
            otp
        )

    @staticmethod
    def resend_password_reset_otp(
        user_id
    ):

        return AuthService.resend_otp(
            user_id,
            AuthService.PASSWORD_RESET_OTP
        )

    @staticmethod
    def reset_password(
        user_id,
        password
    ):

        user = db.session.get(
            User,
            user_id
        )

        if not user or not user.is_active:
            return False

        user.password_hash = generate_password_hash(
            password
        )

        db.session.commit()

        return True

    @staticmethod
    def activate_user(user_id):

        user = db.session.get(
            User,
            user_id
        )

        if not user:
            return None

        user.is_active = True

        db.session.commit()

        return user


    @staticmethod
    def get_user(user_id):

        return db.session.get(
            User,
            user_id
        )