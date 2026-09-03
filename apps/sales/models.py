from datetime import datetime, timezone

from apps.customers.models import Customer
from core.extensions import db


class Sale(db.Model):

    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=True,
        index=True
    )

    sale_number = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )

    sale_date = db.Column(
        db.Date,
        nullable=False,
        index=True
    )

    subtotal = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=0
    )

    tax_amount = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=0
    )

    total_amount = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=0
    )

    notes = db.Column(db.Text, nullable=True)

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

    # A sale may optionally belong to one of the user's saved customers.
    # Keeping the relationship here lets the Sales list display the saved
    # customer's name instead of incorrectly falling back to Walk-in Customer.
    customer = db.relationship(
        "Customer",
        foreign_keys=[customer_id],
        lazy="joined"
    )

    items = db.relationship(
        "SaleItem",
        back_populates="sale",
        cascade="all, delete-orphan",
        order_by="SaleItem.id"
    )


class SaleItem(db.Model):

    __tablename__ = "sale_items"

    id = db.Column(db.Integer, primary_key=True)

    sale_id = db.Column(
        db.Integer,
        db.ForeignKey("sales.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    product_name = db.Column(
        db.String(150),
        nullable=False
    )

    unit = db.Column(
        db.String(30),
        nullable=False
    )

    quantity = db.Column(
        db.Numeric(14, 3),
        nullable=False
    )

    unit_price = db.Column(
        db.Numeric(14, 2),
        nullable=False
    )

    gst_rate = db.Column(
        db.Numeric(5, 2),
        nullable=False,
        default=0
    )

    tax_amount = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=0
    )

    line_total = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=0
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    sale = db.relationship(
        "Sale",
        back_populates="items"
    )
