"""Move percentage_of_points_in_assignment from rule_group to assignment_rule_group

Rule groups are now reusable across assignments/courses (created and managed
independently via /rule_groups), so the percentage a rule group contributes
to a specific assignment can no longer live on the rule_group row itself -
it belongs on the assignment<->rule_group link.

Revision ID: 7943cfe3a965
Revises: 2b2eb71aa17d
Create Date: 2026-08-19 14:04:09.086234

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7943cfe3a965"
down_revision: Union[str, None] = "2b2eb71aa17d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assignment_rule_group",
        sa.Column("percentage_of_points_in_assignment", sa.Float(), nullable=True),
        schema="academic_writing_schema",
    )
    op.execute(
        """
        UPDATE academic_writing_schema.assignment_rule_group arg
        SET percentage_of_points_in_assignment = rg.percentage_of_points_in_assignment
        FROM academic_writing_schema.rule_group rg
        WHERE rg.id = arg.rule_group_id
        """
    )
    op.drop_column(
        "rule_group", "percentage_of_points_in_assignment", schema="academic_writing_schema"
    )


def downgrade() -> None:
    op.add_column(
        "rule_group",
        sa.Column("percentage_of_points_in_assignment", sa.Float(), nullable=True),
        schema="academic_writing_schema",
    )
    op.execute(
        """
        UPDATE academic_writing_schema.rule_group rg
        SET percentage_of_points_in_assignment = arg.percentage_of_points_in_assignment
        FROM academic_writing_schema.assignment_rule_group arg
        WHERE arg.rule_group_id = rg.id
        """
    )
    op.drop_column(
        "assignment_rule_group",
        "percentage_of_points_in_assignment",
        schema="academic_writing_schema",
    )
