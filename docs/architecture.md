# Architektura MVP

## Cel projektu

Projekt buduje pierwsza, kompletnie testowalna wersje systemu, ktory formalizuje ludzkie intencje, ustalenia i polecenia w jawny DSL. DSL ma byc czytelny dla czlowieka, jednoznaczny dla agentow AI i wykonalny przez runtime bez ukrytych zalozen.

MVP dziala offline, na mockach i danych przykladowych. Nie wymaga internetu, klucza OpenRouter ani prawdziwych integracji z poczta, plikami, bazami danych czy zewnetrznymi API.

## Glowny przeplyw

Kanoniczny przeplyw pracy jest nastepujacy:

```text
NL / rozmowa / wytyczne tekstowe
-> LLM
-> formalny DSL
-> diagnoza brakow, sprzecznosci, niejednoznacznosci i zalozen
-> walidacja Python verifierem
-> akceptacja jednej strony albo obu stron
-> TypeScript runtime
-> dokument, kontrakt, opis zadania albo wynik operacji
-> audyt
```

Wejscie moze byc pojedyncza wypowiedzia, historia rozmowy dwoch stron albo plik z wytycznymi. LLM zamienia tekst na DSL, ale nie ma prawa dopisywac ustalen, ktorych nie ma w zrodle. Kazde istotne pole DSL powinno byc powiazane ze zrodlem: wypowiedzia, fragmentem rozmowy, plikiem lub przykladem.

Po wygenerowaniu DSL system diagnozuje jego stan. Jezeli brakuje danych, wartosci sa niejednoznaczne, wypowiedzi stron sa sprzeczne albo LLM dodal zalozenie, runtime nie powinien renderowac finalnego dokumentu jako gotowego. Zamiast tego powinien pokazac pytania, blokady albo wymagane potwierdzenia.

## Przeplyw DSL do NL

Drugi kierunek jest rownie wazny: DSL musi byc mozliwy do wyrenderowania z powrotem do czytelnego opisu w jezyku naturalnym albo dokumentu koncowego. Ten rendering nie moze zmieniac znaczenia zaakceptowanego DSL.

Minimalny przeplyw DSL -> NL:

```text
formalny DSL
-> walidacja strukturalna
-> walidacja znaczeniowa
-> sprawdzenie statusow informacji i akceptacji
-> render human-readable DSL albo dokumentu
-> audyt renderowania
```

Jezeli DSL zawiera pola `MISSING`, `AMBIGUOUS`, `CONFLICTING`, `ASSUMED` albo `REQUIRES_CONFIRMATION`, wynik powinien byc raportem roboczym, a nie finalnym kontraktem lub zadaniem gotowym do wykonania.

## Role ludzi

Human1 to autor intencji, zleceniodawca albo pierwsza strona umowy. Human1 dostarcza polecenie, rozmowe lub wytyczne, odpowiada na pytania doprecyzowujace i moze zaakceptowac DSL jako zgodny ze swoja intencja.

Human2 to odbiorca, wykonawca albo druga strona umowy. Human2 ocenia, czy DSL zawiera wystarczajace dane do wykonania zadania lub zawarcia kontraktu. W scenariuszach dwustronnych Human2 musi zaakceptowac ten sam stan DSL co Human1.

Akceptacja czlowieka dotyczy konkretnej wersji DSL, najlepiej identyfikowanej hashem. Zmiana DSL po akceptacji uniewaznia wczesniejsze akceptacje, poniewaz strony nie potwierdzily juz tej samej tresci.

## Rola LLM

LLM pelni role formalizatora i interpretatora. W MVP moze dzialac jako mock planner, a tryb z OpenRouter pozostaje opcjonalny i nie jest wymagany do poprawnego dzialania projektu.

LLM powinien:

- zamieniac tekst naturalny na DSL,
- wykrywac kandydatow na strony, role, obowiazki, terminy, rezultaty i kryteria odbioru,
- oznaczac braki i niepewnosci zamiast zgadywac,
- wskazywac zrodla ustalen,
- generowac pytania doprecyzowujace,
- renderowac DSL do czytelnego opisu, kiedy runtime uzna to za dozwolone.

LLM nie powinien wykonywac akcji, zmieniac danych, wysylac wiadomosci ani uznawac dokumentu za zaakceptowany. Te decyzje naleza do verifiera, runtime'u i ludzi.

## Rola Python verifiera

Python verifier odpowiada za walidacje znaczeniowa. Sprawdza, czy DSL pokrywa intencje z wejscia i czy nie zawiera dzialan albo warunkow dodanych bez podstawy w zrodle.

Verifier powinien raportowac:

- braki wzgledem intencji,
- sprzecznosci miedzy ustaleniami,
- elementy dodane przez LLM,
- wymagane potwierdzenia,
- naruszenia polityk,
- rekomendacje: zaakceptowac, odrzucic, poprawic albo zadac pytania.

Raport verifiera ma byc maszynowo przetwarzalny przez runtime i czytelny w audycie.

## Rola TypeScript runtime

TypeScript runtime odpowiada za techniczna walidacje, orkiestracje procesu, stan zadania, decyzje polityk, wykonanie akcji mockowych, rendering i audyt.

Runtime powinien:

- walidowac strukture DSL,
- prowadzic state machine zadania,
- blokowac wykonanie przy brakach, sprzecznosciach i odmowie polityki,
- obslugiwac pytania i odpowiedzi,
- obslugiwac akceptacje jednej albo dwoch stron,
- uniewazniac akceptacje po zmianie DSL,
- wykonywac akcje w trybie dry-run lub mock,
- zapisywac audyt decyzji, wejsc, DSL, verifiera, planu i wynikow.

Runtime jest miejscem, w ktorym konczy sie interpretacja, a zaczyna kontrolowane wykonanie.

## Diagnozowanie problemow

System rozroznia kilka klas problemow:

- Brak danych: wymagane pole nie ma wartosci.
- Niejednoznacznosc: wartosc moze znaczyc wiecej niz jedna rzecz.
- Sprzecznosc: dwa zrodla lub dwie strony podaja niezgodne ustalenia.
- Zalozenie: LLM dopelnil tresc bez jawnego potwierdzenia.
- Brak akceptacji: DSL jest poprawny technicznie, ale nie zostal zatwierdzony przez wymagana strone.

Te problemy nie sa bledami wykonania. Sa normalnym stanem procesu formalizacji i powinny prowadzic do pytan, odmowy finalizacji albo edycji DSL.

## Pytania doprecyzowujace

Pytania doprecyzowujace powstaja wtedy, gdy runtime lub verifier nie maja wystarczajacych danych do bezpiecznego dalszego kroku. Pytanie powinno byc konkretne, powiazane z polem DSL i zapisane w audycie.

Po odpowiedzi czlowieka system aktualizuje DSL albo kontekst procesu, ponownie wykonuje walidacje i dopiero wtedy przechodzi dalej. Odpowiedz nie powinna automatycznie oznaczac calego DSL jako zaakceptowanego.

## Akceptacje

W prostym przeplywie wystarczy akceptacja Human1. Dotyczy to polecenia jednostronnego, raportu, zadania roboczego albo dokumentu, ktory nie tworzy zobowiazan drugiej strony.

W przeplywie dwustronnym wymagane sa akceptacje Human1 i Human2 dla tego samego hasha DSL. Jezeli DSL zmieni sie po akceptacji jednej strony, poprzedni hash przestaje byc aktualny i obie strony musza ponownie ocenic tresc.

Runtime nie powinien renderowac finalnej umowy ani oznaczac zadania jako gotowego, jezeli wymagana akceptacja jest nieobecna, odrzucona albo dotyczy starszej wersji DSL.

## Rola examples

Folder `examples/` jest zestawem scenariuszy regresyjnych MVP. Kazdy przyklad powinien zawierac wejscie, oczekiwany DSL, oczekiwany plan, oczekiwana weryfikacje i oczekiwany wynik lub raport.

Przyklady pelnia trzy role:

- dokumentuja zachowanie systemu,
- sluza jako testy regresyjne,
- chronia przed dodawaniem przez LLM dzialan, warunkow lub danych bez zrodla.

MVP powinno byc oceniane przez mozliwosc ponownego uruchomienia przykladow offline.

## Decyzja dotyczaca project.sh

`project.sh` jest aktywnym, bezpiecznym wrapperem komend projektu. Obsluguje instalacje workspace, typecheck, lint, format, testy, przyklady, verify i system-check. Na Windows ten sam zakres udostepnia `project.bat`.

Historyczny, sieciowy workflow analityczny zostal odseparowany pod jawna komenda `legacy-analyze`, wiec rutynowa walidacja powinna uzywac `project.sh verify` albo `project.sh system-check`.

## Granice MVP

MVP obejmuje:

- mockowe planowanie NL -> DSL,
- walidacje DSL,
- Python verifier,
- TypeScript runtime,
- pytania doprecyzowujace,
- akceptacje i hashowanie planu,
- mockowe wykonanie bez efektow zewnetrznych,
- rendering roboczy DSL do opisu,
- audyt,
- przyklady regresyjne.

MVP nie obejmuje:

- prawdziwego wysylania e-maili,
- prawdziwych integracji z zewnetrznymi systemami,
- wymaganego OpenRouter,
- instalacji zaleznosci z sieci w czasie testow,
- wykonywania niekontrolowanych komend shell,
- finalnej automatyzacji prawnie wiazacych umow bez ludzkiej akceptacji.
