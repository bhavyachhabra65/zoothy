"""add business settings

Revision ID: d554a3ba2c3d
Revises: f503aa58abe0
Create Date: 2026-08-24 21:42:09.859082

"""

from alembic import op
import sqlalchemy as sa


revision = "d554a3ba2c3d"
down_revision = "f503aa58abe0"
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        "businesses",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False
        ),

        sa.Column(
            "business_name",
            sa.String(150),
            nullable=True
        ),

        sa.Column(
            "owner_name",
            sa.String(100),
            nullable=True
        ),

        sa.Column(
            "phone",
            sa.String(20),
            nullable=True
        ),

        sa.Column(
            "gstin",
            sa.String(15),
            nullable=True
        ),

        sa.Column(
            "address",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),

        sa.UniqueConstraint(
            "user_id"
        )
    )

    op.create_index(
        "ix_businesses_user_id",
        "businesses",
        ["user_id"],
        unique=True
    )


def downgrade():

    op.drop_index(
        "ix_businesses_user_id",
        table_name="businesses"
    )

    op.drop_table(
        "businesses"
    )