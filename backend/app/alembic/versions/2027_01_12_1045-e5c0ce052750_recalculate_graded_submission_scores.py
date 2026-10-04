"""Recalculate graded submission scores weighted by rule group

Revision ID: e5c0ce052750
Revises: 9fc7c8394d28
Create Date: 2027-01-12 10:45:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e5c0ce052750"
down_revision: Union[str, None] = "9fc7c8394d28"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

MAX_RULE_GRADE = 2


def _weighted_score(values_by_group: dict, percentages: dict) -> float:
    if not values_by_group:
        return 0.0
    weights = {group: percentages.get(group) for group in values_by_group}
    if any(weight is None for weight in weights.values()) or sum(weights.values()) <= 0:
        weights = {group: 1.0 for group in values_by_group}
    total_weight = sum(weights.values())
    return sum(
        weights[group] * sum(values) / (MAX_RULE_GRADE * len(values))
        for group, values in values_by_group.items()
    ) / total_weight


def upgrade() -> None:
    conn = op.get_bind()

    submissions = conn.execute(
        sa.text(
            """
            SELECT id, assignment_id
            FROM academic_writing_schema.submission
            WHERE graded
            """
        )
    ).fetchall()

    for submission_id, assignment_id in submissions:
        rows = conn.execute(
            sa.text(
                """
                SELECT r.rule_group_id, f.final_fulfillment_value
                FROM academic_writing_schema.fulfillment f
                JOIN academic_writing_schema.feedback fb ON fb.id = f.feedback_id
                JOIN academic_writing_schema.rule r ON r.id = fb.rule_id
                WHERE f.submission_id = :submission_id
                  AND f.final_fulfillment_value IS NOT NULL
                """
            ),
            {"submission_id": submission_id},
        ).fetchall()
        if not rows:
            continue

        values_by_group: dict = {}
        for rule_group_id, value in rows:
            values_by_group.setdefault(rule_group_id, []).append(value)

        percentages = dict(
            conn.execute(
                sa.text(
                    """
                    SELECT rule_group_id, percentage_of_points_in_assignment
                    FROM academic_writing_schema.assignment_rule_group
                    WHERE assignment_id = :assignment_id
                    """
                ),
                {"assignment_id": assignment_id},
            ).fetchall()
        )

        conn.execute(
            sa.text(
                """
                UPDATE academic_writing_schema.submission
                SET achieved_points_percentage = :score
                WHERE id = :submission_id
                """
            ),
            {
                "score": _weighted_score(values_by_group, percentages),
                "submission_id": submission_id,
            },
        )


def downgrade() -> None:
    pass
