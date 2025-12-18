"""Upgrade rule prompts

Revision ID: e38838f1fc32
Revises: 9812170dfeec
Create Date: 2025-12-17 12:52:47.694678

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e38838f1fc32"
down_revision: Union[str, None] = "9812170dfeec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UPDATES = {
    "Gramatika i pravopis": "Tekst mora biti gramatički ispravan, bez pravopisnih grešaka.",
    "Strane reči": "Strane reči treba da budu napisane kurzivom (italic). Ako je neka reč prevedena na srpski jezik, strani naziv je potrebno da se nađe u zagradi.",
    "Skraćenice": "Prilikom uvođenja skraćenice, mora biti naveden pun termin od kojeg je nastala. U daljem tekstu, mora se koristi skraćenica, a ne pun termin (izuzetak su naslovi poglavlja). Ne smeju biti definisane skraćenice koje kasnije nisu korišćene.",
    "Argumentacija": "Sve tvrdnje moraju biti podržane citatima ili argumentovane rezultatima rada. Literatura mora biti citirana u okviru rečenice, najbliže tvrdnji koju podržava. Citati moraju biti deo rečenice.",
    "Konciznost rečenice": "Svaka rečenica mora sadržati jednu i samo jednu poentu.",
    "Jasnoća rečenica": "Svaka rečenica treba biti nedvosmislena, lako razumljiva i logično strukturirana, bez suvišne složenosti ili nepreciznih formulacija.",
    "Aktiv i pasiv": "Aktiv treba koristiti kao podrazumevanu formu, dok se pasiv upotrebljava samo kada je izvršilac radnje nebitan, očigledan ili kada je fokus na rezultatu ili opštoj činjenici.",
    "Početak rečenice": "Rečenica ne sme početi sa rečima A, Ili, I, kao ni sa brojevima.",
    "Sadržaj rečenice": "Rečenice treba da budu formalne. Ne treba da koriste žargone i slengove. Ne treba da se obraćaju čitaocu direktno.",
    "Korišćenje vremena": "Prezent se koristi prilikom iskazivanja činjenica, dok se perfekt koristi prilikom spominjanja sopstvenih rezultata.",
    "Zarezi": "Zarez se obavezno koristi uz a i ali, zabranjen je uz i i ili, koristi se kod nabrajanja, za razdvajanje nezavisnih iskaza u istoj rečenici i obavezan je u apoziciji.",
    "Interpunkcija": "Izbegavati uzvičnike; duže crtice koriste se za umetnute komentare, kraće za spajanje reči, a tačka-zarez za pauzu dužu od zareza a kraću od tačke, posebno kada druga klauzula proširuje ili objašnjava prvu.",
    "Konciznost paragrafa": "Jedan paragraf treba da opisuje jednu i samo jednu temu. Jedna tema ne treba da bude razbijena na više paragrafa.",
    "Organizacija paragrafa": "Paragraf treba da ima uvodnu rečenicu koja ističe glavnu ideju, rečenice koje je dosledno razrađuju objašnjenjima, primerima ili dokazima, i zaključnu rečenicu koja sumira implikacije ili povezuje sa narednim paragrafom.",
    "Konzistentnost": "Za određeni koncept se konzistentno koristi isti termin/fraza.",
    "Repetitivnost": "Tekst ne sme biti repetitivan, odnosno ne treba ponavljati iste pojmove, objašnjenja ili informacije već jasno iznete drugde u tekstu ili prikazane na slici.",
    "Bespotrebni detalji": "Tekst ne treba da sadrži nepotrebne detalje, poput trivijalnih isečaka koda ili definisanja koncepata koji nisu ključni za razumevanje teme.",
    "Odnos teksta i teme rada": "Sve što je izloženo mora biti povezano sa temom rada, odnosno, ne postoji tekst čija povezanost sa temom nije jasna.",
    "Nekonciznost": "Treba izbegavati korišćenje generičkih i bespotrebnih reči u tekstu.",
    "Korišćenje ličnih zamenica": "Izbegavati korišćenje ličnih zamenica radi izbegavanja subjektivnosti rada.",
    "Širi problem": "Širi problem koji rad obrađuje treba da bude jasno predstavljen tako da se odmah razume njegov kontekst i važnost. Čitalac ne bi trebalo da mora da istražuje dodatne izvore da bi shvatio zašto je tema relevantna.",
    "Osnovni koncepti": "Osnovni koncepti za razumevanje problema treba da budu jasno definisani tako da čitalac može da razume tekst bez dodatnog istraživanja. Istovremeno, svaki definisani koncept treba da bude neophodan, bez suvišnih pojmova koji ne doprinose razumevanju.",
    "Značaj rešenja": "Istaknuto je zašto je priloženo rešenje značajno za društvo. Objašnjava se koja je motivacija iza rešenja i problema koji se rešava.",
    "Pozicioniranje užeg problema u širem kontekstu": "Tekst treba najpre da predstavi opšti okvir oblasti, a zatim jasno da prikaže kako se konkretan uži problem logično uklapa u taj širi kontekst.",
    "Opis fokusa rada": "Jasno je očekivano ponašanje rešenja i kada/kako se koristi.",
    "Opis koristi rešenja": "Istaknute su konkretne interesne grupe koje bi rešenje koristile i na koji način.",
    "Opis problema domena": "Opis problema treba da pruži detaljan prikaz domena iz kojeg jasno proističu zahtevi koje rešenje mora da ispuni.",
    "Zahtevi": "Potrebno je navesti jasno definisane stavke koje opisuju šta tačno rešenje treba da omogući ili koji problem treba da otkloni.",
    "Opis drugačijih rešenja": "Tekst sažeto prikazuje moguće alternativne pristupe bez ulaska u preterane detalje.",
    "Argumentacija odabranog rešenja": "Prisutan je razlog zbog kojeg je odabrano predstavljeno rešenje u radu.",
    "Opis koncepata rešenja": "Jasno predstavljanje tehnologija, modela i pristupa koji se koriste, tako da čitalac nakon čitanja poseduje sve neophodno znanje za razumevanje rezultata rešenja.",
    "Definisani koncepti": "Svi pojmovi su jasno objašnjeni tako da čitalac može da razume problem i rešenje bez dodatnih pitanja ili nejasnoća.",
    "Višak koncepata": "Ne postoje koncepti koji nisu potrebni za razumevanje rada.",
    "Opis rešenja koncepata": "Jasno je kako je svaki od zahteva sistema realizovan.",
    "Opis rešenja na opštijem nivou": "Pojednostavljen pregled toga koje potrebe rešenje ispunjava i kakav se ulaz i izlaz očekuje, bez ulaska u detaljne korake procesa.",
    "Inicijalno predstavljanje strukture sistema": "Kratko i pregledno prikazivanje glavnih komponenti, modula ili faza rešenja.",
    "Opis svake celine strukture rešenja": "Detaljno objašnjenje svake komponente sistema tek nakon predstavljanja ukupne strukture.",
    "Preciznost": "Tekst daje dovoljno relevantnih detalja da čitalac može jasno da razume postupak bez dodatnih pitanja.",
    "Visok nivo apstrakcije": "Rešenje treba opisati na konceptualnom i opštem nivou, bez ulaska u implementacione detalje.",
    "Teorijske osnove": "Ne treba opisivati kako neka procedura, algoritam ili nešto treće funkcioniše, već kako je korišćeno.",
    "Problem": "Potrebno je opisati koji su problemi nastali tokom izrade rada. Ukoliko ih nije bilo, potrebno je to eksplicitno navesti.",
    "Konciznost": "Jasno je objašnjen poželjan, odnosno nepoželjan ishod evaluacije.",
    "Dovoljno detalja": "Na osnovu datog opisa eksperimenta u tekstu, moguće ga je reprodukovati.",
    "Vreme pisanja": "Potrebno je koristiti prošlo vreme u opisu dobijenih rezultata.",
    "Struktura opisa rezultata": "Tekst logično i jasno tumači predstavljene rezultate, sortirane po značaju ili hronološki.",
    "Diskusija o rezultatima": "Komentarisane su prednosti i ograničenja rezultata, kao i poređenje sa postojećim rešenjima.",
    "Finalni paragraf": "Potrebno je sintezirati sve rezultate u jednom paragrafu na kraju poglavlja i navesti budući rad.",
}


ORIGINALS = {
    "Širi problem": "Jasno je istaknut širi problem koji se obrađuje u radu. Čitalac nema potrebe da dodatno istražuje o problemu da bi video značaj rada.",
    "Osnovni koncepti": "Definisani su osnovni koncepti za razumevanja problema. Definisani koncepti - nije potrebno dodatno istraživanje da bi se tekst razumeo. Definisani koncepti - nijedan definisani koncept nije suvišan.",
    "Značaj rešenja": "Istaknuto je zašto je priloženo rešenje značajno za društvo. Objašnjava se koja je motivacija iza rešenja i problema koji se rešava. Naveden je slučaj korišćenja tog rešenja.",
    "Pozicioniranje užeg problema u širem kontekstu": "Primer za softversko inženjerstvo: - Širi kontekst: U poslednje dve decenije, agilne metodologije poput Scrum-a i Kanban-a postale su standard u razvoju softvera... - Uži kontekst: U ovom radu fokusiramo se na optimizaciju komunikacije i saradnje u distribuiranim agilnim timovima, ...; Primer za AI: - Širi kontekst: Veštačka inteligencija značajno je unapredila različite domene, poput obrade prirodnog jezika, prepoznavanja slika i optimizacije složenih sistema.... - Uži kontekst: Ovaj rad istražuje kako se algoritmi zasnovani na dubokom učenju mogu prilagoditi da pruže interpretabilne rezultate u medicinskoj dijagnostici...",
    "Opis fokusa rada": "Jasno je očekivano ponašanje rešenja i kada/kako se koristi.",
    "Opis fokusa rešenja": "Istaknute su konkretne interesne grupe koje bi rešenje koristile i na koji način.",
    "Opis problema domena": "Detaljniji opis domena problema iz koga sledi skup zahteva koje rešenje treba da ispuni. Aplikativna rešenja - koji su ciljevi krajnjih korisnika?  Tehnička rešenja - koje tehničke probleme rešenje treba da reši? Mašinsko učenje - kako prevesti problem u problem mašinskog učenja? Nakon čitanja opisa problema domena, čitalac bi trebalo da razume sve aspekte o problemu (šta treba rešiti, šta su nedostaci postojećih rešenja), bez bilo kakvih nejasnoća o istom. Primer: Rad se bavi primenom kompjuterske vizije na problem detekcije stepena očne retinopatije. Pojašnjeno je šta je problem tradicionalnog pregleda kod lekara. Iz ove analize izvučeni su zahtevi koje sistem treba da ispuni (npr., minimalan prag tačnosti, brzina analize). Takođe je pojašnjeno kako lekari donose odluke kad vrše pregled - uvidi na šta se domenski eksperti fokusiraju prilikom analize slike pomažu kreiranju modela kompjuterske vizije, kao i analizi grešaka modela.",
    "Zahtevi": "Potrebno je definisati/opisati zahteve koje bi rešenje trebalo da reši. Zahtevi su zapravo lista stavki koje predstavljaju problem.",
    "Opis drugačijih rešenja": "Razmatranje mogućih (alternativnih) rešenja. Koncizna sumarizacija, ali ne i detaljan pregled.",
    "Argumentacija odabranog rešenja": "Argumentacija zbog čega ste se opredelili za rešenje koje predstavljate u radu (samo teorijski). Ovo bi trebalo da se naslanja na prethodnu tezu.",
    "Opis koncepata rešenja": "Opis koncepata korišćenih u rešenju (tehnologije, modeli). Nakon čitanja opisa koncepata rešenja, čitalac bi trebalo da ima sve potrebno znanje za razumevanje dobijenog rezultata rešenja.",
    "Opis rešenja na opštijem nivou": "Pojednostavljeni slučajevi korišćenja, bez definisanja koraka procesa: npr. Koje potrebe tvoj softver ispunjava?; Kakav ulaz se očekuje, kakav izlaz se dobija (za svaku potrebu)?",
    "Inicijalno predstavljanje strukture sistema": "Pipeline u ML-u ili Moduli (feature u kontekstu package by feature pristupa paketiranja) u SW inženjerstvu (u zavisnosti koja se oblast obrađuje). Ovaj opis je jedno od sledeća dva: (1) kratak paragraf u slučaju jednostavne metodologije koja se ne sastoji od više koraka obrade ili (2) predstavljen grafički (npr. dijagram komponenti).",
    "Opis svake celine strukture rešenja": "Rad prelazi detalje svake celine sistema tek nakon opisa cilja i strukture sistema. Ovo može podrazumevati na koji način su sakupljani, obrađivani i analizirani podaci, na koji način je građen i analizirani sistem...",
    "Preciznost": "Dovoljno detalja - čitalac razume postupak i nema dodatnih pitanja.",
    "Visok nivo apstrakcije": "Rešenje treba da bude objašnjeno na visokom nivou apstrakcije (npr. ne treba opisivati isečke koda).",
    "Teorijske osnove": "Ne treba opisivati kako neka procedura, algoritam ili nešto treće funkcioniše, već kako je korišćeno.",
    "Problem": "Ne treba opisivati problem koji se rešava u radu. Opis problema, koji su nastali tokom izrade rešenja, je potrebno opisati (npr. zašto je bilo problematično prikupiti adekvatan skup podataka).",
    "Definisani koncepti": "Ni u jednom od ovih poglavlja ne postoje nedefinisani koncepti (čitalac može da razume problem i rešenje i nema dodatnih pitanja).",
    "Višak koncepata": "Poglavlje Teorijske osnove ne definiše koncepte koji nisu relevantni za razumevanje rada.",
    "Opis rešenja koncepata": "Iz poglavlja Rešenje je jasno kako je svaki od zahteva sistema realizovan. U slučaju da neki od zahteva nije realizovan, treba istaknuti da će se o tome pričati u narednom poglavlju Rezultati.",
    "Konciznost": "Jasno je izraženo šta je to što želimo da pokažemo evaluacijom (šta je poželjan/nepoželjan ishod evaluacije).",
    "Dovoljno detalja": "Moguće bi bilo reprodukovati eksperiment na osnovu njegovog opisa (dato je dovoljno detalja): (1) opisana je procedura, (2) opisane su metrike performanse, (3) definisan je kriterijum uspeha (npr. rešenje treba da pređe x% F-meru da bi bilo primenljivo u praksi ili smatra se da je zahtev ispunjen ako...)",
    "Vizuelni prikaz rezultata": "Rezultati su jasno predstavljeni (odgovarajuće tabele, grafikoni i slike). Tekst prisutan kod tabela, grafikona i slika treba da da informacije o istim i da se autor ne ponavlja. Treba ih koristiti kada postoji mnogo podataka, prikazuju se podaci kroz vreme, poredi se više izvora informacija, ukazuju se šabloni, trendovi, itd.)",
    "Vreme pisanja": "Potrebno je koristiti prošlo vreme.",
    "Struktura opisa rezultata": "Tekst poglavlja logično i jasno tumači predstavljene rezultate. Kombinovanje više rezultata radi diskusije o istim ili prezentovanje i objašnjavanje jednog rezultata i taj proces se iterativno ponavlja za svaki dobijeni rezultat. Sortirati po značaju ili hronološki.",
    "Diskusija o rezultatima": "Komentarisane su prednosti i ograničenja rešenja. Istaknuto je u kojim kontekstima je rešenje korisno i pouzdano, a u kojim nije. Komentarisano je šta nije pokriveno rešenjem (koji zahtevi nisu ispunjeni). Ako postoje, porediti sa ostalim radovima koji obrađuju sličnu tematiku.",
    "Finalni paragraf": "Sintezirati sve pronalaske (rezultate) u jednom paragrafu na kraju poglavlja.",
    "Gramatika i pravopis": "Izuzetak generalnom uputstvu. Proceniti koliko se često javljaju greške i odlučiti da li je osoba omašila gramatiku i/ili pravopis ili nije.",
    "Strane reči": "Paziti da strane reči treba da budu napisane kurzivom. Ako je neka reč prevedena, stavljamo strani naziv u zagradi (npr. Korišćenjem metode nasumične šume (eng. random forest)...).",
    "Skraćenice": "Prilikom uvođenja skraćenice, naveden je pun termin od koga je nastala. U daljem tekstu je korišćena skraćenica, a ne pun termin (izuzetak su naslovi poglavlja). Nisu definisane skraćenice koje kasnije nisu korišćene.",
    "Dužina rada": "Maksimalno tri stranice (sa literaturom) u zadatom formatu. Između 200 i 300 reči u poglavlju Problem. Između 250 i 500 reči u poglavlju Teorijske osnove. Između 400 i 800 reči u poglavlju Rešenje. Između 400 i 800 reči u poglavlju Rezultati.",
    "Razdvajanje teksta": "Koristiti spacing umesto praznih redova.",
    "Reference": "Click-able su reference ka izvorima i vode ka istim. Unutar rečenice, nikako izvan.",
    "Poglavlja i potpoglavlja": "Click-able su brojevi i/ili nazivi (pot)poglavlja i vode ka istim.",
    "Jednačina": "Deo su rečenice, koristiti equation alat za kreiranje istih.",
    "Slike i tabele": "Svaka mora biti pozvana iz teksta (ne sme da postoji tabela ili slika koje su u radu, a ne referenciraju se). Click-able su i vode ka istim. Moraju biti numerisane i imati naslov. Naslov slike je ispod slike, a tabele iznad tabele, na istoj stranici u oba slučaja. Pozivanje na iste se vrši pomoću enumeracije (nikako na slici ispod, već npr. na tabeli 1 se može videti...).",
    "Argumentacija": "Sve tvrdnje su podržane citatima ili argumentovane rezultatima rada. Literatura je citirana u okviru rečenice, najbliže tvrdnji koju podržava. Na primer, tvrdnja 1 [1] i tvrdnja 2 [2]. umesto tvrdnja 1 i tvrdnja 2 [1][2]. Važno je da su citati deo rečenice. Na primer, zabranjeno je Tvrdnja 1 i tvrdnja 2. [1][2].",
    "Konciznost rečenice": "1 rečenica = 1 poenta. Heuristika: rečenice sa više poenti tipično sadrže dosta zareza i veznika. Heuristika: rečenice sa više poenti su tipično dugačke. Heuristika: ako rečenica ima puno zareza jer je u pitanju nabrajanje, razmotrite upotrebu liste.",
    "Jasnoća rečenica": "Heuristika: Tekst ne sadrži preterano formalne i kompleksne reči koje otežavaju razumevanje. Heuristika: Rečenice su tako konstruisane da je subjekat (o kome/o čemu) pri početku, a glagol (šta subjekat radi) pri kraju rečenice. Heuristika: Glagol nije predaleko od subjekta. Heuristika: Korišćeni su jaki glagoli.",
    "Aktiv i pasiv": "Aktiv bi trebalo da je default opcija i da se koristi gde god nema očiglednog razloga da se koristi pasiv. Pasiv se koristi kada je izvršilac radnje očigledan ili nebitan, jer se stavlja fokus na rezultate ili proces, a ne na izvršioca. Takođe se koristi kada se navodi opšta činjenica. Npr. Eksperimenti su sprovedeni u kontrolisanim uslovima. - znamo da su autori izvršili eksperiment, ne treba ih navoditi. Nova metoda je primenjena na uzorku od 200 ispitanika. - bitno je da je metoda primenjena, a ne ko ju je primenio. Temperatura ključanja vode je određena pritiskom. - opšta činjenica.",
    "Početak rečenice": "Ne kretati rečenicu sa rečima `a`, `ili`, `i`, kao ni sa brojevima (npr. 2 eksperimenta su pokrenuta...).",
    "Sadržaj rečenice": "Rečenice ne treba da sadrže obraćanje čitaocu direktno. Ne treba koristiti žargone i slengove. Rečenice treba da budu formalnog tipa.",
    "Korišćenje vremena": "Prezent se koristi prilikom iskazivanja činjenica. Perfekt se koristi prilikom spominjanja sopstvenih rezultata.",
    "Zarezi": "Obavezni kod reči `a`, `ali`, zabranjeni kod reči `i`, `ili`. Koristiti ih kod nabrajanja. Ako postoje dva nezavisna iskaza u jednoj rečenici, razdvojiti ih zarezom (iako bi ovo trebalo da budu dve odvojene rečenice u većini slučajeva). Obavezni kod apozicije (primer: Jovan, sin Miloša, voli voće.).",
    "Interpunkcija": "Izbegavati uzvičnike. Dashes (duže crtice) - dodatni komentar u rečenici (npr. ... rezultati su ti i ti -- ovo ukazuje na to da...). Hyphens (kraće crtice) - spajanje reči/grupa reči (npr. crveno-beli, jug-jugoistok...). Tačka-zarez: trebalo bi da predstavlja dužu pauzu od zareza, ali kraću od tačke. Primeri korišćenja su: druga kauzula proširuje ili nastavlja prvu, objašnjenje sekvence akcija.",
    "Konciznost paragrafa": "1 paragraf = 1 tema. Jedna tema ne treba da bude razbijena na više paragrafa. 1) da li je tok misli jasan, 2) da li rečenice čine kohezivnu celinu",
    "Organizacija paragrafa": "1. Rečenica koja ističe glavnu ideju paragrafa 2. Rečenice koje razrađuju ideju paragrafa (objašnjenja/primeri/dokazi) - sve rečenice se odnose na glavnu ideju paragrafa 3. Zaključna rečenica (implikacije ideje; sumiranje/povezivanje sa 1. rečenicom; najava narednog paragrafa)",
    "Konzistentnost": "Za određeni koncept se konzistentno koristi isti termin/fraza.",
    "Repetitivnost": "Tekst nije repetitivan (primeri repetitivnosti: pojašnjavanje istog pojma/poente na dva različita mesta; tekst koji u potpunosti ponavlja ono što se nalazi na slici).",
    "Bespotrebni detalji": "Tekst ne zalazi u nepotrebne detalje (primeri nepotrebnih detalja: isečci koda koji su trivijalni, definisanje koncepata koji nisu neophodni za razumevanje teme).",
    "Odnos teksta i teme rada": "Sve što je izloženo je povezano sa temom rada - ne postoji tekst čija povezanost sa temom nije jasna.",
    "Nekonciznost": "Treba izbegavati korišćenje generičkih i bespotrebnih reči u tekstu. Primeri nekonciznih reči: 1. pridevi poput veoma/jako/donekle... 2. prazne fraze poput kao što je već rečeno,..., lako je zaključiti da..., opšte je poznato da... 3. redudantne fraze poput neočekivano iznenađenje, krajnji rezultat 4. primeri loših reči: oni, ljudi, drugim rečima, takođe poznat kao, veoma, neverovatno, samim, itd.",
    "Korišćenje ličnih zamenica": "Izbegavati korišćenje ličnih zamenica (ja, ti, on...), radi izbegavanja subjektivnosti rada. Izuzetak su rečenice gde je nužno iskoristiti lične zamenice (npr. Ja sam intervjuisao 20 studenata...)",
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
