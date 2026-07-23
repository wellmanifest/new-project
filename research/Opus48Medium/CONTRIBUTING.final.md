# CONTRIBUTING — przewodnik pracy dla agentów AI i ludzi

> **Rola tego pliku:** wykonalny punkt wejścia dla agenta AI. Mówi, co przeczytać, w jakiej
> kolejności pracować, jakich narzędzi *realnie* można użyć i kiedy się zatrzymać. Opisy są
> zgodne z faktycznym stanem repozytorium — nie zakładaj niczego, czego nie potwierdzisz.
>
> Uwaga: foldery `GPT56Luna/`, `Kimik27/`, `SWE17/`, `Opus48Medium/` to równoległe analizy
> różnych modeli (materiał pomocniczy), a nie kanoniczne źródła prawdy. Kanoniczne są pliki
> w katalogu głównym: `README.md`, `POLICY.md`, `project.sh`.

---

## 0. Hierarchia dokumentów (jedno źródło prawdy)

Każdy plik ma inną rolę i nie powiela pozostałych:

| Plik | Rola | Odpowiada na pytanie |
|------|------|----------------------|
| `README.md` | Pełny standard pracy (PL): proces, narzędzia, testy, Docker, wersjonowanie, changelog | *Jak wygląda pełny standard pracy* |
| `CONTRIBUTING.md` (ten plik) | Skrócony, wykonalny przewodnik + szybki start | *Od czego zacząć i co zrobić krok po kroku* |
| `POLICY.md` | Zasady: nazewnictwo, modularność, zależności, bezpieczeństwo | *Jakich reguł nie wolno złamać* |
| `TODO.md` | Dynamiczna kolejka pracy (istnieje tylko podczas pracy) | *Co zrobić jako następne* |
| `project.sh` | Inicjalizacja środowiska i uruchomienie narzędzi analizy | *Jak przygotować środowisko* |

Przy sprzeczności obowiązuje kolejność: **polecenie użytkownika > rzeczywisty stan repo > `POLICY.md` > `README.md` > `CONTRIBUTING.md`**.

---

## 1. Zasada nadrzędna

Przed napisaniem własnego rozwiązania agent **MUSI** sprawdzić, czy zadanie wykona już
istniejące narzędzie, skrypt lub workflow. **Nie odtwarzaj istniejącej funkcjonalności.**
Główny agent koordynuje pracę i deleguje ją do właściwych narzędzi.

---

## 2. Charakter repozytorium (stan potwierdzony)

To repozytorium zawiera **standardy dokumentacyjne, polityki i skrypt analityczny** — nie jest
to gotowa aplikacja biznesowa.

**Istnieje:** `README.md`, `CONTRIBUTING.md`, `POLICY.md`, `LICENSE`, `project.sh`,
`docs/README.md`, `.devin/workflows/analyze-documentation.md`.

**NIE zakładaj istnienia** (potwierdź fizycznie, zanim użyjesz lub opiszesz jako dostępne):

- kod aplikacji (`src/`), testy (`tests/`), konfiguracja CI, pliki Docker,
- `TODO.md` i `CHANGELOG.md` (powstają dopiero w trakcie pracy),
- agenci `test-agent`, `repair-agent`, `validator-agent`, `todo-agent`, `doctor-agent` —
  są *opisani* w `README.md §6`, ale w repo **nie ma ich kodu ani sposobu wywołania**.
  Traktuj ich jako docelowych/zewnętrznych; jeśli zadanie ich wymaga, a nie potwierdzisz
  ich dostępności — zatrzymaj się i zapytaj (patrz sekcja 7).

---

## 3. Szybki start

```bash
# Inicjalizacja środowiska: venv + instalacja narzędzi + analiza projektu do ./project
bash ./project.sh
```

Skrypt tworzy `venv/` i wywołuje narzędzia przez `venv/bin/<tool>` (patrz sekcja 5).

---

## 4. Obowiązkowy przebieg pracy

### 4.1. Przed zmianą
1. Przeczytaj `README.md`, `POLICY.md` oraz ten plik.
2. Sprawdź stan Git: `git status`, `git log --oneline -10`.
3. Sprawdź strukturę katalogów i istniejące narzędzia (`project.sh`, `venv/bin/`).
4. Dla zadania większego niż jeden krok utwórz/zaktualizuj `TODO.md` z etapami i kryteriami akceptacji.

### 4.2. Podczas pracy
1. Wprowadzaj **minimalne, logiczne zmiany**; po każdym etapie sprawdzaj `git diff`.
2. Nie uruchamiaj zakomentowanych poleceń z `project.sh` bez uzasadnienia.
3. Nie opisuj jako dostępnych elementów, których nie potwierdziłeś.
4. Sprzeczności między dokumentacją a rzeczywistością zapisuj w `TODO.md`.

### 4.3. Po zmianie
1. Przejrzyj `git diff` — brak przypadkowych zmian i sekretów.
2. Sprawdź, czy odwołania do plików i sekcji są nadal poprawne.
3. Zaktualizuj `TODO.md` i — jeśli dotyczy — `CHANGELOG.md`.
4. Commituj małymi, logicznymi krokami w formacie `<type>(<scope>): <opis>`
   (`feat`, `fix`, `docs`, `test`, `refactor`, `build`, `ci`, `chore`, `security`).
5. Push/commit wykonuj po zatwierdzeniu przez użytkownika lub gdy jest to wyraźnie zlecone.

---

## 5. Narzędzia w `project.sh` — co wolno uruchamiać

Skrypt `project.sh` przygotowuje środowisko i uruchamia narzędzia. Rozróżniaj polecenia
**aktywne**, pakiety **tylko instalowane** oraz polecenia **zakomentowane**.

### Aktywne polecenia (część bieżącego przepływu)

| Narzędzie | Komenda | Efekt |
|---|---|---|
| `code2llm` | `$VENV/bin/code2llm ./ -f all -o ./project --no-chunk --exclude '*.md'` | reprezentacja projektu dla LLM w `./project` |
| `redup` | `$VENV/bin/redup scan . --format toon --output ./project --ext .mjs,.js,.php,.sh` | raport duplikatów w `./project` |
| `prefact` | `$VENV/bin/prefact -a -e "examples/**"` | analiza struktury projektu |
| `doql` | `$VENV/bin/doql adopt . --format less --output app.doql.less --force` | tworzy/nadpisuje `app.doql.less` (sprawdź diff) |
| `sumd` | `$VENV/bin/sumd .` | podsumowanie plików `.md` |
| `sumr` | `$VENV/bin/sumr .` | podsumowanie raportów |

### Pakiety instalowane, lecz nie wywoływane w skrypcie

Zainstalowane, ale bez wywołania — nie zakładaj ich działania bez sprawdzenia dokumentacji:
`regix`, `glon`, `code2logic`.

### Polecenia zakomentowane (poza bieżącym przepływem)

Nie uruchamiaj bez uzasadnienia:
- `$VENV/bin/vallm batch ...` — wymaga modelu LLM (np. `qwen2.5-coder:7b`), może być czasochłonne.
- `$VENV/bin/goal -a` — wymaga konfiguracji celów.

> **Uwaga:** pełne opisy narzędzi (przeznaczenie, wejście, ograniczenia) są w `README.md §5`.
> `README.md §5` nie opisuje jeszcze `regix`, `glon`, `code2logic` — to znana luka do uzupełnienia.

---

## 6. Agenci i delegacja — gdy specjalista nie jest dostępny

`README.md §6` opisuje agentów (`test-agent`, `repair-agent`, `validator-agent`, `todo-agent`,
`doctor-agent`), ale w repo **nie ma ich kodu ani sposobu wywołania**. Nie wywołuj ich z samej nazwy.

Zamiast tego:
- dla dokumentacji: sprawdź odwołania, spójność z `project.sh`, `git diff --check` i `git diff`,
- dla kodu: najpierw znajdź rzeczywisty runner testów lub linter w repozytorium,
- jeśli nie ma testów ani runnera — zgłoś to jako **ograniczenie**, nie jako „testy zaliczone”,
- gdy wymagane narzędzie/agent nie istnieje — poproś użytkownika o decyzję.

---

## 7. Zasady bezpieczeństwa i kiedy się zatrzymać

**Ograniczenia operacyjne:**
- **Nie commituj sekretów**, haseł, tokenów ani kluczy API.
- **Nie uruchamiaj `--force`** bez sprawdzenia, czy nie nadpisze ważnych plików.
- **Nie instaluj zależności globalnie** (poza `venv`) bez wyraźnej zgody.
- **Nie usuwaj/nie wyłączaj testów** bez udokumentowanej przyczyny; nie zmieniaj oczekiwanego wyniku, by test przeszedł.
- **Nie twierdź, że coś działa**, jeśli tylko zainstalowałeś pakiet lub nie uruchomiłeś kodu.

**Zatrzymaj się i zapytaj człowieka, gdy:**
- wymagania są sprzeczne lub niepełne,
- operacja może być destrukcyjna (`rm -rf`, `git push --force`, nadpisanie plików),
- brakuje danych dostępowych,
- dokumentacja i kod wykluczają się i wymagają decyzji architektonicznej,
- zadanie wymaga narzędzia/agenta, którego dostępności nie potwierdziłeś.

---

## 8. Definition of Done (zmiany dokumentacyjne)

- [ ] opis wskazuje aktualne źródła prawdy i poprawne odwołania,
- [ ] opisany przepływ odpowiada rzeczywistym plikom,
- [ ] elementy niepotwierdzone są wyraźnie oznaczone,
- [ ] komendy aktywne i zakomentowane nie są pomieszane,
- [ ] `git diff` nie zawiera przypadkowych zmian ani sekretów,
- [ ] znane luki i ryzyka zapisano w `TODO.md`.

---

## 9. Ściągawka dla agenta

```text
1. Czytaj: CONTRIBUTING.md → README.md → POLICY.md (project.sh, jeśli o narzędzia)
2. Sprawdź: git status, git log, strukturę katalogów, venv/bin
3. Narzędzia: odróżnij aktywne / tylko instalowane / zakomentowane w project.sh
4. Nie zakładaj istnienia: src/, tests/, CI, Docker, agentów (test-/repair-/...)
5. Plan większego zadania zapisz w TODO.md
6. Minimalne zmiany → sprawdź diff → bez sekretów → logiczne commity
7. Stop przy operacjach destrukcyjnych, sprzecznych lub niepotwierdzonych
```
