"""Move assigned_to_instructor from user to a per-course course_student_instructor table

A student can now be assigned to a different instructor in each course they
take, instead of having one fixed instructor across the whole system.

Revision ID: 453b91fc8278
Revises: 7eea1ea13b50
Create Date: 2026-08-26 14:30:44.853962

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "453b91fc8278"
down_revision: Union[str, None] = "7eea1ea13b50"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "course_student_instructor",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("instructor_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["academic_writing_schema.course.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["academic_writing_schema.user.id"]),
        sa.ForeignKeyConstraint(["instructor_id"], ["academic_writing_schema.user.id"]),
        sa.PrimaryKeyConstraint("course_id", "student_id"),
        schema="academic_writing_schema",
    )
    op.drop_constraint(
        "assigned_to_instructor_fk",
        "user",
        schema="academic_writing_schema",
        type_="foreignkey",
    )
    op.drop_column("user", "assigned_to_instructor", schema="academic_writing_schema")


def downgrade() -> None:
    op.add_column(
        "user",
        sa.Column("assigned_to_instructor", sa.Integer(), nullable=True),
        schema="academic_writing_schema",
    )
    op.create_foreign_key(
        "assigned_to_instructor_fk",
        "user",
        "user",
        ["assigned_to_instructor"],
        ["id"],
        source_schema="academic_writing_schema",
        referent_schema="academic_writing_schema",
    )
    op.drop_table("course_student_instructor", schema="academic_writing_schema")
