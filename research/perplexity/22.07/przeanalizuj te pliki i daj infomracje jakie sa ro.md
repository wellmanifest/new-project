<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# przeanalizuj te pliki i daj infomracje jakie sa roznice i co dalej z tym zrobic

Przejrzałem te trzy pliki i różnice są dość wyraźne: **CONTRIBUTING.md** jest najbardziej „techniczny” i formalny, **CONTRIBUTING-2.md** wygląda jak wersja uproszczona/regułowa z naciskiem na polityki i narzędzia, a **CONTRIBUTING-3.md** jest najbardziej kompletny i operacyjny, bo opisuje pełny cykl pracy agenta krok po kroku.[^1][^2][^3]

## Najważniejsze różnice

- **CONTRIBUTING.md** to głównie formalna specyfikacja DSL z modułami, stanami, regułami i warunkami zakończenia. Widać tam silny nacisk na scope, źródła prawdy, dowody i kontrolę błędów.[^1]
- **CONTRIBUTING-2.md** jest bardziej „zasadniczy”: definiuje fazy pracy, priorytety P0/P1/P2, reguły uruchamiania narzędzi, delegacji i publikacji. Ma też bardziej praktyczne wskazówki, np. kiedy nie uruchamiać commented tools i kiedy wymagać diff review.[^2]
- **CONTRIBUTING-3.md** wygląda jak najbardziej rozbudowana wersja instrukcji dla agenta: ma słownik pojęć, procedury START/ANALYZE/DELEGATE/TEST/VALIDATE/REPAIR/DOCUMENT/COMMIT/FINISH/SELFIMPROVE oraz reguły typu Definition of Done.[^3]


## Co się pokrywa

- Wszystkie trzy pliki traktują CONTRIBUTING jako **proceduralny dokument sterujący pracą agenta**, a nie zwykły opis dla człowieka.[^2][^3][^1]
- Wszystkie podkreślają, że trzeba bazować na istniejących plikach repozytorium, sprawdzać stan repo i unikać zgadywania.[^3][^1][^2]
- Wszystkie mają też wspólny motyw: **najpierw analiza, potem plan, potem zmiany, testy/walidacja i dopiero na końcu publikacja**.[^1][^2][^3]


## Najważniejsze różnice praktyczne

- **CONTRIBUTING.md** bardziej przypomina maszynowo sformatowaną specyfikację reguł i stanów. Nadaje się jako „kanoniczny” opis działania systemu, ale jest mniej przyjazny operacyjnie.[^1]
- **CONTRIBUTING-2.md** zawiera bardzo konkretne reguły dotyczące narzędzi, np. które są aktywne, które tylko zainstalowane, a które zakomentowane. To wygląda jak dokument do ścisłej egzekucji przez agenta.[^2]
- **CONTRIBUTING-3.md** najlepiej opisuje rzeczywisty workflow: co czytać na starcie, jak analizować wymagania, jak tworzyć TODO, jak delegować, jak testować, jak dokumentować i jak kończyć zadanie.[^3]


## Co dalej z tym zrobić

1. **Wybrać jeden plik jako źródło prawdy.** Najpewniej **CONTRIBUTING-3.md** jako najbardziej kompletny workflow, a **CONTRIBUTING.md** i **CONTRIBUTING-2.md** potraktować jako materiał do konsolidacji.[^2][^3][^1]
2. **Usunąć rozjazdy między wersjami.** Trzeba sprawdzić, czy te pliki nie powielają się z różnymi regułami, bo agent może dostać sprzeczne instrukcje.[^3][^1][^2]
3. **Zrobić jedną finalną wersję CONTRIBUTING.md.** Powinna mieć:
    - krótki cel,
    - sekcję workflow,
    - reguły dla narzędzi,
    - zasady testów i walidacji,
    - zasady commit/push,
    - Definition of Done.[^2][^3]
4. **Dodać mapowanie „co z czym się zgadza”.** Jeśli któryś plik ma unikalne reguły, warto je przepisać do finalnej wersji i oznaczyć jako nadrzędne.[^1][^3][^2]
5. **Przetestować dokument na jednym zadaniu.** Najlepiej wykonać symulację: start → analiza → plan → modyfikacja → test → dokumentacja → finish, i sprawdzić, czy reguły nie blokują się nawzajem.[^3]

## Moja rekomendacja

Jeśli celem jest utrzymanie repo, to najlepszy ruch to **scalenie** tych trzech plików w jeden spójny standard, zamiast trzymania trzech konkurencyjnych wersji. Najbardziej wartościowe elementy do zachowania to: z **CONTRIBUTING.md** — formalna struktura stanów i dowodów, z **CONTRIBUTING-2.md** — polityka narzędzi i priorytety, z **CONTRIBUTING-3.md** — pełna procedura wykonawcza.[^1][^2][^3]

Mogę teraz przygotować Ci **konkretną tabelę różnic sekcja po sekcji** albo od razu **propozycję jednej scalonej wersji CONTRIBUTING.md**.

<div align="center">⁂</div>

[^1]: CONTRIBUTING.md

[^2]: CONTRIBUTING-2.md

[^3]: CONTRIBUTING-3.md

