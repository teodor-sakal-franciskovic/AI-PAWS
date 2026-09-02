"""Move student group membership from user.group_id to group_student

A student can now belong to a different group on each course they're part
of, instead of one group system-wide, but must never be in two groups on
the *same* course. course_id is denormalized onto group_student (from the
group's course_group link) so a unique constraint on (course_id,
student_id) lets the database itself enforce that invariant, closing the
race window a plain check-then-insert would leave open.

Existing memberships are preserved in the new join table before the old
column is dropped. A membership whose group has no course_group link (or
more than one, which the app never actually creates) is skipped rather
than guessed at.

Revision ID: 5279cc587926
Revises: 0f8109ca8543
Create Date: 2027-01-12 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5279cc587926"
down_revision: Union[str, None] = "0f8109ca8543"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "group_student",
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["academic_writing_schema.group.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["academic_writing_schema.user.id"]),
        sa.ForeignKeyConstraint(["course_id"], ["academic_writing_schema.course.id"]),
        sa.PrimaryKeyConstraint("group_id", "student_id"),
        sa.UniqueConstraint(
            "course_id", "student_id", name="uq_group_student_course_student"
        ),
        schema="academic_writing_schema",
    )

    op.execute(
        """
        INSERT INTO academic_writing_schema.group_student (group_id, student_id, course_id)
        SELECT DISTINCT ON (u.group_id, u.id) u.group_id, u.id, cg.course_id
        FROM academic_writing_schema."user" AS u
        JOIN academic_writing_schema.course_group AS cg ON cg.group_id = u.group_id
        WHERE u.group_id IS NOT NULL
        ORDER BY u.group_id, u.id, cg.course_id
        """
    )

    op.drop_constraint(
        "user_group_id_fkey",
        "user",
        schema="academic_writing_schema",
        type_="foreignkey",
    )
    op.drop_column("user", "group_id", schema="academic_writing_schema")


def downgrade() -> None:
    op.add_column(
        "user",
        sa.Column("group_id", sa.Integer(), nullable=True),
        schema="academic_writing_schema",
    )
    op.create_foreign_key(
        "user_group_id_fkey",
        "user",
        "group",
        ["group_id"],
        ["id"],
        source_schema="academic_writing_schema",
        referent_schema="academic_writing_schema",
    )

    op.execute(
        """
        UPDATE academic_writing_schema."user" AS u
        SET group_id = gs.group_id
        FROM academic_writing_schema.group_student AS gs
        WHERE gs.student_id = u.id
        """
    )

    op.drop_table("group_student", schema="academic_writing_schema")
