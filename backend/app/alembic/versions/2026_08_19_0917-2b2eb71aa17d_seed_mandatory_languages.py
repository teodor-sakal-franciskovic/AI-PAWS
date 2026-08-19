"""Seed mandatory languages

Revision ID: 2b2eb71aa17d
Revises: ab5ab8a31bfc
Create Date: 2026-08-19 09:17:47.582492

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2b2eb71aa17d"
down_revision: str | None = "ab5ab8a31bfc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MANDATORY_LANGUAGES = [
    ("Serbian", "SR"),
    ("Greek", "EL"),
    ("English", "EN"),
]

ADDITIONAL_LANGUAGES = [
    ("German", "DE"),
    ("French", "FR"),
    ("Spanish", "ES"),
    ("Italian", "IT"),
    ("Croatian", "HR"),
    ("Macedonian", "MK"),
    ("Bulgarian", "BG"),
    ("Romanian", "RO"),
    ("Albanian", "SQ"),
    ("Turkish", "TR"),
]

SEED_LANGUAGES = MANDATORY_LANGUAGES + ADDITIONAL_LANGUAGES


def upgrade() -> None:
    op.execute(
        """
        SELECT setval(
            pg_get_serial_sequence('academic_writing_schema.language', 'id'),
            (SELECT COALESCE(MAX(id), 0) FROM academic_writing_schema.language) + 1,
            false
        )
        """
    )

    for name, short_name in SEED_LANGUAGES:
        op.execute(
            f"""
            INSERT INTO academic_writing_schema.language (name, short_name)
            SELECT '{name}', '{short_name}'
            WHERE NOT EXISTS (
                SELECT 1 FROM academic_writing_schema.language WHERE name = '{name}'
            )
            """
        )


def downgrade() -> None:
    names = ", ".join(f"'{name}'" for name, _ in SEED_LANGUAGES)
    op.execute(f"DELETE FROM academic_writing_schema.language WHERE name IN ({names})")
