"""Update problem prompt

Revision ID: e03a74b56b33
Revises: 44140ab1610c
Create Date: 2026-04-29 07:41:49.535867

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e03a74b56b33"
down_revision: Union[str, None] = "44140ab1610c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UPDATES = {
    "Problem": "U poglavlju Rešenje je potrebno opisati koji su  problemi nastali tokom izrade rada. Ukoliko ih nije bilo, potrebno je to eksplicitno navesti.",
}


ORIGINALS = {
    "Problem": "Potrebno je opisati koji su problemi nastali tokom izrade rada. Ukoliko ih nije bilo, potrebno je to eksplicitno navesti.",
}


def upgrade() -> None:
    conn = op.get_bind()
    stmt = sa.text("""
        UPDATE academic_writing_schema.rule
        SET description = :desc
        WHERE name = :name
    """)

    for name, desc in UPDATES.items():
        conn.execute(stmt, {"name": name, "desc": desc})


def downgrade() -> None:
    conn = op.get_bind()
    stmt = sa.text("""
        UPDATE academic_writing_schema.rule
        SET description = :desc
        WHERE name = :name
    """)

    for name, desc in ORIGINALS.items():
        conn.execute(stmt, {"name": name, "desc": desc})
