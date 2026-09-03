"""update inventory stock fields

Revision ID: 31c32318b0bb
Revises: 96bcc4d94126
Create Date: 2026-09-03 09:32:26.912593

"""
from decimal import Decimal

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "31c32318b0bb"
down_revision = "96bcc4d94126"
branch_labels = None
depends_on = None


def upgrade():
    # ---------------------------------------------------------
    # 1. Add resulting_quantity temporarily as nullable.
    # ---------------------------------------------------------
    with op.batch_alter_table("inventory_movements", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "resulting_quantity",
                sa.Numeric(precision=14, scale=3),
                nullable=True,
            )
        )

    # ---------------------------------------------------------
    # 2. Backfill resulting_quantity from movement history.
    #
    # Movements are processed chronologically for each
    # user/product pair.
    # ---------------------------------------------------------
    bind = op.get_bind()

    movements = sa.table(
        "inventory_movements",
        sa.column("id", sa.Integer()),
        sa.column("user_id", sa.Integer()),
        sa.column("product_id", sa.Integer()),
        sa.column("movement_type", sa.String(length=20)),
        sa.column("quantity", sa.Numeric(precision=14, scale=3)),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column(
            "resulting_quantity",
            sa.Numeric(precision=14, scale=3),
        ),
    )

    rows = bind.execute(
        sa.select(
            movements.c.id,
            movements.c.user_id,
            movements.c.product_id,
            movements.c.movement_type,
            movements.c.quantity,
        ).order_by(
            movements.c.user_id,
            movements.c.product_id,
            movements.c.created_at,
            movements.c.id,
        )
    ).mappings().all()

    balances = {}

    for row in rows:
        key = (row["user_id"], row["product_id"])

        balance = balances.get(key, Decimal("0"))

        quantity = Decimal(row["quantity"] or 0)

        if row["movement_type"] in ("add", "opening"):
            balance += quantity

        elif row["movement_type"] == "remove":
            balance -= quantity

        balances[key] = balance

        bind.execute(
            movements.update()
            .where(movements.c.id == row["id"])
            .values(resulting_quantity=balance)
        )

    # ---------------------------------------------------------
    # 3. resulting_quantity is now fully populated, so make
    #    it NOT NULL.
    # ---------------------------------------------------------
    with op.batch_alter_table("inventory_movements", schema=None) as batch_op:
        batch_op.alter_column(
            "resulting_quantity",
            existing_type=sa.Numeric(precision=14, scale=3),
            nullable=False,
        )

    # ---------------------------------------------------------
    # 4. Rename low_stock_threshold -> low_stock_level.
    #
    # This preserves all existing threshold values.
    # ---------------------------------------------------------
    with op.batch_alter_table("inventory_stock", schema=None) as batch_op:
        batch_op.alter_column(
            "low_stock_threshold",
            new_column_name="low_stock_level",
            existing_type=sa.Numeric(precision=14, scale=3),
            existing_nullable=False,
        )


def downgrade():
    # ---------------------------------------------------------
    # 1. Rename low_stock_level back to low_stock_threshold.
    # ---------------------------------------------------------
    with op.batch_alter_table("inventory_stock", schema=None) as batch_op:
        batch_op.alter_column(
            "low_stock_level",
            new_column_name="low_stock_threshold",
            existing_type=sa.Numeric(precision=14, scale=3),
            existing_nullable=False,
        )

    # ---------------------------------------------------------
    # 2. Remove resulting_quantity.
    # ---------------------------------------------------------
    with op.batch_alter_table("inventory_movements", schema=None) as batch_op:
        batch_op.drop_column("resulting_quantity")