"""Replace the rule's short description with a generated, more precise one

Revision ID: d7a2e91c4b36
Revises: b19c4f7e2d80
Create Date: 2027-01-12 12:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d7a2e91c4b36"
down_revision: Union[str, None] = "b19c4f7e2d80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PREVIOUS_FIELD_LINE = "- short_description: at most 15 words, summarising the rule for display"

NEW_FIELD_LINE = "- generated_description: the instructor's description, for students and instructors to read. If it is already clear, return it word for word. Reword only the parts that are vague or ambiguous, so that they say the same thing more precisely. Never make it stricter or looser, and add no examples or conditions the instructor did not state."

PREVIOUS_LANGUAGE_LINE = "grade lines and short_description in the language"

NEW_LANGUAGE_LINE = "grade lines and generated_description in the language"

REPLACE_TEXT = sa.text(
    """
    UPDATE academic_writing_schema.prompt_template
    SET system_text = REPLACE(system_text, :old_text, :new_text)
    WHERE purpose = 'Rule Compilation'
    """
)

CLEAR_DESCRIPTIONS = "UPDATE academic_writing_schema.rule SET {column} = NULL"


def upgrade() -> None:
    op.alter_column(
        "rule",
        "short_description",
        new_column_name="generated_description",
        schema="academic_writing_schema",
    )
    op.execute(CLEAR_DESCRIPTIONS.format(column="generated_description"))
    conn = op.get_bind()
    conn.execute(
        REPLACE_TEXT, {"old_text": PREVIOUS_FIELD_LINE, "new_text": NEW_FIELD_LINE}
    )
    conn.execute(
        REPLACE_TEXT,
        {"old_text": PREVIOUS_LANGUAGE_LINE, "new_text": NEW_LANGUAGE_LINE},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        REPLACE_TEXT, {"old_text": NEW_FIELD_LINE, "new_text": PREVIOUS_FIELD_LINE}
    )
    conn.execute(
        REPLACE_TEXT,
        {"old_text": NEW_LANGUAGE_LINE, "new_text": PREVIOUS_LANGUAGE_LINE},
    )
    op.execute(CLEAR_DESCRIPTIONS.format(column="generated_description"))
    op.alter_column(
        "rule",
        "generated_description",
        new_column_name="short_description",
        schema="academic_writing_schema",
    )
