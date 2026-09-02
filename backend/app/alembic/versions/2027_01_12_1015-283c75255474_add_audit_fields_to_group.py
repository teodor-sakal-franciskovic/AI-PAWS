"""Add audit fields to group

Matches the created_by/created_at/updated_by/updated_at pattern already
used on course and rule_group, needed for GET /groups/{group_id}.

Revision ID: 283c75255474
Revises: 5279cc587926
Create Date: 2027-01-12 10:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "283c75255474"
down_revision: Union[str, None] = "5279cc587926"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "group",
        sa.Column("created_by", sa.Integer(), nullable=True),
        schema="academic_writing_schema",
    )
    op.add_column(
        "group",
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="academic_writing_schema",
    )
    op.add_column(
        "group",
        sa.Column("updated_by", sa.Integer(), nullable=True),
        schema="academic_writing_schema",
    )
    op.add_column(
        "group",
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=True),
        schema="academic_writing_schema",
    )
    op.create_foreign_key(
        "group_created_by_fkey",
        "group",
        "user",
        ["created_by"],
        ["id"],
        source_schema="academic_writing_schema",
        referent_schema="academic_writing_schema",
    )
    op.create_foreign_key(
        "group_updated_by_fkey",
        "group",
        "user",
        ["updated_by"],
        ["id"],
        source_schema="academic_writing_schema",
        referent_schema="academic_writing_schema",
    )


def downgrade() -> None:
    op.drop_constraint(
        "group_updated_by_fkey",
        "group",
        schema="academic_writing_schema",
        type_="foreignkey",
    )
    op.drop_constraint(
        "group_created_by_fkey",
        "group",
        schema="academic_writing_schema",
        type_="foreignkey",
    )
    op.drop_column("group", "updated_at", schema="academic_writing_schema")
    op.drop_column("group", "updated_by", schema="academic_writing_schema")
    op.drop_column("group", "created_at", schema="academic_writing_schema")
    op.drop_column("group", "created_by", schema="academic_writing_schema")
