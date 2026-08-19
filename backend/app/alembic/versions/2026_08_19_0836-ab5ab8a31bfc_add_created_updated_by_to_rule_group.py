"""Add created_by and updated_by to rule_group

Revision ID: ab5ab8a31bfc
Revises: daad5b46aa4d
Create Date: 2026-08-19 08:36:40.026290

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ab5ab8a31bfc"
down_revision: Union[str, None] = "daad5b46aa4d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "rule_group",
        sa.Column("created_by", sa.Integer(), nullable=True),
        schema="academic_writing_schema",
    )
    op.add_column(
        "rule_group",
        sa.Column("updated_by", sa.Integer(), nullable=True),
        schema="academic_writing_schema",
    )
    op.create_foreign_key(
        "rule_group_created_by_fkey",
        "rule_group",
        "user",
        ["created_by"],
        ["id"],
        source_schema="academic_writing_schema",
        referent_schema="academic_writing_schema",
    )
    op.create_foreign_key(
        "rule_group_updated_by_fkey",
        "rule_group",
        "user",
        ["updated_by"],
        ["id"],
        source_schema="academic_writing_schema",
        referent_schema="academic_writing_schema",
    )


def downgrade() -> None:
    op.drop_constraint(
        "rule_group_updated_by_fkey",
        "rule_group",
        schema="academic_writing_schema",
        type_="foreignkey",
    )
    op.drop_constraint(
        "rule_group_created_by_fkey",
        "rule_group",
        schema="academic_writing_schema",
        type_="foreignkey",
    )
    op.drop_column("rule_group", "updated_by", schema="academic_writing_schema")
    op.drop_column("rule_group", "created_by", schema="academic_writing_schema")
