"""Modify chapter grading aspect

Revision ID: 44140ab1610c
Revises: 25d850ad8745
Create Date: 2026-04-08 13:55:16.773644
"""

from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "44140ab1610c"
down_revision: Union[str, None] = "25d850ad8745"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove (chapter_id=3, grading_aspect_id=0)
    op.execute(
        """
        DELETE FROM academic_writing_schema.chapter_grading_aspect
        WHERE chapter_id = 3 AND grading_aspect_id = 9
        """
    )

    op.execute(
        """
        INSERT INTO academic_writing_schema.chapter_grading_aspect (chapter_id, grading_aspect_id)
        VALUES (2, 9)
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM academic_writing_schema.chapter_grading_aspect
        WHERE chapter_id = 2 AND grading_aspect_id = 9
        """
    )

    op.execute(
        """
        INSERT INTO academic_writing_schema.chapter_grading_aspect (chapter_id, grading_aspect_id)
        VALUES (3, 9)
        """
    )
