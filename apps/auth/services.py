from werkzeug.security import check_password_hash, generate_password_hash

from apps.auth.models import User
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