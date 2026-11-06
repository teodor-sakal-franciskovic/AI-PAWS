"""Add max_points and updated_at to user_course_points and fill it from submission_points

Revision ID: b8e3f6a1d245
Revises: a6d4e2b9c013
Create Date: 2027-01-12 13:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b8e3f6a1d245"
down_revision: Union[str, None] = "a6d4e2b9c013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "academic_writing_schema"


def upgrade() -> None:
    op.add_column(
        "user_course_points", sa.Column("max_points", sa.Float(), nullable=True), schema=SCHEMA
    )
    op.add_column(
        "user_course_points",
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.execute(
        f"""
        INSERT INTO {SCHEMA}.user_course_points (course_id, user_id, achieved_points, max_points)
        SELECT latest.course_id, latest.user_id,
               ROUND(SUM(CASE WHEN latest.graded THEN COALESCE(latest.final_points, 0) ELSE 0 END)::numeric, 2),
               ROUND(SUM(COALESCE(latest.max_points, 0))::numeric, 2)
        FROM (
            SELECT DISTINCT ON (s.user_id, s.assignment_id)
                   a.course_id, s.user_id, s.graded, sp.max_points, sp.final_points
            FROM {SCHEMA}.submission s
            JOIN {SCHEMA}.assignment a ON a.id = s.assignment_id
            JOIN {SCHEMA}.submission_mode m ON m.id = a.submission_mode_id
            LEFT JOIN {SCHEMA}.submission_points sp ON sp.submission_id = s.id
            WHERE s.status = 'COMPLETED' AND m.name = 'Evaluative mode' AND a.course_id IS NOT NULL
            ORDER BY s.user_id, s.assignment_id, s.submitted_at DESC, s.id DESC
        ) latest
        GROUP BY latest.course_id, latest.user_id
        ON CONFLICT (course_id, user_id) DO UPDATE
        SET achieved_points = EXCLUDED.achieved_points, max_points = EXCLUDED.max_points
        """
    )


def downgrade() -> None:
    op.drop_column("user_course_points", "updated_at", schema=SCHEMA)
    op.drop_column("user_course_points", "max_points", schema=SCHEMA)
