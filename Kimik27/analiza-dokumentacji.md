# Analiza dokumentacji dla agentów AI

## Stan faktyczny

Przeanalizowano repozytorium `wellmanifest/new-project` pod kątem zgodności dokumentacji z rzeczywistym stanem projektu oraz czytelności dla agentów AI.

### Pliki źródłowe

- `CONTRIBUTING.md` — skrócona wersja angielska reguł pracy agentów.
- `README.md` — zawiera pełną polską wersję wytycznych `CONTRIBUTING.md` (nagłówek `# CONTRIBUTING.md`), a nie opis projektu.
- `POLICY.md` — polityki nazewnictwa, modułowości, zależności, bezpieczeństwa.
- `docs/` — **pusty katalog**.
- `project.sh` — skrypt inicjalizacji instalujący i uruchamiający narzędzia.
- `.devin/workflows/analyze-documentation.md` — workflow opisujący, jak sprawdzać dokumentację.

### Historia Git

- `b302616` — Initial commit (LICENSE).
- `0ae1938` — dodano `CONTRIBUTING.md`.
- `f55fc06` (HEAD) — dodano `POLICY.md`, workflow `analyze-documentation`, zmodyfikowano `CONTRIBUTING.md` oraz **przeniesiono `docs/README.md` → `README.md`** (`R065`).

W wyniku ostatniego commitu katalog `docs/` jest pusty, a `README.md` przejął treść, którą workflow zakłada w `docs/README.md`.

## Wyniki analizy

### 1. Czy plik w `docs/` oddaje logikę działania?

**Nie.** Katalog `docs/` jest pusty. Nie ma w nim żadnego pliku opisującego logikę pracy.

Powinien tam znajdować się przynajmniej `docs/README.md` z kompletnymi wytycznymi `CONTRIBUTING.md`, zgodnie z workflow `.devin/workflows/analyze-documentation.md`.

### 2. Czy `CONTRIBUTING.md` jest zrozumiały dla agentów AI?

**Częściowo.** Zalety:

- Jasne nagłówki i lista reguł.
- Konkretne odwołania do agentów i narzędzi.
- Format markdown ułatwia parsowanie.

Wady utrudniające pracę agentom AI:

- **Dwa źródła prawdy:** `CONTRIBUTING.md` (angielski skrót) i `README.md` (polska pełna wersja). Agent nie wie, który dokument jest nadrzędny.
- **Język:** `README.md` jest po polsku, `CONTRIBUTING.md` po angielsku. Agent musi obsługiwać oba języki lub zgubić kontekst.
- **Brak opisu projektu w `README.md`:** zamiast opisu projektu `new-project` znajduje się tam treść CONTRIBUTING, co jest sprzeczne z `CONTRIBUTING.md` sekcja 7 i `POLICY.md` sekcja 2.3.
- **Brakujące narzędzia:** `project.sh` używa `regix`, `glon`, `code2logic`, które nie są opisane ani w `CONTRIBUTING.md`, ani w `README.md`.
- **Nieistniejące pliki referencyjne:** dokument wspomina `TODO.md` i `CHANGELOG.md`, które nie istnieją w repozytorium.
- **Agenci Subactor:** opisani jako dostępni (`test-agent`, `repair-agent`, `validator-agent`, `todo-agent`, `doctor-agent`), ale nie ma potwierdzenia, że są skonfigurowani w tym repozytorium.

### 3. Co brakuje lub co należy dopisać?

#### Pilne

1. **Przywrócić lub utworzyć `docs/README.md`**
   - Zgodnie z workflow `analyze-documentation.md`, powinien zawierać pełne wytyczne CONTRIBUTING wraz z opisem narzędzi.
   - Obecnie cała treść znajduje się w `README.md`, co psuje semantykę plików.

2. **Naprawić `README.md`**
   - Powinien zawierać krótki opis projektu, cel, sposób uruchomienia, strukturę katalogów.
   - Obecna treść CONTRIBUTING powinna trafić do `docs/README.md` lub do `CONTRIBUTING.md`.

3. **Dodać opis narzędzi używanych w `project.sh`:**
   - `regix`
   - `glon`
   - `code2logic`
   - Brakuje też opisu wariantów instalacji `goal` (lokalna ścieżka `../goal/` vs PyPI).

#### Ważne

4. **Ujednolicić język**
   - Wybrać jeden język dokumentacji (polski lub angielski) albo utrzymywać równoległe wersje w sposób uporządkowany.

5. **Utworzyć szablon `TODO.md`**
   - Dokumentacja wymaga `TODO.md`, ale plik nie istnieje. Agent nie ma gdzie zapisać planu pracy.

6. **Utworzyć `CHANGELOG.md`**
   - Wymagany przez `CONTRIBUTING.md` sekcja 14 i Definition of Done.

7. **Dodać wskazówkę o workflow `analyze-documentation.md`**
   - Root `CONTRIBUTING.md` powinien wspomnieć, że istnieje gotowy workflow analizy dokumentacji.

### 4. Zalecenia dotyczące struktury

```text
new-project/
├── README.md                    # Opis projektu (cel, uruchomienie, struktura)
├── CONTRIBUTING.md              # Skrót + odsyłacz do docs/README.md
├── docs/
│   └── README.md                # Pełne wytyczne pracy agentów
├── POLICY.md                    # Polityki projektu
├── project.sh                   # Skrypt inicjalizacji
├── TODO.md                      # Aktualne zadania (tworzony podczas pracy)
├── CHANGELOG.md                 # Historia zmian
└── .devin/workflows/
    └── analyze-documentation.md
```

## Podsumowanie

Obecny stan dokumentacji jest sprzeczny z własnymi regułami zapisanymi w `CONTRIBUTING.md` i `POLICY.md`:

- `README.md` nie opisuje projektu.
- `docs/` jest pusty, choć workflow zakłada tam pełną dokumentację.
- Nie wszystkie narzędzia z `project.sh` są opisane.
- Brakuje `TODO.md` i `CHANGELOG.md`.

Dla agenta AI największym problemem jest **brak pojedynczego źródła prawdy** i niejasność, który dokument jest aktualny: `README.md` czy `CONTRIBUTING.md`.

Rekomendacja: przenieść pełne wytyczne z `README.md` do `docs/README.md`, napisać nowy `README.md` z opisem projektu, uzupełnić opis narzędzi `regix`, `glon`, `code2logic`, oraz utworzyć szablony `TODO.md` i `CHANGELOG.md`.
