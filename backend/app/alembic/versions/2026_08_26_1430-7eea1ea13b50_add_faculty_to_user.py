"""Add faculty to user

Revision ID: 7eea1ea13b50
Revises: 55b9470ae168
Create Date: 2026-08-26 14:30:36.884050

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7eea1ea13b50"
down_revision: Union[str, None] = "55b9470ae168"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("faculty", sa.String(), nullable=True),
        schema="academic_writing_schema",
    )


def downgrade() -> None:
    op.drop_column("user", "faculty", schema="academic_writing_schema")
