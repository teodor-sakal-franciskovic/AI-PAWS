"""Update course

Revision ID: 33ce80d3aa8b
Revises: 06612e6c11b6
Create Date: 2026-06-26 15:25:34.640587

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "33ce80d3aa8b"
down_revision: Union[str, None] = "06612e6c11b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE academic_writing_schema.role SET name = 'Instructor' WHERE id = 2"
    )
    op.drop_constraint(
        "assignment_chapter_id_fkey",
        "assignment",
        schema="academic_writing_schema",
        type_="foreignkey",
    )
    op.drop_column("assignment", "chapter_id", schema="academic_writing_schema")
    op.drop_table("chapter", schema="academic_writing_schema")
    op.add_column(
        "course",
        sa.Column("created_by", sa.Integer(), nullable=True),
        schema="academic_writing_schema",
    )
    op.add_column(
        "course",
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="academic_writing_schema",
    )
    op.add_column(
        "course",
        sa.Column("updated_by", sa.Integer(), nullable=True),
        schema="academic_writing_schema",
    )
    op.add_column(
        "course",
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=True),
        schema="academic_writing_schema",
    )
    op.create_foreign_key(
        "course_created_by_fkey",
        "course",
        "user",
        ["created_by"],
        ["id"],
        source_schema="academic_writing_schema",
        referent_schema="academic_writing_schema",
    )
    op.create_foreign_key(
        "course_updated_by_fkey",
        "course",
        "user",
        ["updated_by"],
        ["id"],
        source_schema="academic_writing_schema",
        referent_schema="academic_writing_schema",
    )
    op.drop_constraint(
        "uq_group_name", "group", schema="academic_writing_schema", type_="unique"
    )
    op.drop_constraint(
        "assigned_to_ta_fk",
        "user",
        schema="academic_writing_schema",
        type_="foreignkey",
    )
    op.drop_column("user", "assigned_to_ta", schema="academic_writing_schema")
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


def downgrade() -> None:
    op.drop_constraint(
        "assigned_to_instructor_fk",
        "user",
        schema="academic_writing_schema",
        type_="foreignkey",
    )
    op.drop_column("user", "assigned_to_instructor", schema="academic_writing_schema")
    op.add_column(
        "user",
        sa.Column("assigned_to_ta", sa.INTEGER(), autoincrement=False, nullable=True),
        schema="academic_writing_schema",
    )
    op.create_foreign_key(
        "assigned_to_ta_fk",
        "user",
        "user",
        ["assigned_to_ta"],
        ["id"],
        source_schema="academic_writing_schema",
        referent_schema="academic_writing_schema",
    )
    op.create_unique_constraint(
        "uq_group_name", "group", ["name"], schema="academic_writing_schema"
    )
    op.drop_constraint(
        "course_updated_by_fkey",
        "course",
        schema="academic_writing_schema",
        type_="foreignkey",
    )
    op.drop_constraint(
        "course_created_by_fkey",
        "course",
        schema="academic_writing_schema",
        type_="foreignkey",
    )
    op.drop_column("course", "updated_at", schema="academic_writing_schema")
    op.drop_column("course", "updated_by", schema="academic_writing_schema")
    op.drop_column("course", "created_at", schema="academic_writing_schema")
    op.drop_column("course", "created_by", schema="academic_writing_schema")
    op.create_table(
        "chapter",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id", name="chapter_pkey"),
        schema="academic_writing_schema",
    )
    op.add_column(
        "assignment",
        sa.Column("chapter_id", sa.INTEGER(), autoincrement=False, nullable=True),
        schema="academic_writing_schema",
    )
    op.create_foreign_key(
        "assignment_chapter_id_fkey",
        "assignment",
        "chapter",
        ["chapter_id"],
        ["id"],
        source_schema="academic_writing_schema",
        referent_schema="academic_writing_schema",
    )
    op.execute("UPDATE academic_writing_schema.role SET name = 'TA' WHERE id = 2")
