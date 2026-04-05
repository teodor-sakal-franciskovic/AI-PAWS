"""Rule updates

Revision ID: c5fca9659cb7
Revises: 2bd052143563
Create Date: 2026-04-02 20:30:00.230932

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c5fca9659cb7"
down_revision: Union[str, None] = "2bd052143563"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UPDATES = {
    "Strane reči": "Strane reči treba da budu napisane kurzivom (italic). Ako je neka reč prevedena na srpski jezik, strani naziv je potrebno da se nađe u zagradi (npr. korišćenjem nasumične šume (eng. random forest))",
    "Širi problem": "Širi problem koji rad obrađuje treba da bude jasno predstavljen. Čitalac ne bi trebalo da mora da istražuje dodatne izvore da bi shvatio zašto je tema relevantna.",
    "Pozicioniranje užeg problema u širem kontekstu": "Tekst treba najpre da predstavi širi problem, a zatim jasno da prikaže kako se konkretan uži problem uklapa u taj širi problem.",
}


ORIGINALS = {
    "Strane reči": "Strane reči treba da budu napisane kurzivom (italic). Ako je neka reč prevedena na srpski jezik, strani naziv je potrebno da se nađe u zagradi.",
    "Širi problem": "Širi problem koji rad obrađuje treba da bude jasno predstavljen tako da se odmah razume njegov kontekst i važnost. Čitalac ne bi trebalo da mora da istražuje dodatne izvore da bi shvatio zašto je tema relevantna.",
    "Pozicioniranje užeg problema u širem kontekstu": "Tekst treba najpre da predstavi opšti okvir oblasti, a zatim jasno da prikaže kako se konkretan uži problem logično uklapa u taj širi kontekst.",
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
