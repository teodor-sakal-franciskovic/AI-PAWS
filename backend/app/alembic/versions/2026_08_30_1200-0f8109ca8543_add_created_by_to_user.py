"""Add created_by to user

Records which instructor registered a student, for audit purposes on
batch registration.

Revision ID: 0f8109ca8543
Revises: 453b91fc8278
Create Date: 2026-08-30 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0f8109ca8543"
down_revision: Union[str, None] = "453b91fc8278"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("created_by", sa.Integer(), nullable=True),
        schema="academic_writing_schema",
    )
    op.create_foreign_key(
        "user_created_by_fk",
        "user",
        "user",
        ["created_by"],
        ["id"],
        source_schema="academic_writing_schema",
        referent_schema="academic_writing_schema",
    )


def downgrade() -> None:
    op.drop_constraint(
        "user_created_by_fk",
        "user",
        schema="academic_writing_schema",
        type_="foreignkey",
    )
    op.drop_column("user", "created_by", schema="academic_writing_schema")
