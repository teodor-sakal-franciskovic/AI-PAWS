"""Add created_at and updated_at to rule_group

Revision ID: ddc22d945f7d
Revises: 7943cfe3a965
Create Date: 2026-08-19 14:04:22.301330

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ddc22d945f7d"
down_revision: Union[str, None] = "7943cfe3a965"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "rule_group",
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="academic_writing_schema",
    )
    op.add_column(
        "rule_group",
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=True),
        schema="academic_writing_schema",
    )


def downgrade() -> None:
    op.drop_column("rule_group", "updated_at", schema="academic_writing_schema")
    op.drop_column("rule_group", "created_at", schema="academic_writing_schema")
