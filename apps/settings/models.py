from datetime import datetime, timezone

from core.extensions import db


class Business(db.Model):

    __tablename__ = "businesses"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True,
        index=True
    )

    business_name = db.Column(
        db.String(150),
        nullable=True
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    gstin = db.Column(
        db.String(15),
        nullable=True
    )

    address = db.Column(
        db.Text,
        nullable=True
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