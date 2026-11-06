"""Rename submission.achieved_points_percentage to fulfillment_ratio, since it holds a 0-1 value

Revision ID: a6d4e2b9c013
Revises: f3c8a51d7e92
Create Date: 2027-01-12 12:45:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a6d4e2b9c013"
down_revision: Union[str, None] = "f3c8a51d7e92"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "submission",
        "achieved_points_percentage",
        new_column_name="fulfillment_ratio",
        schema="academic_writing_schema",
    )


def downgrade() -> None:
    op.alter_column(
        "submission",
        "fulfillment_ratio",
        new_column_name="achieved_points_percentage",
        schema="academic_writing_schema",
    )
