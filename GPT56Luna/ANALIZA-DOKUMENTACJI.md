# Analiza dokumentacji dla agentów AI

## Wniosek

Przed wdrożeniem DSL `CONTRIBUTING.md` nie był wystarczająco zrozumiały jako samodzielna instrukcja dla agenta AI. Zawierał podstawowe zasady, ale nie wskazywał jednoznacznie źródła prawdy, nie rozróżniał funkcji potwierdzonych od deklarowanych i nie opisywał dokładnie aktualnego przepływu `project.sh`.

Najważniejsza poprawa polega na rozdzieleniu:

- ogólnego standardu pracy w głównym `README.md`,
- polityk repozytorium w `POLICY.md`,
- proceduralnej polityki lokalnej w `GPT56Luna/POLICY.md`,
- proceduralnej instrukcji operacyjnej w `GPT56Luna/CONTRIBUTING.md`,
- ustaleń z analizy w tym pliku,
- indeksu dokumentacji w `docs/README.md`.

## Wdrożenie proceduralne

- `GPT56Luna/CONTRIBUTING.md` używa stanów, przejść, reguł `WHEN/DO/ASSERT/NEXT` i jawnych wyników.
- `GPT56Luna/POLICY.md` wymusza dowody dla deklaracji, rozdziela instalację od wykonania i blokuje operacje bez decyzji lub kontroli.
- Reguła bez warunku, działania, asercji albo przejścia jest odrzucana.
- Reguła naturalnojęzyczna musi zostać przekształcona do postaci proceduralnej.

## Stan repozytorium

Na moment analizy repozytorium zawiera:

- `CONTRIBUTING.md`,
- `README.md`, który zawiera rozbudowany ogólny standard pracy; przed tą analizą miał mylący nagłówek `CONTRIBUTING.md`,
- `POLICY.md`,
- `GPT56Luna/POLICY.md` — proceduralny DSL polityk lokalnych,
- `project.sh`,
- workflow `.devin/workflows/analyze-documentation.md`,
- `docs/README.md` — indeks dokumentacji.

Nie znaleziono:

- aplikacji lub katalogu `src/`,
- katalogu `tests/`,
- `TODO.md`,
- `CHANGELOG.md`,
- plików Docker,
- konfiguracji CI,
- folderu `GPT56Luna` przed rozpoczęciem tej pracy.

Brak tych elementów oznacza, że dokumentacja nie może przedstawiać tego repozytorium jako gotowej aplikacji. Jest to obecnie zestaw standardów, skryptów i workflow do analizy projektu.

## Porównanie dokumentacji z `project.sh`

### Elementy zgodne

- Dokumentacja wskazuje `code2llm`, `redup`, `prefact`, `vallm`, `doql`, `sumd`, `sumr` i `goal`.
- Dokumentacja opisuje generowanie wyników analizy w `./project`.
- Dokumentacja promuje planowanie, kontrolę Git, testowanie, walidację i dokumentowanie decyzji.

### Braki i rozbieżności

1. Przed zmianą `docs/` był pusty, mimo że starsza wersja dokumentacji i workflow wskazywały `docs/README.md` jako główne miejsce dokumentacji; obecnie `docs/README.md` jest indeksem.
2. Przed tą zmianą `CONTRIBUTING.md` był po angielsku i miał formę listy ogólnych reguł, bez instrukcji wykonania zadania krok po kroku.
3. `project.sh` instaluje `regix`, `glon` i `code2logic`, ale dokumentacja nie opisuje ich nawet jako elementów przepływu.
4. `project.sh` nie uruchamia `regix`, `glon`, `code2logic`, a polecenia `vallm` i `goal` są zakomentowane. Sama obecność instalacji nie potwierdza funkcjonalności.
5. Dokumentacja opisuje test-agent, repair-agent, validator-agent, todo-agent i doctor-agent, ale w repozytorium nie ma ich kodu ani konfiguracji. Ich dostępność wymaga potwierdzenia poza repozytorium.
6. Dokumentacja zakłada `TODO.md`, testy, Docker, CI, changelog i wersjonowanie, których aktualnie nie ma.
7. Skrypt używa nieprzypiętych wersji pakietów, co jest sprzeczne z zasadą powtarzalności w `POLICY.md`.
8. W gałęzi lokalnego `goal` skrypt używa `pip` bez ścieżki `venv`, co może zmienić środowisko poza wirtualnym środowiskiem.
9. Skrypt używa ścieżki `venv/bin`, więc na Windows wymaga środowiska z POSIX-owym układem ścieżek, np. WSL; natywne uruchomienie nie zostało potwierdzone.
10. `doql ... --force` może nadpisać `app.doql.less`, ale dotychczasowa dokumentacja nie eksponuje tego ryzyka wystarczająco jasno.

## Co agent powinien rozumieć jako aktualną logikę

Aktualny przepływ nie jest pipeline'em implementacji aplikacji. Jest sekwencją przygotowania środowiska i narzędzi analitycznych:

`venv` → instalacja narzędzi → analiza kodu → analiza duplikatów → pre-faktoryzacja → konwersja do `doql` → sumaryzacja → snapshot drzewa.

Nie należy dopowiadać etapów testowania, naprawy, wdrażania ani publikacji, ponieważ nie ma ich w aktywnych poleceniach `project.sh`.

## Analiza historii Git

Historia pokazuje, że:

1. początkowo dodano długi `CONTRIBUTING.md`,
2. następnie przeniesiono go do `docs/README.md` i dodano `project.sh`,
3. później `docs/README.md` został przeniesiony do głównego `README.md`,
4. wprowadzono `POLICY.md` i workflow analizy dokumentacji,
5. W momencie analizowanego commita katalog `docs/` pozostał pusty, choć workflow zakładał istnienie `docs/README.md`; obecny workflow i indeks zostały uzupełnione.

Wniosek z historii: obecny układ jest wynikiem przeniesienia dokumentacji, ale nie został domknięty aktualizacją odwołań. Agent powinien używać historii do zrozumienia intencji, lecz aktualny stan plików ma pierwszeństwo przed dawną wersją.

## Zalecenia dla kolejnych prac

- Utrzymywać jedną instrukcję operacyjną dla agenta i wyraźnie wskazywać ją jako źródło prawdy.
- Po zmianie `project.sh` aktualizować tabelę narzędzi oraz sekcję ryzyk.
- Nie wpisywać do dokumentacji niepotwierdzonych możliwości agentów zewnętrznych.
- Dodać `TODO.md`, testy, CI, Docker i `CHANGELOG.md` dopiero wtedy, gdy repozytorium zacznie zawierać aplikację lub wymagany proces publikacji.
- Rozważyć osobne zadanie naprawy `project.sh`: przypięcie wersji, używanie wyłącznie `venv/bin/pip` i rozdzielenie instalacji od uruchamiania analiz.
- Przy każdym większym zadaniu zapisać decyzje, blokady i wynik kontroli w raporcie lub `TODO.md`.

## Zakres wykonanej pracy

W ramach tej analizy:

- porównano `CONTRIBUTING.md`, `README.md`, `POLICY.md`, workflow i `project.sh`,
- przeanalizowano historię commitów i przenoszenie dokumentacji,
- potwierdzono pusty stan `docs/`,
- przygotowano proceduralną instrukcję operacyjną w `GPT56Luna/CONTRIBUTING.md`,
- przygotowano proceduralną politykę w `GPT56Luna/POLICY.md`,
- zaktualizowano indeks dokumentacji w `docs/README.md` i workflow analizy.
