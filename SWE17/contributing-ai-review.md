# Analiza CONTRIBUTING.md pod kątem zrozumiałości dla AI agentów

## Stan faktyczny repozytorium

W repozytorium `new-project` znajdują się dwa pliki opisujące zasady pracy:

- `CONTRIBUTING.md` (root, 129 linii, angielski, skrócona wersja)
- `README.md` (root, 927 linii, polski, pełna wersja CONTRIBUTING.md)

Katalog `docs/` jest pusty. Workflow `.devin/workflows/analyze-documentation.md` wskazuje, że pełna dokumentacja powinna być w `docs/README.md`, a root `CONTRIBUTING.md` powinien odsyłać do niej.

Historia git (`git log --oneline -20`):

```text
f55fc06 (HEAD) update
7a37b2e Update
0ae1938 adds CONTRIBUTING
b302616 Initial commit
```

- `0ae1938` — dodano pełny `CONTRIBUTING.md` (561 linia).
- `7a37b2e` — przeniesiono pełną treść do `docs/README.md` (561 linia), skrócono `CONTRIBUTING.md` (593 linie usunięto), dodano `project.sh`.
- `f55fc06` — przeniesiono `docs/README.md` do root `README.md` (365 linii), dodano `POLICY.md`, dalej skracano `CONTRIBUTING.md`.

Obecnie `README.md` zaczyna się od nagłówka `# CONTRIBUTING.md` i zawiera pełne wytyczne po polsku, natomiast `CONTRIBUTING.md` zawiera skróconą wersję po angielsku.

## Czy CONTRIBUTING.md jest zrozumiały dla AI agentów?

### Krótka odpowiedź

Tak, ale **niejednoznacznie** — istnieją dwa pliki o zbliżonej treści, w dwóch językach, z różnym poziomem szczegółowości. AI agent nie wie, który plik jest źródłem prawdy.

### Mocne strony

- `CONTRIBUTING.md` (angielski) ma klarowną strukturę: Core Principles, Workflow Rules, Tool Usage, Agent Coordination, Policy Compliance, Quality Standards.
- Język jest imperatywny: "Check", "Delegate", "Follow", "Use" — łatwy do zaimplementowania przez agenta.
- Wyraźnie wymienione są narzędzia i agenci do wykorzystania.
- Zasady są konkretne (np. "Do NOT duplicate existing functionality").

### Słabe strony / problemy

1. **Dwa źródła prawdy**
   - `CONTRIBUTING.md` (angielski, 129 linii)
   - `README.md` (polski, 927 linii, tytuł `# CONTRIBUTING.md`)
   - Agent nie wie, który dokument obowiązuje.

2. **Niespójność językowa**
   - Główny plik CONTRIBUTING po angielsku.
   - Pełna wersja po polsku w README.
   - Wymagane jest jednoznaczne rozstrzygnięcie językowe.

3. **Nieaktualne odniesienia w CONTRIBUTING.md**
   - W sekcji "Follow documentation" wymienia `TODO.md`, którego w repozytorium nie ma.
   - Workflow wymaga `docs/README.md`, ale katalog `docs/` jest pusty.

4. **Brak kontekstu dla IDE/agentów bez specjalistycznych narzędzi**
   - Dokument zakłada dostępność narzędzi: `code2llm`, `redup`, `prefact`, `vallm`, `doql`, `sumd`, `sumr`, `goal`.
   - Zakłada dostępność agentów: `test-agent`, `repair-agent`, `validator-agent`, `todo-agent`, `doctor-agent`.
   - W środowisku takim jak Cascade / Cursor / Devin te agenci/narzędzia nie są domyślnie dostępne. Brakuje instrukcji awaryjnych (fallback) lub sposobu ich wywołania.

5. **README.md jako CONTRIBUTING.md**
   - Plik `README.md` powinien opisywać projekt, a nie zawierać pełen regulamin CONTRIBUTING.
   - Tytuł `# CONTRIBUTING.md` w `README.md` jest mylący.

## Czy dokument oddaje logikę działania?

### Co jest dobrze opisane

Główna pętla pracy jest wyraźna:

```text
sprawdź istniejące rozwiązania → zaplanuj w TODO.md → deleguj → testuj → waliduj → napraw → dokumentuj → commituj → push
```

Logika jest poprawna i spójna z `POLICY.md` oraz `project.sh`.

### Co brakuje lub jest niejasne

1. **Jedno źródło prawdy**
   - Należy zdecydować, gdzie mieszka pełna wersja CONTRIBUTING: w `CONTRIBUTING.md` czy w `docs/README.md`.
   - Aktualnie znajduje się w `README.md`, co jest sprzeczne z zasadą "single source of truth" z workflow.

2. **TODO.md**
   - CONTRIBUTING wymaga tworzenia i aktualizowania `TODO.md`.
   - Plik nie istnieje w repozytorium.
   - Agent nie ma wzoru do naśladowania.

3. **CHANGELOG.md**
   - Wymagany w sekcji 7 (standard nowego projektu) i sekcji 14.
   - Brak pliku w repozytorium.

4. **Testy i CI**
   - Wymagane testy, automatyczne uruchamianie testów, konfiguracja CI.
   - W repozytorium brak `tests/`, plików CI (np. `.github/workflows/`), `pyproject.toml`, `package.json` itp.

5. **Dokumentacja narzędzi**
   - `project.sh` używa narzędzi: `code2llm`, `redup`, `prefact`, `doql`, `sumd`, `sumr`, `goal`.
   - W README.md ( Contributing) narzędzia te są opisane, ale:
     - Brakuje `code2logic` (instalowany w `project.sh` w linii 27).
     - Brakuje `glon` (instalowany w `project.sh` w linii 26).
     - Nie wszystkie polecenia z `project.sh` są wyjaśnione.

6. **Sposób inicjalizacji projektu**
   - `project.sh` tworzy venv i instaluje narzędzia, ale brakuje instrukcji dla agenta, czy ma go uruchamiać przed każdą pracą.

7. **Język i odbiorca**
   - Należy ustalić, czy dokumentacja ma być po polsku czy po angielsku, i konsekwentnie ją zastosować.

## Rekomendacje

### Pilne (blokujące dla AI)

1. **Rozstrzygnąć, gdzie jest CONTRIBUTING**
   - Opcja A: Przywrócić pełną wersję do `CONTRIBUTING.md` (po angielsku lub polsku), a `README.md` przekształcić w opis projektu.
   - Opcja B: Przenieść pełną wersję do `docs/README.md`, a w root `CONTRIBUTING.md` dać tylko skrót z linkiem.
   - Workflow `.devin/workflows/analyze-documentation.md` preferuje opcję B.

2. **Jednolity język**
   - Wybrać język (zalecany polski — szef pisze po polsku, README.md jest po polsku) i zastosować w całym repozytorium.

3. **Utworzyć brakujące pliki**
   - `TODO.md` — szablon zgodny z sekcją 4 CONTRIBUTING.
   - `CHANGELOG.md` — pusty szablon.
   - `tests/` lub inny katalog testowy — jeśli projekt ma być zgodny ze standardem.

4. **Uzupełnić brakujące narzędzia**
   - Dodać opisy `code2logic` i `glon`.
   - Wskazać, które narzędzia są opcjonalne, a które obowiązkowe.

### Ważne

5. **Dodać sekcję "Jak pracować, gdy nie ma agentów specjalistycznych"**
   - Fallback dla agentów takich jak Cascade / Devin, które nie mają `test-agent` czy `repair-agent`.
   - Na przykład: jeśli `test-agent` nie jest dostępny, uruchom `pytest` / `npm test` / inny lokalny runner.

6. **README.md jako opis projektu**
   - `README.md` powinien zawierać: cel projektu, instalację, uruchomienie, strukturę katalogów.
   - Obecnie zawiera CONTRIBUTING — należy to rozdzielić.

## Podsumowanie dla szefa

- `CONTRIBUTING.md` jest zrozumiały dla AI, ale **nie jest jednoznaczny** z powodu podwójnego źródła prawdy i niespójności językowej.
- Logika działania (sprawdź → zaplanuj → deleguj → testuj → waliduj → dokumentuj → commituj) jest poprawnie opisana, ale **brakuje implementacji**: `TODO.md`, `CHANGELOG.md`, testów, CI.
- Największy problem: `README.md` zawiera pełny CONTRIBUTING, a `CONTRIBUTING.md` jest skróconą wersją — to myli AI i ludzi.
- Zalecana naprawa: wybrać jedno źródło prawdy, ujednolicić język, uzupełnić brakujące pliki i dodać fallback dla agentów specjalistycznych.
