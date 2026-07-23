"""Style rules upgrade

Revision ID: 25d850ad8745
Revises: b393c0eafe41
Create Date: 2026-04-07 17:13:14.725787

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "25d850ad8745"
down_revision: Union[str, None] = "b393c0eafe41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


RULE_UPDATES = {
    "Konciznost rečenice": "Svaka rečenica mora sadržati jednu i samo jednu jasno izdvojivu poentu. Ukoliko rečenica sadrži više nezavisnih tvrdnji, objašnjenja ili zaključaka koji mogu postojati kao zasebne rečenice, smatra se da pravilo nije ispoštovano.",
    "Jasnoća rečenica": "Svaka rečenica treba biti nedvosmislena, lako razumljiva i logično strukturirana. Rečenice koje sadrže neprecizne izraze (npr. 'neki', 'određeni', 'takvi'), nejasne reference ili zahtevaju dodatno tumačenje ne ispunjavaju ovo pravilo.",
    "Zarezi": "Zarez se obavezno koristi uz 'a' i 'ali', zabranjen je uz 'i' i 'ili', koristi se kod nabrajanja, za razdvajanje nezavisnih iskaza u istoj rečenici i obavezan je u apoziciji. Pravilo treba primenjivati isključivo kada postoji jasna gramatička greška; ne navoditi primere gde je upotreba zareza opciona ili stilistički prihvatljiva.",
    "Interpunkcija": "Izbegavati uzvičnike; duže crtice koriste se za umetnute komentare, kraće za spajanje reči, a tačka-zarez za pauzu dužu od zareza a kraću od tačke, posebno kada druga klauzula proširuje ili objašnjava prvu. Potrebno je obratiti pažnju da li se liste posmatraju kao deo rečenice, tako da se nakon nabrajanja koriste odgovarajući zarezi i završna tačka. Pravilo se primenjuje na nivou celog teksta, a ne izolovanih primera.",
    "Organizacija paragrafa": "Paragraf treba da ima uvodnu rečenicu koja ističe glavnu ideju, rečenice koje je dosledno razrađuju objašnjenjima, primerima ili dokazima, i zaključnu rečenicu koja sumira implikacije ili povezuje sa narednim paragrafom. Nije dozvoljeno indirektno referisanje na pojmove iz prethodnih paragrafa bez njihovog jasnog imenovanja (npr. korišćenje izraza poput 'oni', 'takvi', 'ovakvi' bez eksplicitnog konteksta).",
    "Nekonciznost": "Treba izbegavati korišćenje generičkih, neinformativnih i bespotrebnih reči ili fraza (npr. 'savremeno', 'različiti', 'takvi', 'određeni', 'u današnje vreme') koje ne doprinose značenju rečenice. Prisustvo ovakvih izraza smatra se kršenjem pravila.",
}


RULE_ORIGINALS = {
    "Konciznost rečenice": "Svaka rečenica mora sadržati jednu i samo jednu poentu.",
    "Jasnoća rečenica": "Svaka rečenica treba biti nedvosmislena, lako razumljiva i logično strukturirana, bez suvišne složenosti ili nepreciznih formulacija.",
    "Zarezi": "Zarez se obavezno koristi uz a i ali, zabranjen je uz i i ili, koristi se kod nabrajanja, za razdvajanje nezavisnih iskaza u istoj rečenici i obavezan je u apoziciji.",
    "Interpunkcija": "Izbegavati uzvičnike; duže crtice koriste se za umetnute komentare, kraće za spajanje reči, a tačka-zarez za pauzu dužu od zareza a kraću od tačke, posebno kada druga klauzula proširuje ili objašnjava prvu.",
    "Organizacija paragrafa": "Paragraf treba da ima uvodnu rečenicu koja ističe glavnu ideju, rečenice koje je dosledno razrađuju objašnjenjima, primerima ili dokazima, i zaključnu rečenicu koja sumira implikacije ili povezuje sa narednim paragrafom.",
    "Nekonciznost": "Treba izbegavati korišćenje generičkih i bespotrebnih reči u tekstu.",
}


# --- PROMPT INJECTION ---
INSERT_TEXT = """Ukoliko uočiš da se student ponovo suočava sa problemima koji su već identifikovani u prethodnim radovima, obavezno:
- eksplicitno naglasi da se greška ponavlja,
- pruži konkretnije i direktnije smernice za ispravku,
- i posveti više pažnje i detalja tim pravilima.

Za pravila koja su ranije bila problematična, budi stroži prilikom evaluacije.

Za pravila koja predstavljaju jake strane studenta, možeš dati kraće obrazloženje, osim ako postoji regresija.

Ukoliko primetiš napredak u odnosu na prethodno znanje, kratko ga istakni.
"""


TARGET_PURPOSES = [
    "Initial Interactive",
    "Additional Interactive",
    "Evaluative",
]


def upgrade() -> None:
    conn = op.get_bind()

    stmt = sa.text("""
        UPDATE academic_writing_schema.rule
        SET description = :desc
        WHERE name = :name
    """)

    for name, desc in RULE_UPDATES.items():
        conn.execute(stmt, {"name": name, "desc": desc})

    prompt_stmt = sa.text("""
        UPDATE academic_writing_schema.prompt_template
        SET system_text = REPLACE(
            system_text,
            '{student_knowledge}',
            '{student_knowledge}\n\n' || :injection
        )
        WHERE purpose = :purpose
        AND system_text NOT LIKE '%' || :injection || '%'
    """)

    for purpose in TARGET_PURPOSES:
        conn.execute(
            prompt_stmt, {"injection": INSERT_TEXT.strip(), "purpose": purpose}
        )


def downgrade() -> None:
    conn = op.get_bind()

    stmt = sa.text("""
        UPDATE academic_writing_schema.rule
        SET description = :desc
        WHERE name = :name
    """)

    for name, desc in RULE_ORIGINALS.items():
        conn.execute(stmt, {"name": name, "desc": desc})

    prompt_stmt = sa.text("""
        UPDATE academic_writing_schema.prompt_template
        SET system_text = REPLACE(
            system_text,
            '{student_knowledge}\n\n' || :injection,
            '{student_knowledge}'
        )
        WHERE purpose = :purpose
    """)

    for purpose in TARGET_PURPOSES:
        conn.execute(
            prompt_stmt, {"injection": INSERT_TEXT.strip(), "purpose": purpose}
        )
