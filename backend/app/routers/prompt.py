import requests
from fastapi import (
    APIRouter,
    Depends,
    Body,
)
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from typing import Annotated


from ..schemas.response import GenericResponse
from ..settings import settings

router = APIRouter(
    prefix="/prompts",
    tags=["prompts"],
    responses={404: {"description": "Not found"}},
)


@router.get("/generate-text")
def generate_text():
    API_KEY = settings.groq_cloud_api_key
    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": """
                    Ti si recenzent koji treba da revidira naučne radove.
                    Potrebno je da odgovori budu formalni i da na osnovu pravila, koja ću ti priložiti, revidiraš uneseni tekst. 
                    U svojim odgovorima koristi ekavicu ili ijekavicu, u zavisnosti od toga koji dijalekt uočiš u tekstu.
                    """,
            },
            {
                "role": "user",
                "content": """
                Prvo ću ti priložiti sva pravila koja treba da budu ispoštovana, a zatim i tekst koji treba da ispraviš. 
                Tvoj odgovor treba da prikaže predloge ispravke i razloge predloga ispravki teksta za svako pravilo.
                Ukoliko smatraš da je pravilo ispoštovano 90%, navedi da je ono ispoštovano umesto ispravke.
                Za svako pravilo koje se nalazi ispod "Pravila", tvoj odgovor treba da ima sledeći šablon i ništa van njega ne treba da postoji. Takođe, bolduj sve stavke u šablonu.

                    (Ako si siguran da je ispravno manje od 90%)
                    Naziv pravila koje se ispravlja (Izvuci ove nazive iz "Pravila"):
                        Ispravka:
                        Obrazloženje ispravke:

                    (Ako si siguran da je ispravno više od ili jednako 90%)
                    Naziv pravila koje se ispravlja (Izvuci ove nazive iz "Pravila"):
                        Obrazloženje validnosti: 

                Pravila: 
                - Širi problem:
                    Jasno je istaknut širi problem koji se obrađuje u radu.
                    Čitalac nema potrebe da dodatno istražuje o problemu da bi video značaj rada.

                - Osnovni koncepti:
                    Definisani su osnovni koncepti za razumevanja problema. 
                    Definisani koncepti - nije potrebno dodatno istraživanje da bi se tekst razumeo.
                    Definisani koncepti - nijedan definisani koncept nije suvišan.

                - Značaj rešenja:
                    Istaknuto je zašto je priloženo rešenje značajno za društvo; 
                    Objašnjava se koja je motivacija iza rešenja i problema koji se rešava

                - Pozicioniranje užeg problema u širem kontekstu:
                    Primer za softversko inženjerstvo:
                    - Širi kontekst: U poslednje dve decenije, agilne metodologije poput Scrum-a i Kanban-a 
                    postale su standard u razvoju softvera...
                    - Uži kontekst: U ovom radu fokusiramo se na optimizaciju komunikacije i saradnje u 
                    distribuiranim agilnim timovima, ...

                    Primer za AI:
                    - Širi kontekst: Veštačka inteligencija značajno je unapredila različite domene, 
                    poput obrade prirodnog jezika, prepoznavanja slika i optimizacije složenih sistema....
                    - Uži kontekst: Ovaj rad istražuje kako se algoritmi zasnovani na dubokom učenju mogu prilagoditi 
                    da pruže interpretabilne rezultate u medicinskoj dijagnostici...  

                - Opis fokusa rada:
                    Jasno je očekivano ponašanje rešenja i kada/kako se koristi.

                - Opis koristi rešenja:
                    Istaknute su konkretne interesne grupe koje bi rešenje koristile i na koji način.

                Tekst:
                    Dijabetička retinopatija je jedan od glavnih uzroka slepila
                    među odraslima [1]. Dijagnoza ove bolesti predstavlja složen
                    proces koji zahteva stručnu procenu oftalmologa. Međutim,
                    nedostatak stručnjaka u pojedinim područjima, posebno rural-
                    nim, rezultuje nedostupnošću adekvatne dijagnostike i nepra-
                    vovremenom lečenju pacijenata [2].

                    Primena mašinskog učenja (ML, Machine Learning) može
                    pomoći u dijagnozi rane dijabetičke retinopatije [3]. Blagovre-
                    mena dijagnoza može značajno smanjiti rizik od težih kom-
                    plikacija i slepila [4]. Algoritam se obučava na osnovu slika
                    mrežnjače oka prethodno ocenjenih od strane oftalmologa.
                    Bolest se klasifikuje stepenima 0, 1, 2, 3, 4 pri čemu stepen
                    0 predstavlja zdravo oko. Najteži stepeni, 3 i 4, su retki, ali i
                    ključni za uspostavljanje precizne dijagnoze [5]. Implementa-
                    cijom različitih tehnika namenjenih za rad sa nebalansiranim
                    podacima, može se značajno poboljšati preciznost pri dijagnozi
                    modela ML.

                    Ovaj rad istražuje primenu ML za dijagnozu dijabetičke re-
                    tinopatije. Razvijeni algoritam zahteva samo slike mrežnjače,
                    koje se mogu dobiti pomoću uobičajene opreme za snimanje
                    oka. Rešenje je od koristi zdrastvenim radnicima za povećanje
                    efikasnosti i brzine uspostavljanja dijagnoze. Takođe, pacijen-
                    tima se omogućava pristup pouzdanoj dijagnostici, nezavisno
                    od lokalne dostupnosti oftalmoloških stručnjaka. Ovim se
                    prevazilaze ograničenja tradicionalne dijagnostike i širi se
                    dostupnost kvalitetne zdrastvene zaštite.
                """,
            },
        ],
        # "max_completion_tokens": 1000,
    }

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    response = requests.post(API_URL, json=data, headers=headers)

    if response.status_code == 200:
        generated_text = response.json()["choices"][0]["message"]["content"]
        print(generated_text)
    else:
        generated_text = response.text
        print("Error:", generated_text)

    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Succesfully generated text", data=generated_text
        ).model_dump(),
    )
