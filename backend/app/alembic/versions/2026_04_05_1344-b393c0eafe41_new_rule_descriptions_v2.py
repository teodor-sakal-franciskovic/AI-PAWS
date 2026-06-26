"""New rule descriptions v2

Revision ID: b393c0eafe41
Revises: c5fca9659cb7
Create Date: 2026-04-05 13:44:37.018070

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b393c0eafe41"
down_revision: Union[str, None] = "c5fca9659cb7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
UPDATES = {
    "Skraćenice": "Prilikom uvođenja skraćenice, mora biti naveden pun termin od kojeg je nastala. U daljem tekstu, mora se koristi skraćenica, a ne pun termin (izuzetak su naslovi poglavlja). Ne smeju biti definisane skraćenice koje kasnije nisu korišćene. Ne mešati skraćenice sa engleskim rečima definisanim u zagradama prilikom revidiranja ovog pravila.",
    "Argumentacija": "Sve tvrdnje koje nisu opšte prihvaćene moraju biti podržane citatima ili argumentovane rezultatima rada. Literatura mora biti citirana u okviru rečenice, najbliže tvrdnji koju podržava. Citati moraju biti deo rečenice.",
}

ORIGINALS = {
    "Skraćenice": "Prilikom uvođenja skraćenice, mora biti naveden pun termin od kojeg je nastala. U daljem tekstu, mora se koristi skraćenica, a ne pun termin (izuzetak su naslovi poglavlja). Ne smeju biti definisane skraćenice koje kasnije nisu korišćene.",
    "Argumentacija": "Sve tvrdnje moraju biti podržane citatima ili argumentovane rezultatima rada. Literatura mora biti citirana u okviru rečenice, najbliže tvrdnji koju podržava. Citati moraju biti deo rečenice.",
}


def upgrade() -> None:
    conn = op.get_bind()

    # --- Update rule descriptions ---
    stmt = sa.text("""
        UPDATE academic_writing_schema.rule
        SET description = :desc
        WHERE name = :name
    """)

    for name, desc in UPDATES.items():
        conn.execute(stmt, {"name": name, "desc": desc})

    conn.execute(
        sa.text("""
        UPDATE academic_writing_schema.prompt_template
        SET system_text = REPLACE(
            system_text,
            'Takođe, prilikom davanja',
            'Ukoliko neko pravilo nije ispoštovano, navesti bar jedan primer zašto nije. Takođe, prilikom davanja'
        )
        WHERE purpose = 'Evaluative'
    """)
    )


def downgrade() -> None:
    conn = op.get_bind()

    # --- Revert rule descriptions ---
    stmt = sa.text("""
        UPDATE academic_writing_schema.rule
        SET description = :desc
        WHERE name = :name
    """)

    for name, desc in ORIGINALS.items():
        conn.execute(stmt, {"name": name, "desc": desc})

    # --- Remove inserted sentence ---
    conn.execute(
        sa.text("""
        UPDATE academic_writing_schema.prompt_template
        SET system_text = REPLACE(
            system_text,
            'Ukoliko neko pravilo nije ispoštovano, navesti bar jedan primer zašto nije. Takođe, prilikom davanja',
            'Takođe, prilikom davanja'
        )
        WHERE purpose = 'Evaluative'
    """)
    )
