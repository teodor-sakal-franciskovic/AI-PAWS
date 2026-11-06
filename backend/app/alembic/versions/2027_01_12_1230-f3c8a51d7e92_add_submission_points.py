"""Add submission_points and fill it for existing evaluative submissions

Revision ID: f3c8a51d7e92
Revises: d7a2e91c4b36
Create Date: 2027-01-12 12:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f3c8a51d7e92"
down_revision: Union[str, None] = "d7a2e91c4b36"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "academic_writing_schema"
MAX_RULE_GRADE = 2


def _weighted_score(values, percentages):
    values_by_group = {}
    for rule_group_id, value in values:
        values_by_group.setdefault(rule_group_id, []).append(value)
    weights = {group: percentages.get(group) for group in values_by_group}
    if any(weight is None for weight in weights.values()) or sum(weights.values()) <= 0:
        weights = {group: 1.0 for group in values_by_group}
    total_weight = sum(weights.values())
    return sum(
        weights[group] / total_weight * sum(group_values) / (MAX_RULE_GRADE * len(group_values))
        for group, group_values in values_by_group.items()
    )


def _points(ratio, max_points):
    if ratio is None or max_points is None:
        return None
    return round(ratio * max_points, 2)


def upgrade() -> None:
    op.create_table(
        "submission_points",
        sa.Column(
            "submission_id",
            sa.Integer(),
            sa.ForeignKey(f"{SCHEMA}.submission.id"),
            primary_key=True,
        ),
        sa.Column("max_points", sa.Float(), nullable=True),
        sa.Column("ai_suggested_points", sa.Float(), nullable=True),
        sa.Column("final_points", sa.Float(), nullable=True),
        sa.Column(
            "updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()
        ),
        schema=SCHEMA,
    )

    conn = op.get_bind()
    submissions = conn.execute(
        sa.text(
            f"""
            SELECT s.id, s.graded, s.achieved_points_percentage, a.id AS assignment_id,
                   a.percentage_of_points_in_course, c.max_amount_of_points
            FROM {SCHEMA}.submission s
            JOIN {SCHEMA}.assignment a ON a.id = s.assignment_id
            LEFT JOIN {SCHEMA}.course c ON c.id = a.course_id
            JOIN {SCHEMA}.submission_mode m ON m.id = a.submission_mode_id
            WHERE s.status = 'COMPLETED' AND m.name = 'Evaluative mode'
            """
        )
    ).all()
    if not submissions:
        return

    percentages = {}
    for row in conn.execute(
        sa.text(
            f"SELECT assignment_id, rule_group_id, percentage_of_points_in_assignment FROM {SCHEMA}.assignment_rule_group"
        )
    ):
        percentages.setdefault(row.assignment_id, {})[row.rule_group_id] = (
            row.percentage_of_points_in_assignment
        )

    grades = {}
    for row in conn.execute(
        sa.text(
            f"""
            SELECT f.submission_id, r.id AS rule_id, r.rule_group_id,
                   f.initial_fulfillment_value, f.final_fulfillment_value
            FROM {SCHEMA}.fulfillment f
            JOIN {SCHEMA}.feedback fb ON fb.id = f.feedback_id
            JOIN {SCHEMA}.rule r ON r.id = fb.rule_id
            ORDER BY fb.id
            """
        )
    ):
        grades.setdefault(row.submission_id, {})[row.rule_id] = row

    insert = sa.text(
        f"""
        INSERT INTO {SCHEMA}.submission_points
            (submission_id, max_points, ai_suggested_points, final_points)
        VALUES (:submission_id, :max_points, :ai_suggested_points, :final_points)
        """
    )
    for submission in submissions:
        max_points = None
        if (
            submission.max_amount_of_points is not None
            and submission.percentage_of_points_in_course is not None
        ):
            max_points = round(
                submission.max_amount_of_points
                * submission.percentage_of_points_in_course
                / 100,
                2,
            )
        rules = list(grades.get(submission.id, {}).values())
        assignment_percentages = percentages.get(submission.assignment_id, {})
        ai_values = [
            (rule.rule_group_id, rule.initial_fulfillment_value)
            for rule in rules
            if rule.initial_fulfillment_value is not None
        ]
        ai_ratio = _weighted_score(ai_values, assignment_percentages) if ai_values else None
        final_ratio = submission.achieved_points_percentage if submission.graded else None
        conn.execute(
            insert,
            {
                "submission_id": submission.id,
                "max_points": max_points,
                "ai_suggested_points": _points(ai_ratio, max_points),
                "final_points": _points(final_ratio, max_points),
            },
        )


def downgrade() -> None:
    op.drop_table("submission_points", schema=SCHEMA)
