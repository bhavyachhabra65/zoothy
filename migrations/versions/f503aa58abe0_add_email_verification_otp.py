"""add email verification otp

Revision ID: f503aa58abe0
Revises: 08f3f960a637
Create Date: 2026-08-24 15:41:09.247493

"""
from alembic import op
import sqlalchemy as sa


revision = "f503aa58abe0"
down_revision = "08f3f960a637"
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        "email_otps",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "purpose",
            sa.String(length=30),
            nullable=False
        ),

        sa.Column(
            "otp_hash",
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),

        sa.Column(
            "attempts",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "is_used",
            sa.Boolean(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"]
        ),

        sa.PrimaryKeyConstraint("id")
    )

    with op.batch_alter_table(
        "email_otps",
        schema=None
    ) as batch_op:

        batch_op.create_index(
            batch_op.f(
                "ix_email_otps_user_id"
            ),
            ["user_id"],
            unique=False
        )

        batch_op.create_index(
            batch_op.f(
                "ix_email_otps_purpose"
            ),
            ["purpose"],
            unique=False
        )


def downgrade():

    with op.batch_alter_table(
        "email_otps",
        schema=None
    ) as batch_op:

        batch_op.drop_index(
            batch_op.f(
                "ix_email_otps_purpose"
            )
        )

        batch_op.drop_index(
            batch_op.f(
                "ix_email_otps_user_id"
            )
        )

    op.drop_table(
        "email_otps"
    )