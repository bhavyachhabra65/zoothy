from datetime import datetime, timezone

from core.extensions import db


class Product(db.Model):

    __tablename__ = "products"

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

    name = db.Column(
        db.String(150),
        nullable=False
    )

    sku = db.Column(
        db.String(100),
        nullable=True
    )

    hsn_sac = db.Column(
        db.String(20),
        nullable=True
    )

    unit = db.Column(
        db.String(30),
        nullable=False,
        default="pcs"
    )

    purchase_price = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=0
    )

    selling_price = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=0
    )

    gst_rate = db.Column(
        db.Numeric(5, 2),
        nullable=False,
        default=0
    )

    opening_stock = db.Column(
        db.Numeric(14, 3),
        nullable=False,
        default=0
    )

    description = db.Column(
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
