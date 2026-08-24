from datetime import datetime, timezone

from flask_login import UserMixin

from core.extensions import db


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(255),
        nullable=False,
        unique=True,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


class EmailOTP(db.Model):

    __tablename__ = "email_otps"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    purpose = db.Column(
        db.String(30),
        nullable=False,
        index=True
    )

    otp_hash = db.Column(
        db.String(255),
        nullable=False
    )

    expires_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False
    )

    attempts = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    is_used = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )