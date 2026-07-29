# Centrum Zasad i Onboardingu (Governance & Onboarding Hub)

[![Purpose: Governance](https://img.shields.io/badge/Purpose-Governance_%26_Policy-blue.svg)](#)
[![AI Agent Ready](https://img.shields.io/badge/AI_Agents-Ready-success.svg)](#)

Repozytorium `wellmanifest/new-project` stanowi wyłączne, oficjalne źródło polityk bezpieczeństwa, procedur pracy oraz uniwersalnych narzędzi automatyzujących dla ludzi oraz autonomicznych agentów AI.

> **POLITYKA READ-ONLY (`P-CORE-007`):** Niniejsze repozytorium jest hubem zasad. Nie tworzy się w nim fizycznych ticketów, logów ani plików wykonawczych. Każdy nowy system (System X) jest tworzony i rozwijany w osobnym repozytorium.

---

## 1. Struktura Drzewa Plików Repozytorium Docelowego

```text
DOCELOWE REPOZYTORIUM SYSTEMU X (Root)
├── .env.example                 <-- (Szablon konfiguracji: PROJECT_USERS, DEFAULT_AGENT)
├── .env                         <-- (Lokalna konfiguracja uaktualniona z .env.example)
├── README.md                    <-- (Główne Menu Całego Projektu)
├── VERSION                      <-- (Wersja główna projektu, np. 0.1.0)
├── CHANGELOG.md                 <-- (Główny rejestr zmian projektu)
├── TODO.md                      <-- (Główna checklista kroków i zadań)
├── Dockerfile & compose.yml     <-- (Odizolowane środowisko kontenerowe)
├── project.sh / project.bat     <-- (Narzędzia analityczne: code2llm, redup, prefact, etc.)
│
└── project/                     <-- (Katalog zarządzania ticketami)
    ├── README.md                <-- (Menu Katalogu Project: opis, linki do huba i indeks ticketów)
    ├── readme.sh / .bat         <-- (Skrypt automatycznie aktualizujący project/README.md)
    ├── new-ticket.sh / .bat     <-- (Skrypt generujący strukturę nowego ticketu)
    │
    └── ticket-001/              <-- (Podkatalog Konkretnego Ticketu)
        ├── user-{NAME}.md       <-- (Notatki człowieka zdefiniowanego w .env / CLI)
        ├── preprompt.md         <-- (Wyciągnięte wytyczne z notatek & ustrukturyzowany workflow)
        ├── ai-{PROVIDER}.md     <-- (MÓZG AGENTA: rozumienie intencji, plan, Kryteria Odbioru)
        ├── ai-{PROVIDER}-logs.txt <-- (Dedykowany plik surowych logów tego agenta)
        └── changelog.md         <-- (Lokalny rejestr zmian dotyczący tylko tego ticketu)
```

---

## 2. Chronologia i Wynikanie ("Co z Czego Wynika")

Realizacja każdego zadania w docelowym repozytorium odbywa się według ściśle określonej kolejności:

1. **Wyszczególnienie Wymagań (`USER_REQUEST`)**
   * 1.1. Człowiek przekazuje inicjujące notatki, wytyczne i polecenie biznesowe.

2. **Inicjalizacja Korzenia Projektu (Root Level Bootstrap)**
   * 2.1. Tworzony jest plik konfiguracji `.env` (na bazie `.env.example`).
   * 2.2. Tworzone są pliki bazowe: `README.md` (Master Menu), `VERSION`, `CHANGELOG.md`, `TODO.md` oraz kontener `Dockerfile`/`compose.yml`.

3. **Inicjalizacja Katalogu `project/`**
   * 3.1. Tworzony jest `project/README.md` (Menu Ticketów), `project/readme.sh` oraz `project/new-ticket.sh`.

4. **Wywołanie Skryptu `new-ticket.sh` (`project/ticket-{NNN}/`)**
   * 4.1. Skrypt odczytuje listę aktywnych użytkowników z pliku `.env` (`PROJECT_USERS`) lub z flagi CLI `--users` i generuje odpowiednie pliki `user-{NAME}.md` (np. `user-mateusz.md`).
   * 4.2. Generowany jest pusty lokalny plik `changelog.md` przeznaczony dla tego ticketu.

5. **Ekstrakcja Wytycznych (`preprompt.md`)**
   * 5.1. Agent AI analizuje notatki z plików `user-{NAME}.md` i tworzy plik `preprompt.md`, zawierający ustrukturyzowane wymagania oraz krok-po-kroku workflow.

6. **Generowanie Mózgu AI (`ai-{AGENT}.md`) oraz Harmonogramu (`TODO.md`)**
   * 6.1. Z pliku `preprompt.md` Agent generuje plik `ai-{AGENT}.md` (MÓZG AI), zawierający rozumienie intencji, koncepcję architektury, zakres i **Kryteria Odbioru (Acceptance Criteria)**.
   * 6.2. Agent wpisuje listę zadań wykonawczych do głównego pliku `TODO.md`.

7. **Wstrzymanie Pracy i Akceptacja Planu (`P-CORE-008`)**
   * 7.1. Agent zatrzymuje przerwane kodowanie i przedstawia plik `ai-{AGENT}.md` oraz checklistę w `TODO.md` Użytkownikowi do weryfikacji.
   * 7.2. Pisanie kodu rozpoczyna się wyłącznie po wyraźnej zgodzie Użytkownika.

8. **Kodowanie, Logowanie i Rejestr Zmian**
   * 8.1. Podczas wykonania Agent zapisuje surowe wyjścia z terminala i testów do pliku `ai-{AGENT}-logs.md`.
   * 8.2. Po zakończeniu etapu Agent uzupełnia `project/ticket-{NNN}/changelog.md`, odznacza pozycje w `TODO.md`, a po wyznaczeniu wydania aktualizuje zbiorczy `CHANGELOG.md` i podbija `VERSION`.

---

## 3. Specyfikacja Plików i Kontrakty (DSL)

| Plik | Rola i Specyfikacja Kontraktu |
| :--- | :--- |
| **`.env.example`** | **Szablon Konfiguracji**: definiuje domyślne zmienne środowiskowe projektu (`PROJECT_USERS="mateusz"`, `DEFAULT_AGENT="antigravity"`). |
| **`user-{NAME}.md`** | **Kontekst Człowieka**: ręczne notatki i polecenia od danego użytkownika. Służy jako stały kontekst w promptach LLM. |
| **`preprompt.md`** | **Ustrukturyzowany Workflow**: przetworzone wytyczne z plików `user-*.md` ze zdefiniowanymi krokami wykonawczymi. |
| **`ai-{AGENT}.md`** | **Mózg Agenta AI**: rozumienie intencji, zakres prac, specyfikacja techniczna i Kryteria Odbioru (AC). |
| **`ai-{AGENT}-logs.md`** | **Dedykowane Logi**: wyłączne surowe wyjścia komend CLI i testów uruchamianych przez danego agenta. |
| **`changelog.md`** | **Lokalny Changelog**: wykaz zmian i edycji wykonanych wyłącznie w ramach danego ticketu. |
| **`project/README.md`** | **Master Menu**: centralny plik nawigacyjny indeksujący wszystkie tickety i ich pliki składowe. |

---

## 4. Interfejs CLI Skryptów Automatyzujących

### Skrypt `new-ticket.sh` / `new-ticket.bat`
Automatyzuje tworzenie struktury nowego ticketu na podstawie parametrów CLI lub pliku `.env`.

```bash
# Użycie podstawowe (pobiera PROJECT_USERS z pliku .env)
./project/new-ticket.sh --title "Implementacja Walidacji"

# Użycie z jawnym podaniem użytkowników i agenta
./project/new-ticket.sh --title "Naprawa Błędu" --users "mateusz,tom" --agent "codex"
```

### Skrypt `readme.sh` / `readme.bat`
Skanuje katalog `project/` i automatycznie aktualizuje spis ticketów w `project/README.md`.

```bash
# Aktualizacja indeksu w project/README.md
./project/readme.sh
```

---

## 5. Zasada Odbioru Planu przed Kodowaniem (`P-CORE-008`)

Przed rozpoczęciem edycji plików źródłowych w nowym systemie Agent AI **musi**:
1. Wygenerować plik `ai-{AGENT}.md` oraz uzupełnić `TODO.md`.
2. Przedstawić Użytkownikowi oba te dokumenty do wglądu.
3. Uzyskać wyraźną akceptację (`"Zgoda"`, `"Plan zatwierdzony"`) przed przejściem do fazy wykonawczej.

---

## 6. Przewodnik i Zasady Pracy (Opis w Języku Naturalnym)

*Poniższy opis stanowi przystępną wykładnię zasad zawartych w ścisłych plikach polityk [POLICY.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/POLICY.md) oraz [CONTRIBUTING.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/CONTRIBUTING.md). Jeśli formuła DSL w plikach jest dla kogoś trudna do zinterpretowania, ten przewodnik służy jako oficjalne wyjaśnienie.*

### 6.1. Hierarchia Ważności Źródeł Prawdy
W przypadku wystąpienia konfliktu informacji obowiązuje następująca kolejność ważności:
1. **Bezpośrednie polecenie użytkownika (`USER_REQUEST`)** – najwyższy autorytet.
2. **Aktualny stan plików w docelowym repozytorium (`FILESYSTEM`)**.
3. **[POLICY.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/POLICY.md)** – bezwzględne zasady i zakazy bezpieczeństwa.
4. **[CONTRIBUTING.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/CONTRIBUTING.md)** – procedura pracy i maszyna stanów.
5. **README.md / Historia Git** – informacje pomocnicze i kontekstowe.

---

### 6.2. System Ticketów (`project/ticket-{NNN}` w Docelowym Repozytorium)
* **Wymóg zakładania**: Każde zadanie składające się z więcej niż 1 kroku lub wymagające użycia Agenta AI **musi** posiadać swój folder pod `project/ticket-{NNN}` **w repozytorium docelowym projektu**.
* **Menu projektu (`project/README.md`)**: Służy jako Menu nawigacyjne do wszystkich ticketów z linkami do dokumentacji i uczestników.
* **Mózg Agenta (`ai-{AGENT}.md`)**: Definiuje rozumienie intencji, zakres, ryzyka i kryteria odbioru (Acceptance Criteria). Jest jedynym źródłem prawdy dla zakresu pracy danego agenta.
* **Pliki uczestników (`user-mateusz.md`, `user-tom.md`)**: Ręczne notatki człowieka wklejane przy każdym zleceniu jako stały kontekst.
* **Logi (`ai-{AGENT}-logs.md`)**: Wyłączne surowe wyjścia z konsoli i testów wykonywanych przez danego agenta.
* **Retencja (Nie wolno usuwać ticketów!)**: Foldery ticketów są trwale zachowywane w docelowym repozytorium. Agentom **nie wolno ich usuwać**, chyba że po zakończonym projekcie użytkownik wyraźnie wyda takie polecenie.

---

### 6.3. Bezpieczeństwo i Dobre Praktyki (`POLICY.md`)
* **Weryfikacja faktów**: Twierdzenia bez dowodów (np. "test przeszedł" bez uruchomienia komendy) są zabronione.
* **Ochrona sekretów**: Klucze API, tokeny i hasła nie mogą trafić do repozytorium ani logów.
* **Czyszczenie ścieżek**: W komitach i logach używamy ścieżek względnych. Zabronione jest wyciekanie lokalnych ścieżek bezwzględnych użytkownika (`C:/Users/...`).
* **Higiena kontekstu**: Wczytywanie dużych plików i logów odbywa się fragmentami (`head`, `tail`, paginacja), aby nie zapychać okna kontekstowego Agenta AI.
* **Zakaz niszczących komend**: Operacje takie jak `force push`, czyszczenie historii czy niezweryfikowane skasowanie plików wymagają zgody człowieka.

---

### 6.4. Wymagania Środowiskowe (Docker i Narzędzia)
* Każdy tworzony system **musi** być budowany i uruchamiany w odizolowanym środowisku **Docker** (`Dockerfile`, `compose.yml`).
* Należy obowiązkowo korzystać z zestawu narzędzi deweloperskich (`project.sh` / `project.bat`) do analizy i automatyzacji.

---

### 6.5. Maszyna Stanów (Przepływ Pracy)
Praca nad każdym zadaniem w docelowym repozytorium przechodzi przez cykl stanów:
`START` ➔ `ANALYSIS` ➔ `PLAN` ➔ `WAIT_FOR_APPROVAL` ➔ `TOOLS` ➔ `DELEGATION` ➔ `EDIT` ➔ `VALIDATION` ➔ `PUBLICATION` ➔ `DONE` (lub `BLOCKED` w przypadku braku dowodów/blokady).

---

## 7. Indeks Dokumentów Zarządczych i Skryptów

| Dokument / Skrypt | Rola i Opis |
| :--- | :--- |
| **[POLICY.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/POLICY.md)** | Ścisłe zasady bezpieczeństwa, zakazy i limity (MODE STRICT). |
| **[CONTRIBUTING.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/CONTRIBUTING.md)** | Procedura pracy, tickety, Docker i maszyna stanów (MODE PROCEDURAL). |
| **[AGENTS.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/AGENTS.md)** | Standardowy punkt wejścia dla agentów AI (Cursor, Claude Code, Antigravity itp.). |
| **[llms.txt](file:///c:/Users/Praca/fork/wellmanifest/new-project/llms.txt)** | Mapa dokumentacji dla modeli LLM. |
| **[project.sh](file:///c:/Users/Praca/fork/wellmanifest/new-project/project.sh)** / **[project.bat](file:///c:/Users/Praca/fork/wellmanifest/new-project/project.bat)** | Skrypty instalujące i uruchamiające zestaw narzędzi deweloperskich. |
| **[templates/](file:///c:/Users/Praca/fork/wellmanifest/new-project/templates)** | Czyste szablony dla ticketów i wpisów uczestników. |
