"""Add short_name to group

Revision ID: 302796cbbc88
Revises: ddc22d945f7d
Create Date: 2026-08-19 14:04:29.652498

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "302796cbbc88"
down_revision: Union[str, None] = "ddc22d945f7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "group",
        sa.Column("short_name", sa.String(), nullable=True),
        schema="academic_writing_schema",
    )


def downgrade() -> None:
    op.drop_column("group", "short_name", schema="academic_writing_schema")
