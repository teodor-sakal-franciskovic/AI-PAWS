"""Remove student memberships of already soft-deleted groups

Deleting a group now also removes its group_student rows; this cleans up
the rows left behind by groups deleted before that change.

Revision ID: 9fc7c8394d28
Revises: 283c75255474
Create Date: 2027-01-12 10:30:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9fc7c8394d28"
down_revision: Union[str, None] = "283c75255474"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM academic_writing_schema.group_student
        WHERE group_id IN (
            SELECT id FROM academic_writing_schema."group" WHERE is_deleted
        )
        """
    )


def downgrade() -> None:
    pass
