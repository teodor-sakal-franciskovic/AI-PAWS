"""Modify include in prompt

Revision ID: 65423653cca8
Revises: e38838f1fc32
Create Date: 2025-12-29 10:17:05.998355

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "65423653cca8"
down_revision: Union[str, None] = "e38838f1fc32"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    rule_names = [
        "Gramatika i pravopis",
        "Strane reči",
        "Skraćenice",
        "Dužina rada",
        "Argumentacija",
    ]

    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE academic_writing_schema.rule
            SET include_in_prompt = TRUE
            WHERE name = ANY(:rule_names)
            """
        ),
        {"rule_names": rule_names},
    )


def downgrade() -> None:
    rule_names = [
        "Gramatika i pravopis",
        "Strane reči",
        "Skraćenice",
        "Dužina rada",
        "Argumentacija",
    ]

    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE academic_writing_schema.rule
            SET include_in_prompt = FALSE
            WHERE name = ANY(:rule_names)
            """
        ),
        {"rule_names": rule_names},
    )
