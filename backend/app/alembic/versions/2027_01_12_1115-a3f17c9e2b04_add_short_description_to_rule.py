"""Add short_description to rule and clear placeholder prompt descriptions

Revision ID: a3f17c9e2b04
Revises: 9eba6c382a44
Create Date: 2027-01-12 11:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a3f17c9e2b04"
down_revision: Union[str, None] = "9eba6c382a44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "rule",
        sa.Column("short_description", sa.String(), nullable=True),
        schema="academic_writing_schema",
    )
    op.execute(
        """
        UPDATE academic_writing_schema.rule
        SET prompt_description = NULL
        WHERE prompt_description LIKE 'Evaluate whether: %'
        """
    )


def downgrade() -> None:
    op.drop_column("rule", "short_description", schema="academic_writing_schema")
