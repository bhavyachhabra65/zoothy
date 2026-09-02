"""add suppliers

Revision ID: 9a6350527342
Revises: 20293fd41efb
Create Date: 2026-09-02 18:52:58.994585

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9a6350527342"
down_revision = "20293fd41efb"
branch_labels = None
depends_on = None


def upgrade():
    # Add notes to suppliers.
    # Increase phone length from 10 to 20.
    # Increase email length from 254 to 255.
    # Remove the old contact_person field.
    # Remove the old unique constraint on (user_id, name).

    with op.batch_alter_table("suppliers", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("notes", sa.Text(), nullable=True)
        )

        batch_op.alter_column(
            "phone",
            existing_type=sa.VARCHAR(length=10),
            type_=sa.String(length=20),
            existing_nullable=True,
        )

        batch_op.alter_column(
            "email",
            existing_type=sa.VARCHAR(length=254),
            type_=sa.String(length=255),
            existing_nullable=True,
        )

        batch_op.drop_constraint(
            batch_op.f("uq_supplier_user_name"),
            type_="unique",
        )

        batch_op.drop_column("contact_person")


def downgrade():
    with op.batch_alter_table("suppliers", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "contact_person",
                sa.VARCHAR(length=100),
                autoincrement=False,
                nullable=True,
            )
        )

        batch_op.create_unique_constraint(
            batch_op.f("uq_supplier_user_name"),
            ["user_id", "name"],
            postgresql_nulls_not_distinct=False,
        )

        batch_op.alter_column(
            "email",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=254),
            existing_nullable=True,
        )

        batch_op.alter_column(
            "phone",
            existing_type=sa.String(length=20),
            type_=sa.VARCHAR(length=10),
            existing_nullable=True,
        )

        batch_op.drop_column("notes")