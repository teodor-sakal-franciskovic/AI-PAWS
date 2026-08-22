"""Add is_active to course, rule_group and language for soft-delete support

Revision ID: 55b9470ae168
Revises: 302796cbbc88
Create Date: 2026-08-22 11:40:15.753949

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "55b9470ae168"
down_revision: Union[str, None] = "302796cbbc88"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table in ("course", "rule_group", "language"):
        op.add_column(
            table,
            sa.Column(
                "is_active",
                sa.Boolean(),
                server_default=sa.text("true"),
                nullable=False,
            ),
            schema="academic_writing_schema",
        )


def downgrade() -> None:
    for table in ("course", "rule_group", "language"):
        op.drop_column(table, "is_active", schema="academic_writing_schema")
