"""Show the fix in evaluative feedback on an unrelated topic

Revision ID: b19c4f7e2d80
Revises: e5b71d3a9c26
Create Date: 2027-01-12 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b19c4f7e2d80"
down_revision: Union[str, None] = "e5b71d3a9c26"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PREVIOUS_INSTRUCTION = "Say why the grade was reduced, citing a quote or saying the element is absent, what is missing, and one concrete example of what would fix it."

NEW_INSTRUCTION = "Say why the grade was reduced, citing a quote or saying the element is absent, and what is missing. Then show the fix with one concrete example on an unrelated topic, never rewriting the student's own text or supplying what their paper should say."

REPLACE_INSTRUCTION = sa.text(
    """
    UPDATE academic_writing_schema.prompt_template
    SET system_text = REPLACE(system_text, :old_text, :new_text)
    WHERE purpose = 'Evaluative'
    """
)


def upgrade() -> None:
    op.get_bind().execute(
        REPLACE_INSTRUCTION,
        {"old_text": PREVIOUS_INSTRUCTION, "new_text": NEW_INSTRUCTION},
    )


def downgrade() -> None:
    op.get_bind().execute(
        REPLACE_INSTRUCTION,
        {"old_text": NEW_INSTRUCTION, "new_text": PREVIOUS_INSTRUCTION},
    )
