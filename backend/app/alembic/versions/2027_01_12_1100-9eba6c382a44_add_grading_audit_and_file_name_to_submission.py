"""Add graded_by, graded_at and file_name to submission

Revision ID: 9eba6c382a44
Revises: e5c0ce052750
Create Date: 2027-01-12 11:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9eba6c382a44"
down_revision: Union[str, None] = "e5c0ce052750"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "submission",
        sa.Column("graded_by", sa.Integer(), nullable=True),
        schema="academic_writing_schema",
    )
    op.add_column(
        "submission",
        sa.Column("graded_at", sa.TIMESTAMP(), nullable=True),
        schema="academic_writing_schema",
    )
    op.add_column(
        "submission",
        sa.Column("file_name", sa.String(), nullable=True),
        schema="academic_writing_schema",
    )
    op.create_foreign_key(
        "submission_graded_by_fkey",
        "submission",
        "user",
        ["graded_by"],
        ["id"],
        source_schema="academic_writing_schema",
        referent_schema="academic_writing_schema",
    )


def downgrade() -> None:
    op.drop_constraint(
        "submission_graded_by_fkey",
        "submission",
        schema="academic_writing_schema",
        type_="foreignkey",
    )
    op.drop_column("submission", "file_name", schema="academic_writing_schema")
    op.drop_column("submission", "graded_at", schema="academic_writing_schema")
    op.drop_column("submission", "graded_by", schema="academic_writing_schema")
