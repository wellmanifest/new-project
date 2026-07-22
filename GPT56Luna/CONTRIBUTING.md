# Instrukcje pracy dla agentów AI

## 1. Zakres tego dokumentu

Ten plik opisuje rzeczywisty sposób pracy w tym repozytorium. Jest instrukcją operacyjną dla agenta AI, a nie ogólnym szablonem dla wszystkich projektów.

Jeżeli instrukcja tutaj różni się od ogólnego standardu w głównym `README.md`, pierwszeństwo ma:

1. polecenie użytkownika,
2. rzeczywisty stan repozytorium i kodu,
3. ten dokument,
4. ogólny standard w `README.md`,
5. `POLICY.md`.

Nie wolno zakładać istnienia narzędzia, agenta, testu ani pliku tylko dlatego, że jego nazwa występuje w dokumentacji.

## 2. Obowiązkowa analiza przed zmianą

Przed rozpoczęciem pracy agent MUSI:

1. przeczytać ten dokument,
2. przeczytać główny `README.md` i `POLICY.md`,
3. sprawdzić `git status` oraz ostatnie commity,
4. sprawdzić strukturę repozytorium,
5. przeczytać `project.sh`, jeżeli zadanie dotyczy automatyzacji lub narzędzi,
6. wyszukać istniejącą implementację, dokumentację i workflow,
7. utworzyć albo zaktualizować `TODO.md` dla większego zadania,
8. zapisać założenia, ryzyka i kryteria akceptacji,
9. dopiero potem rozpocząć edycję.

Jeżeli dokumentacja mówi o elemencie, którego nie ma w repozytorium, agent musi oznaczyć go jako niepotwierdzony, a nie traktować go jako dostępny.

## 3. Rzeczywisty przepływ `project.sh`

`project.sh` jest skryptem przygotowania środowiska i analizy projektu. Nie uruchamia aplikacji biznesowej ani testów aplikacji.

Aktywna logika skryptu:

1. zatrzymuje się przy błędzie dzięki `set -e`,
2. tworzy `venv`, jeżeli nie istnieje `venv/bin/pip`,
3. aktualizuje `pip`, ignorując błąd tej aktualizacji,
4. instaluje lub aktualizuje narzędzia analityczne,
5. uruchamia `code2llm`, `redup` i `prefact`,
6. uruchamia `doql`, `sumd` i `sumr`,
7. instaluje `goal` lokalnie z `../goal`, jeżeli lokalne repozytorium istnieje, albo z PyPI,
8. nie uruchamia `goal`, ponieważ jego polecenie jest zakomentowane,
9. wykonuje snapshot drzewa przez `tree.sh` albo systemowe `tree`, jeżeli jest dostępne.

Zakomentowane polecenia w `project.sh` nie są częścią aktualnego przepływu. Agent może je uruchomić tylko po osobnej decyzji i po opisaniu skutków.

## 4. Narzędzia potwierdzone przez skrypt

Poniższa lista wynika z aktywnych poleceń w `project.sh`. Dokładne opcje należy każdorazowo sprawdzić przez dokumentację narzędzia lub jego pomoc CLI.

| Narzędzie | Rzeczywiste użycie w skrypcie | Wynik lub efekt |
| --- | --- | --- |
| `regix` | instalacja/aktualizacja | Sam skrypt nie uruchamia polecenia `regix`; działanie nie jest potwierdzone |
| `prefact` | analiza projektu z wykluczeniem `examples/**` | wynik analizy narzędzia |
| `vallm` | instalacja/aktualizacja | Aktywne polecenia uruchamiające `vallm` są zakomentowane |
| `redup` | skan plików `.mjs`, `.js`, `.php`, `.sh` | raport w `./project` w formacie `toon` |
| `glon` | instalacja/aktualizacja | Sam skrypt nie uruchamia polecenia `glon`; działanie nie jest potwierdzone |
| `code2logic` | instalacja/aktualizacja | Sam skrypt nie uruchamia polecenia `code2logic`; działanie nie jest potwierdzone |
| `code2llm` | analiza projektu do `./project`, z wykluczeniem plików `.md` | wygenerowane reprezentacje projektu |
| `doql` | `adopt` do `app.doql.less` z `--force` | tworzy lub nadpisuje `app.doql.less` |
| `sumd` | sumaryzacja bieżącego projektu | wynik sumaryzacji dokumentacji |
| `sumr` | sumaryzacja raportów | wynik sumaryzacji dostępnych raportów |
| `goal` | instalacja/aktualizacja | komenda wykonawcza jest zakomentowana; nie należy zakładać automatycznego zarządzania zadaniami |

## 5. Zasady bezpieczeństwa i powtarzalności

Agent MUSI:

- nie commitować sekretów, danych dostępowych ani plików środowiskowych,
- sprawdzić, czy narzędzie nie nadpisze pliku przed użyciem `--force`,
- nie uruchamiać zakomentowanych komend bez uzasadnienia,
- nie instalować zależności globalnie bez wyraźnej zgody,
- sprawdzić diff po każdym logicznym etapie,
- opisać w raporcie komendy, które zostały uruchomione, oraz te, których nie uruchomiono,
- nie deklarować sukcesu narzędzia na podstawie samej instalacji pakietu,
- nie twierdzić, że repozytorium ma testy, CI, Docker lub aplikację, jeżeli nie zostały znalezione.

W skrypcie występują nieprzypięte wersje pakietów oraz wywołania `pip` bez ścieżki do `venv` w gałęzi dotyczącej lokalnego `goal`. Są to ryzyka powtarzalności i izolacji środowiska. Agent nie powinien ich poprawiać przy zadaniu czysto dokumentacyjnym, ale musi je zgłosić przy zadaniu dotyczącym skryptu.

## 6. Zasady pracy z dokumentacją

Po każdej zmianie agent sprawdza:

1. czy dokument opisuje aktualny przepływ, a nie planowaną funkcję,
2. czy polecenia są zgodne z `project.sh`,
3. czy oznaczono polecenia zakomentowane i funkcje niepotwierdzone,
4. czy ścieżki i nazwy plików istnieją,
5. czy dokumentacja nie obiecuje testów, CI ani Dockera, których repozytorium nie zawiera,
6. czy opis jest zrozumiały bez kontekstu poprzedniej rozmowy.

Główne źródła prawdy:

- `GPT56Luna/CONTRIBUTING.md` — instrukcja operacyjna dla agenta,
- `GPT56Luna/ANALIZA-DOKUMENTACJI.md` — ustalenia, luki i decyzje,
- `README.md` — ogólny standard pracy,
- `POLICY.md` — polityki projektu,
- `project.sh` — rzeczywista automatyzacja,
- `docs/README.md` — indeks dokumentacji.

## 7. Git i analiza historii

Przed większą zmianą agent analizuje historię Git, aby odróżnić intencję od aktualnego stanu. W szczególności należy sprawdzić:

- kiedy dodano pierwotny standard `CONTRIBUTING.md`,
- czy dokument został przeniesiony lub skrócony,
- które pliki zostały usunięte albo przemianowane,
- czy aktualny skrypt odpowiada dokumentacji.

Commit nie jest sam w sobie dowodem, że funkcja nadal istnieje. Dowodem jest aktualny plik, działająca komenda albo potwierdzona dokumentacja narzędzia.

## 8. Kolejność realizacji zadania

1. Analiza wymagania i istniejącej dokumentacji.
2. Weryfikacja plików, narzędzi i historii Git.
3. Plan oraz kryteria akceptacji w `TODO.md`.
4. Minimalna zmiana w odpowiednim miejscu.
5. Sprawdzenie formatowania i spójności odwołań.
6. Uruchomienie tylko adekwatnych, bezpiecznych kontroli.
7. Przegląd diffu i kontrola sekretów.
8. Aktualizacja raportu decyzji i ograniczeń.
9. Logiczny commit, jeżeli użytkownik zleci wykonanie commita.

## 9. Definition of Done dla zmian dokumentacyjnych

Zmiana dokumentacyjna jest zakończona, gdy:

- [ ] opis wskazuje źródła prawdy,
- [ ] opisany przepływ odpowiada aktualnym plikom,
- [ ] funkcje niepotwierdzone są wyraźnie oznaczone,
- [ ] komendy aktywne i zakomentowane nie są pomieszane,
- [ ] znane luki i ryzyka są zapisane,
- [ ] odwołania do plików są poprawne,
- [ ] diff nie zawiera przypadkowych zmian,
- [ ] raport zawiera zakres wykonanej weryfikacji.
