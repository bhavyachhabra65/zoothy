import secrets
from datetime import datetime, timedelta, timezone

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from apps.auth.models import PasswordResetOTP, User
from core.extensions import db


class AuthService:

    @staticmethod
    def register(data):

        existing_user = User.query.filter_by(
            email=data.email
        ).first()

        if existing_user:
            return None, "An account with this email already exists."

        user = User(
            name=data.name,
            email=data.email,
            password_hash=generate_password_hash(data.password)
        )

        db.session.add(user)
        db.session.commit()

        return user, None

    @staticmethod
    def authenticate(email, password):

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

    # ======================================================
    # OTP
    # ======================================================

    @staticmethod
    def generate_otp():

        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def _create_password_reset_otp(user):

        # Invalidate all previous unused OTPs
        PasswordResetOTP.query.filter_by(
            user_id=user.id,
            is_used=False
        ).update(
            {
                PasswordResetOTP.is_used: True
            },
            synchronize_session=False
        )

        otp = AuthService.generate_otp()

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        )

        otp_record = PasswordResetOTP(
            user_id=user.id,
            otp_hash=generate_password_hash(otp),
            expires_at=expires_at
        )

        db.session.add(otp_record)
        db.session.commit()

        return otp_record, otp

    @staticmethod
    def create_password_reset_otp(email):

        email = email.strip().lower()

        user = User.query.filter_by(
            email=email
        ).first()

        if not user or not user.is_active:
            return None, None

        otp_record, otp = (
            AuthService._create_password_reset_otp(
                user
            )
        )

        return user, otp

    @staticmethod
    def resend_password_reset_otp(user_id):

        user = db.session.get(
            User,
            user_id
        )

        if not user or not user.is_active:
            return None, None

        otp_record, otp = (
            AuthService._create_password_reset_otp(
                user
            )
        )

        return user, otp

    @staticmethod
    def verify_password_reset_otp(user_id, otp):

        record = (
            PasswordResetOTP.query
            .filter_by(
                user_id=user_id,
                is_used=False
            )
            .order_by(
                PasswordResetOTP.created_at.desc()
            )
            .first()
        )

        if not record:
            return False

        now = datetime.now(timezone.utc)

        if now >= record.expires_at:
            return False

        if record.attempts >= 5:
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

    # ======================================================
    # RESET PASSWORD
    # ======================================================

    @staticmethod
    def reset_password(user_id, password):

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