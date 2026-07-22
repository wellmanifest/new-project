# Instrukcja pracy dla agentów AI (Opus48Medium)

## 1. Po co ten plik

Ten dokument jest **punktem wejścia** dla agenta AI pracującego w tym repozytorium. Jest krótszą, repozytoryjną instrukcją operacyjną, która prowadzi do szczegółowych źródeł prawdy.

Repozytorium `new-project` to obecnie **zestaw standardów dokumentacyjnych, polityk i skryptu analitycznego** (`project.sh`). Nie jest to gotowa aplikacja — nie ma tu `src/`, `tests/`, CI, Dockera ani wdrożenia.

---

## 2. Kolejność czytania

Przed każdą zmianą przeczytaj w tej kolejności:

1. **`Opus48Medium/CONTRIBUTING.md`** — ten plik.
2. **`CONTRIBUTING.md`** (root) — aktualny skrót punktu wejścia dla agentów.
3. **`docs/README.md`** — indeks dokumentacji i źródeł prawdy.
4. **`GPT56Luna/CONTRIBUTING.md`** — szczegółowa instrukcja operacyjna dla tego repozytorium.
5. **`GPT56Luna/ANALIZA-DOKUMENTACJI.md`** — ustalenia, znane luki i historia decyzji.
6. **`README.md`** — ogólny standard pracy (po polsku).
7. **`POLICY.md`** — polityki nazewnictwa, modułowości, zależności i bezpieczeństwa.
8. **`project.sh`** — jeśli zadanie dotyczy narzędzi lub środowiska.
9. **`TODO.md`** — jeśli istnieje; utwórz lub zaktualizuj dla większych zadań.

**Hierarchia ważności, gdy dokumenty są sprzeczne:**

1. Bezpośrednie polecenie użytkownika.
2. Rzeczywisty stan repozytorium i kodu.
3. `GPT56Luna/CONTRIBUTING.md`.
4. `Opus48Medium/CONTRIBUTING.md`.
5. Root `CONTRIBUTING.md`.
6. `README.md`.
7. `POLICY.md`.

---

## 3. Co jest potwierdzone, a czego nie zakładać

### Potwierdzone pliki i katalogi

- `README.md`, `CONTRIBUTING.md` (root), `POLICY.md`, `LICENSE`.
- `docs/README.md` — indeks dokumentacji.
- `project.sh` — skrypt przygotowania środowiska i analizy.
- `GPT56Luna/CONTRIBUTING.md` — szczegółowa instrukcja operacyjna.
- `GPT56Luna/ANALIZA-DOKUMENTACJI.md` — analiza luk i decyzji.
- `.devin/workflows/analyze-documentation.md` — workflow weryfikacji dokumentacji.
- Foldery innych agentów (`Kimik27/`, `Opus48Medium/`, `SWE17/`) zawierają ich analizy i notatki.

### Elementy NIEpotwierdzone

Nie zakładaj istnienia poniższych elementów bez fizycznej weryfikacji:

- kod aplikacji (`src/`),
- testy (`tests/`),
- konfiguracja CI,
- pliki Docker,
- `TODO.md`, `CHANGELOG.md` (mogą istnieć tylko podczas trwającej pracy),
- agenci `test-agent`, `repair-agent`, `validator-agent`, `todo-agent`, `doctor-agent` — są opisani w `README.md`, ale nie ma tu ich kodu ani sposobu wywołania.

---

## 4. Przepływ pracy

### 4.1. Przed zmianą

1. Przeczytaj dokumentację w kolejności z sekcji 2.
2. Sprawdź `git status` i ostatnie commity (`git log --oneline -10`).
3. Sprawdź strukturę katalogów (`tree -L 2` lub `ls -R`).
4. Przeczytaj `project.sh`, jeśli zadanie dotyczy narzędzi.
5. Utwórz lub zaktualizuj `TODO.md` dla zadania obejmującego więcej niż jeden mały krok.
6. Zapisz założenia, ryzyka i kryteria akceptacji.

### 4.2. Podczas pracy

1. Wprowadzaj minimalne, logiczne zmiany.
2. Po każdym etapie sprawdź `git diff`.
3. Nie uruchamiaj zakomentowanych poleceń z `project.sh` bez uzasadnienia.
4. Nie opisuj jako dostępnych elementów, których nie potwierdziłeś.
5. Jeśli napotkasz sprzeczność między dokumentacją a rzeczywistością, zapisz ją w `TODO.md` lub raporcie.

### 4.3. Po zmianie

1. Sprawdź `git diff` — upewnij się, że nie ma przypadkowych zmian.
2. Sprawdź, czy nie wyciekły sekrety lub dane środowiskowe.
3. Sprawdź, czy odwołania do plików i sekcji są nadal poprawne.
4. Zaktualizuj `TODO.md` i ewentualnie `CHANGELOG.md`.
5. Wykonaj commit tylko po zatwierdzeniu przez użytkownika lub gdy jest to wyraźnie zlecone.

---

## 5. Narzędzia w `project.sh`

Skrypt `project.sh` przygotowuje środowisko i uruchamia narzędzia analityczne. Niektóre polecenia są aktywne, inne zakomentowane, a inne tylko instalują pakiet.

### Aktywne polecenia

| Narzędzie | Komenda | Efekt |
|---|---|---|
| `code2llm` | `$VENV/bin/code2llm ./ -f all -o ./project --no-chunk --exclude '*.md'` | reprezentacja projektu w `./project` |
| `redup` | `$VENV/bin/redup scan . --format toon --output ./project --ext .mjs,.js,.php,.sh` | raport duplikatów w `./project` |
| `prefact` | `$VENV/bin/prefact -a -e "examples/**"` | analiza struktury projektu |
| `doql` | `$VENV/bin/doql adopt . --format less --output app.doql.less --force` | tworzy lub nadpisuje `app.doql.less` |
| `sumd` | `$VENV/bin/sumd .` | podsumowanie plików `.md` |
| `sumr` | `$VENV/bin/sumr .` | podsumowanie raportów |

### Pakiety instalowane, ale nie uruchamiane

- `regix`
- `glon`
- `code2logic`

Nie zakładaj ich działania bez sprawdzenia dokumentacji.

### Zakomentowane polecenia

Nie uruchamiaj bez uzasadnienia:

- `$VENV/bin/vallm batch ...` — wymaga modelu LLM i może być czasochłonne.
- `$VENV/bin/goal -a` — wymaga konfiguracji celów.

---

## 6. Zasady bezpieczeństwa i ograniczenia

- Nie commituj sekretów, haseł, tokenów ani kluczy API.
- Nie uruchamiaj `--force` bez sprawdzenia, czy nie nadpisze ważnych plików.
- Nie instaluj zależności globalnie (poza `venv`) bez wyraźnej zgody.
- Nie usuwaj testów ani nie wyłączaj ich bez udokumentowanej przyczyny.
- Nie twierdź, że coś działa, jeśli tylko zainstalowałeś pakiet.
- Zakomentowane komendy w `project.sh` nie są częścią aktualnego przepływu.

### Gdy agent specjalistyczny nie jest dostępny

Nazwy agentów `test-agent`, `repair-agent`, `validator-agent`, `todo-agent` i `doctor-agent` nie są potwierdzone w repozytorium. Nie wywołuj ich z samej nazwy.

Zamiast tego:

- wykonaj lokalną kontrolę adekwatną do zadania, jeśli istnieje potwierdzona komenda,
- dla dokumentacji sprawdź odwołania, spójność z `project.sh`, `git diff --check` i `git diff`,
- dla kodu najpierw znajdź rzeczywisty runner testów lub linter,
- jeśli nie ma testów ani runnera, zgłoś to jako ograniczenie,
- poproś użytkownika o decyzję, gdy wymagane narzędzie nie istnieje.

---

## 7. Kiedy zatrzymać się i zapytać człowieka

Zatrzymaj pracę i poproś o decyzję, gdy:

- wymagania są sprzeczne lub niepełne,
- operacja może być destrukcyjna (np. `rm -rf`, `git push --force`, nadpisanie plików),
- brakuje danych dostępowych,
- dokumentacja i kod wykluczają się w sposób wymagający wyboru architektonicznego,
- nie potwierdziłeś istnienia narzędzia/agenta, którego użycie jest wymagane.

---

## 8. Definition of Done

Zadanie jest ukończone, gdy:

- [ ] opis wskazuje aktualne źródła prawdy,
- [ ] opisany przepływ odpowiada rzeczywistym plikom,
- [ ] funkcje niepotwierdzone są wyraźnie oznaczone,
- [ ] komendy aktywne i zakomentowane nie są pomieszane,
- [ ] odwołania do plików i sekcji są poprawne,
- [ ] `git diff` nie zawiera przypadkowych zmian,
- [ ] znane luki i ryzyka są zapisane,
- [ ] raport zawiera zakres wykonanej weryfikacji.

---

## 9. Szybka ściągawka

```text
1. Czytaj: Opus48Medium/CONTRIBUTING.md → CONTRIBUTING.md (root) → docs/README.md → GPT56Luna/CONTRIBUTING.md
2. Sprawdź: git status, git log, struktura katalogów
3. Jeśli zadanie dotyczy narzędzi: przeczytaj project.sh i rozróżnij aktywne/zakomentowane
4. Nie zakładaj istnienia: src/, tests/, CI, Docker, agentów Subactor
5. Zapisz plan w TODO.md dla większych zadań
6. Wprowadź minimalne zmiany, sprawdź diff, nie commituj sekretów
7. Zatrzymaj się przy destrukcyjnych lub niejasnych operacjach
```
