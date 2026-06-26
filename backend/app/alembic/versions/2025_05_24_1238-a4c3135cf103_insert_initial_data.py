"""Insert initial data

Revision ID: a4c3135cf103
Revises: 37eb12aabd39
Create Date: 2025-05-24 12:38:32.770133

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a4c3135cf103"
down_revision: Union[str, None] = "37eb12aabd39"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "INSERT INTO academic_writing_schema.role (id, name) VALUES (1, 'Student'), (2, 'TA')"
    )
    op.execute(
        "INSERT INTO academic_writing_schema.submission_mode (id, name, description) "
        "VALUES (1, 'Interactive mode', 'Mode in which students receive information about the quality of their submitted chapters.'),"
        " (2, 'Evaluative mode', 'Mode in which students receive grades (and reasons behind them) for their submitted chapters.')"
    )
    op.execute(
        "INSERT INTO academic_writing_schema.chapter (id, name) VALUES (1, 'Problem'), (2, 'Teorijske osnove'), (3, 'Rešenje'), (4, 'Rezultati')"
    )
    op.execute(
        "INSERT INTO academic_writing_schema.grading_aspect (id, name) VALUES "
        "(1, 'Širi kontekst problema'), (2, 'Konkretizovan fokus rada'), "
        "(3, 'Koncepti neophodni za razumevanje problema'), (4, 'Koncepti neophodni za razumevanje rešenja'), "
        "(5, 'Opis cilja rešenja'), (6, 'Opis strukture sistema'), (7, 'Detalji svake celine u strukturi rešenja'), (8, 'Šta ne treba da bude sadržaj poglavlja Rešenje'), (9, 'Sinhronizacija pogavlja Problem, Teorijske osnove i Rešenje'), "
        "(10, 'Cilj evaluacije'), (11, 'Reproducibilnost eksperimenta'), (12, 'Opis rezultata'), "
        "(13, 'Tehnički aspekti'), (14, 'Rečenice'), (15, 'Paragrafi'), (16, 'Konciznost')"
    )
    op.execute(
        "INSERT INTO academic_writing_schema.chapter_grading_aspect(chapter_id, grading_aspect_id) VALUES "
        "(1, 1), (1, 2), (1, 13), (1, 14), (1, 15), (1, 16), "
        "(2, 3), (2, 4), (2, 13), (2, 14), (2, 15), (2, 16), "
        "(3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 13), (3, 14), (3, 15), (3, 16), "
        "(4, 10), (4, 11), (4, 12), (4, 13), (4, 14), (4, 15), (4, 16)"
    )
    op.execute(
        "INSERT INTO academic_writing_schema.rule(name, description, include_in_prompt, grading_aspect_id) VALUES "
        "('Širi problem', 'Jasno je istaknut širi problem koji se obrađuje u radu. Čitalac nema potrebe da dodatno istražuje o problemu da bi video značaj rada.', true, 1), "
        "('Osnovni koncepti', 'Definisani su osnovni koncepti za razumevanja problema. Definisani koncepti - nije potrebno dodatno istraživanje da bi se tekst razumeo. Definisani koncepti - nijedan definisani koncept nije suvišan.', true, 1), "
        "('Značaj rešenja', 'Istaknuto je zašto je priloženo rešenje značajno za društvo. Objašnjava se koja je motivacija iza rešenja i problema koji se rešava. Naveden je slučaj korišćenja tog rešenja.', true, 1), "
        "('Pozicioniranje užeg problema u širem kontekstu', 'Primer za softversko inženjerstvo: - Širi kontekst: U poslednje dve decenije, agilne metodologije poput Scrum-a i Kanban-a postale su standard u razvoju softvera... - Uži kontekst: U ovom radu fokusiramo se na optimizaciju komunikacije i saradnje u distribuiranim agilnim timovima, ...; Primer za AI: - Širi kontekst: Veštačka inteligencija značajno je unapredila različite domene, poput obrade prirodnog jezika, prepoznavanja slika i optimizacije složenih sistema.... - Uži kontekst: Ovaj rad istražuje kako se algoritmi zasnovani na dubokom učenju mogu prilagoditi da pruže interpretabilne rezultate u medicinskoj dijagnostici...', true, 2), "
        "('Opis fokusa rada', 'Jasno je očekivano ponašanje rešenja i kada/kako se koristi.', true, 2), "
        "('Opis fokusa rešenja', 'Istaknute su konkretne interesne grupe koje bi rešenje koristile i na koji način.', true, 2), "
        "('Opis problema domena', 'Detaljniji opis domena problema iz koga sledi skup zahteva koje rešenje treba da ispuni. Aplikativna rešenja - koji su ciljevi krajnjih korisnika?  Tehnička rešenja - koje tehničke probleme rešenje treba da reši? Mašinsko učenje - kako prevesti problem u problem mašinskog učenja? Nakon čitanja opisa problema domena, čitalac bi trebalo da razume sve aspekte o problemu (šta treba rešiti, šta su nedostaci postojećih rešenja), bez bilo kakvih nejasnoća o istom. Primer: Rad se bavi primenom kompjuterske vizije na problem detekcije stepena očne retinopatije. Pojašnjeno je šta je problem tradicionalnog pregleda kod lekara. Iz ove analize izvučeni su zahtevi koje sistem treba da ispuni (npr., minimalan prag tačnosti, brzina analize). Takođe je pojašnjeno kako lekari donose odluke kad vrše pregled - uvidi na šta se domenski eksperti fokusiraju prilikom analize slike pomažu kreiranju modela kompjuterske vizije, kao i analizi grešaka modela.', true, 3), "
        "('Zahtevi', 'Potrebno je definisati/opisati zahteve koje bi rešenje trebalo da reši. Zahtevi su zapravo lista stavki koje predstavljaju problem.', true, 3), "
        "('Opis drugačijih rešenja', 'Razmatranje mogućih (alternativnih) rešenja. Koncizna sumarizacija, ali ne i detaljan pregled.', true, 4), "
        "('Argumentacija odabranog rešenja', 'Argumentacija zbog čega ste se opredelili za rešenje koje predstavljate u radu (samo teorijski). Ovo bi trebalo da se naslanja na prethodnu tezu.', true, 4), "
        "('Opis koncepata rešenja', 'Opis koncepata korišćenih u rešenju (tehnologije, modeli). Nakon čitanja opisa koncepata rešenja, čitalac bi trebalo da ima sve potrebno znanje za razumevanje dobijenog rezultata rešenja.', true, 4), "
        "('Opis rešenja na opštijem nivou', 'Pojednostavljeni slučajevi korišćenja, bez definisanja koraka procesa: npr. Koje potrebe tvoj softver ispunjava?; Kakav ulaz se očekuje, kakav izlaz se dobija (za svaku potrebu)?', true, 5), "
        "('Inicijalno predstavljanje strukture sistema', 'Pipeline u ML-u ili Moduli (feature u kontekstu package by feature pristupa paketiranja) u SW inženjerstvu (u zavisnosti koja se oblast obrađuje). Ovaj opis je jedno od sledeća dva: (1) kratak paragraf u slučaju jednostavne metodologije koja se ne sastoji od više koraka obrade ili (2) predstavljen grafički (npr. dijagram komponenti).', true, 6),"
        "('Opis svake celine strukture rešenja', 'Rad prelazi detalje svake celine sistema tek nakon opisa cilja i strukture sistema. Ovo može podrazumevati na koji način su sakupljani, obrađivani i analizirani podaci, na koji način je građen i analizirani sistem...', true, 7), "
        "('Preciznost', 'Dovoljno detalja - čitalac razume postupak i nema dodatnih pitanja.', true, 7), "
        "('Visok nivo apstrakcije', 'Rešenje treba da bude objašnjeno na visokom nivou apstrakcije (npr. ne treba opisivati isečke koda).', true, 8), "
        "('Teorijske osnove', 'Ne treba opisivati kako neka procedura, algoritam ili nešto treće funkcioniše, već kako je korišćeno.', true, 8), "
        "('Problem', 'Ne treba opisivati problem koji se rešava u radu. Opis problema, koji su nastali tokom izrade rešenja, je potrebno opisati (npr. zašto je bilo problematično prikupiti adekvatan skup podataka).', true, 8), "
        "('Definisani koncepti', 'Ni u jednom od ovih poglavlja ne postoje nedefinisani koncepti (čitalac može da razume problem i rešenje i nema dodatnih pitanja).', true, 9), "
        "('Višak koncepata', 'Poglavlje Teorijske osnove ne definiše koncepte koji nisu relevantni za razumevanje rada.', true, 9), "
        "('Opis rešenja koncepata', 'Iz poglavlja Rešenje je jasno kako je svaki od zahteva sistema realizovan. U slučaju da neki od zahteva nije realizovan, treba istaknuti da će se o tome pričati u narednom poglavlju Rezultati.', true, 9), "
        "('Konciznost', 'Jasno je izraženo šta je to što želimo da pokažemo evaluacijom (šta je poželjan/nepoželjan ishod evaluacije).', true, 10), "
        "('Dovoljno detalja', 'Moguće bi bilo reprodukovati eksperiment na osnovu njegovog opisa (dato je dovoljno detalja): (1) opisana je procedura, (2) opisane su metrike performanse, (3) definisan je kriterijum uspeha (npr. rešenje treba da pređe x% F-meru da bi bilo primenljivo u praksi ili smatra se da je zahtev ispunjen ako...)', true, 11), "
        "('Vizuelni prikaz rezultata', 'Rezultati su jasno predstavljeni (odgovarajuće tabele, grafikoni i slike). Tekst prisutan kod tabela, grafikona i slika treba da da informacije o istim i da se autor ne ponavlja. Treba ih koristiti kada postoji mnogo podataka, prikazuju se podaci kroz vreme, poredi se više izvora informacija, ukazuju se šabloni, trendovi, itd.)', false, 12), "
        "('Vreme pisanja', 'Potrebno je koristiti prošlo vreme.', true, 12), "
        "('Struktura opisa rezultata', 'Tekst poglavlja logično i jasno tumači predstavljene rezultate. Kombinovanje više rezultata radi diskusije o istim ili prezentovanje i objašnjavanje jednog rezultata i taj proces se iterativno ponavlja za svaki dobijeni rezultat. Sortirati po značaju ili hronološki.', true, 12), "
        "('Diskusija o rezultatima', 'Komentarisane su prednosti i ograničenja rešenja. Istaknuto je u kojim kontekstima je rešenje korisno i pouzdano, a u kojim nije. Komentarisano je šta nije pokriveno rešenjem (koji zahtevi nisu ispunjeni). Ako postoje, porediti sa ostalim radovima koji obrađuju sličnu tematiku.', true, 12), "
        "('Finalni paragraf', 'Sintezirati sve pronalaske (rezultate) u jednom paragrafu na kraju poglavlja.', true, 12), "
        "('Gramatika i pravopis', 'Izuzetak generalnom uputstvu. Proceniti koliko se često javljaju greške i odlučiti da li je osoba omašila gramatiku i/ili pravopis ili nije.', false, 13), "
        "('Strane reči', 'Paziti da strane reči treba da budu napisane kurzivom. Ako je neka reč prevedena, stavljamo strani naziv u zagradi (npr. Korišćenjem metode nasumične šume (eng. random forest)...).', false, 13), "
        "('Skraćenice', 'Prilikom uvođenja skraćenice, naveden je pun termin od koga je nastala. U daljem tekstu je korišćena skraćenica, a ne pun termin (izuzetak su naslovi poglavlja). Nisu definisane skraćenice koje kasnije nisu korišćene.', false, 13), "
        "('Dužina rada', 'Maksimalno tri stranice (sa literaturom) u zadatom formatu. Između 200 i 300 reči u poglavlju Problem. Između 250 i 500 reči u poglavlju Teorijske osnove. Između 400 i 800 reči u poglavlju Rešenje. Između 400 i 800 reči u poglavlju Rezultati.', false, 13), "
        "('Razdvajanje teksta', 'Koristiti spacing umesto praznih redova.', false, 13), "
        "('Reference', 'Click-able su reference ka izvorima i vode ka istim. Unutar rečenice, nikako izvan.', false, 13), "
        "('Poglavlja i potpoglavlja', 'Click-able su brojevi i/ili nazivi (pot)poglavlja i vode ka istim.', false, 13), "
        "('Jednačina', 'Deo su rečenice, koristiti equation alat za kreiranje istih.', false, 13), "
        "('Slike i tabele', 'Svaka mora biti pozvana iz teksta (ne sme da postoji tabela ili slika koje su u radu, a ne referenciraju se). Click-able su i vode ka istim. Moraju biti numerisane i imati naslov. Naslov slike je ispod slike, a tabele iznad tabele, na istoj stranici u oba slučaja. Pozivanje na iste se vrši pomoću enumeracije (nikako na slici ispod, već npr. na tabeli 1 se može videti...).', false, 13), "
        "('Argumentacija', 'Sve tvrdnje su podržane citatima ili argumentovane rezultatima rada. Literatura je citirana u okviru rečenice, najbliže tvrdnji koju podržava. Na primer, tvrdnja 1 [1] i tvrdnja 2 [2]. umesto tvrdnja 1 i tvrdnja 2 [1][2]. Važno je da su citati deo rečenice. Na primer, zabranjeno je Tvrdnja 1 i tvrdnja 2. [1][2].', false, 13), "
        "('Konciznost rečenice', '1 rečenica = 1 poenta. Heuristika: rečenice sa više poenti tipično sadrže dosta zareza i veznika. Heuristika: rečenice sa više poenti su tipično dugačke. Heuristika: ako rečenica ima puno zareza jer je u pitanju nabrajanje, razmotrite upotrebu liste.', true, 14), "
        "('Jasnoća rečenica', 'Heuristika: Tekst ne sadrži preterano formalne i kompleksne reči koje otežavaju razumevanje. Heuristika: Rečenice su tako konstruisane da je subjekat (o kome/o čemu) pri početku, a glagol (šta subjekat radi) pri kraju rečenice. Heuristika: Glagol nije predaleko od subjekta. Heuristika: Korišćeni su jaki glagoli.', true, 14), "
        "('Aktiv i pasiv', 'Aktiv bi trebalo da je default opcija i da se koristi gde god nema očiglednog razloga da se koristi pasiv. Pasiv se koristi kada je izvršilac radnje očigledan ili nebitan, jer se stavlja fokus na rezultate ili proces, a ne na izvršioca. Takođe se koristi kada se navodi opšta činjenica. Npr. Eksperimenti su sprovedeni u kontrolisanim uslovima. - znamo da su autori izvršili eksperiment, ne treba ih navoditi. Nova metoda je primenjena na uzorku od 200 ispitanika. - bitno je da je metoda primenjena, a ne ko ju je primenio. Temperatura ključanja vode je određena pritiskom. - opšta činjenica.', true, 14), "
        "('Početak rečenice', 'Ne kretati rečenicu sa rečima `a`, `ili`, `i`, kao ni sa brojevima (npr. 2 eksperimenta su pokrenuta...).', true, 14), "
        "('Sadržaj rečenice', 'Rečenice ne treba da sadrže obraćanje čitaocu direktno. Ne treba koristiti žargone i slengove. Rečenice treba da budu formalnog tipa.', true, 14), "
        "('Korišćenje vremena', 'Prezent se koristi prilikom iskazivanja činjenica. Perfekt se koristi prilikom spominjanja sopstvenih rezultata.', true, 14), "
        "('Zarezi', 'Obavezni kod reči `a`, `ali`, zabranjeni kod reči `i`, `ili`. Koristiti ih kod nabrajanja. Ako postoje dva nezavisna iskaza u jednoj rečenici, razdvojiti ih zarezom (iako bi ovo trebalo da budu dve odvojene rečenice u većini slučajeva). Obavezni kod apozicije (primer: Jovan, sin Miloša, voli voće.).', true, 14), "
        "('Interpunkcija', 'Izbegavati uzvičnike. Dashes (duže crtice) - dodatni komentar u rečenici (npr. ... rezultati su ti i ti -- ovo ukazuje na to da...). Hyphens (kraće crtice) - spajanje reči/grupa reči (npr. crveno-beli, jug-jugoistok...). Tačka-zarez: trebalo bi da predstavlja dužu pauzu od zareza, ali kraću od tačke. Primeri korišćenja su: druga kauzula proširuje ili nastavlja prvu, objašnjenje sekvence akcija.', true, 14), "
        "('Konciznost paragrafa', '1 paragraf = 1 tema. Jedna tema ne treba da bude razbijena na više paragrafa. 1) da li je tok misli jasan, 2) da li rečenice čine kohezivnu celinu', true, 15), "
        "('Organizacija paragrafa', '1. Rečenica koja ističe glavnu ideju paragrafa 2. Rečenice koje razrađuju ideju paragrafa (objašnjenja/primeri/dokazi) - sve rečenice se odnose na glavnu ideju paragrafa 3. Zaključna rečenica (implikacije ideje; sumiranje/povezivanje sa 1. rečenicom; najava narednog paragrafa)', true, 15), "
        "('Konzistentnost', 'Za određeni koncept se konzistentno koristi isti termin/fraza.', true, 15), "
        "('Repetitivnost', 'Tekst nije repetitivan (primeri repetitivnosti: pojašnjavanje istog pojma/poente na dva različita mesta; tekst koji u potpunosti ponavlja ono što se nalazi na slici).', true, 16), "
        "('Bespotrebni detalji', 'Tekst ne zalazi u nepotrebne detalje (primeri nepotrebnih detalja: isečci koda koji su trivijalni, definisanje koncepata koji nisu neophodni za razumevanje teme).', true, 16), "
        "('Odnos teksta i teme rada', 'Sve što je izloženo je povezano sa temom rada - ne postoji tekst čija povezanost sa temom nije jasna.', true, 16), "
        "('Nekonciznost', 'Treba izbegavati korišćenje generičkih i bespotrebnih reči u tekstu. Primeri nekonciznih reči: 1. pridevi poput veoma/jako/donekle... 2. prazne fraze poput kao što je već rečeno,..., lako je zaključiti da..., opšte je poznato da... 3. redudantne fraze poput neočekivano iznenađenje, krajnji rezultat 4. primeri loših reči: oni, ljudi, drugim rečima, takođe poznat kao, veoma, neverovatno, samim, itd.',  true, 16), "
        "('Korišćenje ličnih zamenica', 'Izbegavati korišćenje ličnih zamenica (ja, ti, on...), radi izbegavanja subjektivnosti rada. Izuzetak su rečenice gde je nužno iskoristiti lične zamenice (npr. Ja sam intervjuisao 20 studenata...)', true, 16)"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DELETE FROM academic_writing_schema.rule")
    op.execute("DELETE FROM academic_writing_schema.chapter_grading_aspect")
    op.execute("DELETE FROM academic_writing_schema.grading_aspect")
    op.execute("DELETE FROM academic_writing_schema.chapter")
    op.execute("DELETE FROM academic_writing_schema.submission_mode")
    op.execute("DELETE FROM academic_writing_schema.role")
    # ### end Alembic commands ###
