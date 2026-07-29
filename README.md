# Centrum Zasad i Onboardingu (Governance & Onboarding Hub)

[![Purpose: Governance](https://img.shields.io/badge/Purpose-Governance_%26_Policy-blue.svg)](#)
[![AI Agent Ready](https://img.shields.io/badge/AI_Agents-Ready-success.svg)](#)

Witamy w **Centrum Zasad i Onboardingu**. Repozytorium to stanowi wyłączne, oficjalne źródło wytycznych, reguł bezpieczeństwa, automatyzacji oraz procedur współpracy pomiędzy **ludźmi (Human)** a **autonomicznymi agentami AI**.

---

## 📂 1. Rzeczywista Struktura Drzewa Plików Repozytorium

```text
NOWE REPOZYTORIUM SYSTEMU X (Root)
├── 📜 README.md                 <-- (Główne Menu Całego Projektu)
├── 🚀 VERSION                   <-- (Wersja główna projektu, np. 0.1.0)
├── 📋 CHANGELOG.md              <-- (Główny rejestr zmian projektu)
├── 📝 TODO.md                   <-- (Główna checklista kroków i zadań)
├── 🐳 Dockerfile & compose.yml  <-- (Środowisko kontenerowe)
├── 🛠️ project.sh / project.bat  <-- (Skrypty narzędzi deweloperskich)
│
└── 📁 project/                  <-- (Katalog zarządzania ticketami)
    ├── 📜 README.md             <-- (Menu Katalogu Project: opis, linki do doku i indeks wszystkich ticketów)
    ├── ⚙️ readme.sh              <-- (Skrypt generujący/aktualizujący menu w project/README.md)
    ├── ⚙️ new-ticket.sh          <-- (Skrypt generujący nowy katalog ticketu)
    │
    └── 📁 ticket-001/           <-- (Katalog Konkretnego Ticketu)
        ├── 👤 user-Mateusz.md   <-- (Ręczne notatki Mateusza & stały kontekst zadania)
        ├── 👤 user-Tom.md       <-- (Ręczne notatki Toma - ZAWSZE tworzony domyślnie!)
        ├── 🎯 preprompt.md      (Wyciągnięte z user-* wytyczne oraz ustrukturyzowany workflow)
        ├── 🧠 ai-{NAME}.md      (MÓZG ROZUMIENIA AGENTA: intencja, plan, koncepcja, AC)
        ├── 📝 ai-{NAME}-logs.md (Dedykowane surowe logi z komend i testów danego agenta)
        └── 📋 changelog.md      (Lokalny rejestr zmian dotyczący tylko tego 1 ticketu)
```

---

## 📐 2. Chronologia i Wynikanie ("Co z Czego Wynika")

```text
[POLECENIE CZŁOWIEKA: USER_REQUEST]
               │
               ▼
[KROK I: ROOT BOOTSTRAP] ───► (README.md, VERSION, CHANGELOG.md, TODO.md, Docker)
               │
               ▼
[KROK II: INICJALIZACJA project/] ───► (project/README.md, readme.sh, new-ticket.sh)
               │
               ▼
[KROK III: URUCHOMIENIE new-ticket.sh] ───► Tworzy katalog project/ticket-001/ z plikami:
               │                             ├── user-Mateusz.md (Notatki Mateusza)
               │                             ├── user-Tom.md (Notatki Toma)
               │                             └── changelog.md (Lokalny rejestr ticketu)
               ▼
[KROK IV: EKSTRAKCJA WYTYCZNYCH] ─────────► Tworzy project/ticket-001/preprompt.md
               │
               ▼
[KROK V: SYNTEZA MÓZGU AI & TODO] ────────► Tworzy project/ticket-001/ai-{NAME}.md
               │                             oraz uzupełnia główny TODO.md
               ▼
🛑 [KROK VI: WERYFIKACJA UŻYTKOWNIKA] ────► Człowiek sprawdza ai-{NAME}.md oraz TODO.md
               │
               ▼
[KROK VII: KODOWANIE & LOGI] ──────────────► Zapisuje surowe wyjścia do ai-{NAME}-logs.md
               │                             i uaktualnia project/ticket-001/changelog.md,
               └───────────────────────────► a na koniec główny CHANGELOG.md & VERSION
```

---

## 📜 3. Szczegółowy Opis Ról Plików w Strukturze

| Poziom | Plik | Rola i Przeznaczenie |
| :--- | :--- | :--- |
| **Root** | 🗺️ `README.md` | **Główne Menu Nawigacyjne Projektu**: spina całą dokumentację, polityki, moduły i tickety w czytelny spis treści. |
| **Root** | 🚀 `VERSION` & 📋 `CHANGELOG.md` | **Rejestr Wydania Projektu**: zbiorczy numer wersji oraz wykaz wszystkich wprowadzonych modyfikacji w całym projekcie. |
| **Root** | 📝 `TODO.md` | **Główny Harmonogram Zadań**: checklista kroków realizowanych w repozytorium przez ludzi i agentów AI. |
| **`project/`** | 📜 `project/README.md` | **Menu Katalogu Project**: opisuje przeznaczenie katalogu `project/`, zawiera odnośniki do huba oraz dynamiczny indeks wszystkich ticketów i ich plików. |
| **`project/`** | ⚙️ `readme.sh` & `new-ticket.sh` | **Skrypty Automatyzacji**: `new-ticket.sh` tworzy strukturę nowego ticketu, a `readme.sh` aktualizuje menu w `project/README.md`. |
| **Ticket** | 👤 `user-Mateusz.md` & `user-Tom.md` | **Pliki Użytkowników**: zawierają ręczne notatki i polecenia od ludzi. Oba pliki są **zawsze tworzone domyślnie w każdym ticketze**. Służą jako stały kontekst zapytania. |
| **Ticket** | 🎯 `preprompt.md` | **Wytyczne i Workflow**: ustrukturyzowane informacje wyciągnięte przez AI z plików `user-*.md` oraz ustalony schemat prac. |
| **Ticket** | 🧠 `ai-{NAME}.md` | **MÓZG ROZUMIENIA AGENTA**: opis rozumienia intencji biznesowej, plan prac, koncepcja architektury oraz Kryteria Odbioru (Acceptance Criteria). |
| **Ticket** | 📝 `ai-{NAME}-logs.md` | **Dedykowany Plik Logów**: surowe wyjścia z konsoli i testów wykonywanych wyłącznie przez tego danego agenta. |
| **Ticket** | 📋 `changelog.md` (w ticketze) | **Lokalny Rejestr Zmian Ticketu**: wpisy dotyczące wyłącznie modyfikacji wykonanych w ramach danego ticketu. |

---

## 📌 Standard Tworzenia Nowych Systemów

> [!CAUTION]
> 🛑 **BEZWZGLĘDNY ZAKAZ TWORZENIA TICKETÓW ANI PLIKÓW ZADAŃ W TYM REPOZYTORIUM:**
> Repozytorium `wellmanifest/new-project` jest wyznaczonym źródłem prawdy dla polityk (READ-ONLY Governance Hub).
> **W tym repozytorium NIE TWORZY SIĘ żadnych ticketów (`project/ticket-{NNN}`), zadań, logów ani plików projektu.**

> [!IMPORTANT]
> **Obowiązkowy przepływ pracy dla każdego nowego projektu (System X):**
> 1. **Czytanie Zasad:** Agent AI odczytuje polityki i reguły z niniejszego repozytorium `wellmanifest/new-project`.
> 2. **Przejście do Docelowego Repozytorium:** Agent przenosi się całkowicie do docelowego/nowego repozytorium wskazanego dla Systemu X.
> 3. **Bootstrap w Nowym Repozytorium (Przed pisaniem kodu!):** W docelowym repozytorium Systemu X Agent tworzy korzeń projektu oraz katalog `project/`.
> 4. **Wstrzymanie Pracy i Weryfikacja:** Agent przedstawia Szefowi / Użytkownikowi widok intencji w `project/ticket-{NNN}/ai-{NAME}.md` oraz checklistę w `TODO.md` i czeka na zgodę.
> 5. **Praca po Odbiorze Planu:** Po akceptacji planu, Agent uruchamia `./project.sh` / `project.bat` w docelowym repozytorium i realizuje kodowanie pod kontenerami Docker.

---

## 🛠️ Zestaw Narzędzi Deweloperskich i Zasada "Dev Tools First"

> [!TIP]
> ⚡ **Zasada Oszczędności Tokenów i Czasu dla Agentów AI:**
> Agenci AI mają **kategoryczny nakaz** uruchamiania skryptu `./project.sh` (Linux/macOS) lub `project.bat` (Windows) w docelowym repozytorium projektu przed rozpoczęciem analizy kodu.
> * **Jak to działa?** Agent nie traci tokenów ani czasu na żmudne czytanie plik po pliku. Narzędzia (`code2llm`, `redup`, `prefact`, `doql`, `sumd`, `goal`) wykonują całą ciężką pracę analityczną i generują zwięzłe raporty pod katalogiem `./project/` w repozytorium docelowym.
> * **Efekt:** Agent odczytuje gotowe raporty z narzędzi, błyskawicznie dowiaduje się o stanie kodu lub błędach i od razu podejmuje celne działania.

| Narzędzie | Krótki Opis i Przeznaczenie |
| :--- | :--- |
| 📦 **`code2llm`** | Pakuje kod źródłowy i strukturę projektu w zoptymalizowany format dla modeli AI/LLM (zapisuje analizę w podkatalogu `./project`). |
| 🔄 **`redup`** | Skaner wykrywający powtórzenia i redundancje w kodzie źródłowym (generuje raport w formacie `toon`). |
| 🛠️ **`prefact`** | Narzędzie do automatycznego przygotowywania refaktoryzacji oraz analizy zależności w kodzie. |
| 🗄️ **`doql`** | Narzędzie analityczne generujące podsumowania strukturalne i relacyjne projektu (`app.doql.less`). |
| 📊 **`sumd` / `sumr`** | Narzędzia generujące automatyczne raporty i podsumowania z zawartości plików i struktur repozytorium. |
| 🎯 **`goal`** | Narzędzie do weryfikacji celów projektowych i zgodności ze specyfikacją wymagań. |
| 🔤 **`code2logic`** / **`glon`** / **`regix`** | Narzędzia pomocnicze do zamiany kodu na reguły logiczne, operacji tekstowych i parsowania. |
| 🤖 **`vallm`** | Moduł semantycznej walidacji i wsadowego przetwarzania kontekstu dla agentów i modeli LLM. |

---

## 📖 Przewodnik i Zasady Pracy (Opis w Języku Naturalnym)

*Poniższy opis stanowi przystępną wykładnię zasad zawartych w ścisłych plikach polityk [POLICY.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/POLICY.md) oraz [CONTRIBUTING.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/CONTRIBUTING.md). Jeśli formuła DSL w plikach jest dla kogoś trudna do zinterpretowania, ten przewodnik służy jako oficjalne wyjaśnienie.*

### 1. Hierarchia Ważności Źródeł Prawdy
W przypadku wystąpienia konfliktu informacji obowiązuje następująca kolejność ważności:
1. 👑 **Bezpośrednie polecenie użytkownika (`USER_REQUEST`)** – najwyższy autorytet.
2. 📁 **Aktualny stan plików w docelowym repozytorium (`FILESYSTEM`)**.
3. 🛡️ **[POLICY.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/POLICY.md)** – bezwzględne zasady i zakazy bezpieczeństwa.
4. 📋 **[CONTRIBUTING.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/CONTRIBUTING.md)** – procedura pracy i maszyna stanów.
5. 📄 **README.md / Historia Git** – informacje pomocnicze i kontekstowe.

---

### 2. System Ticketów (`project/ticket-{NNN}` w Docelowym Repozytorium)
* **Wymóg zakładania**: Każde zadanie składające się z więcej niż 1 kroku lub wymagające użycia Agenta AI **musi** posiadać swój folder pod `project/ticket-{NNN}` **w repozytorium docelowym projektu**.
* **Menu projektu (`project/README.md`)**: Służy jako Menu nawigacyjne do wszystkich ticketów z linkami do dokumentacji i uczestników.
* **Mózg Agenta (`ai-{NAME}.md`)**: Definiuje rozumienie intencji, zakres, ryzyka i kryteria odbioru (Acceptance Criteria). Jest jedynym źródłem prawdy dla zakresu pracy danego agenta.
* **Pliki uczestników (`user-Mateusz.md`, `user-Tom.md`)**: Ręczne notatki człowieka wklejane przy każdym zleceniu jako stały kontekst.
* **Logi (`ai-{NAME}-logs.md`)**: Wyłączne surowe wyjścia z konsoli i testów wykonywanych przez danego agenta.
* **⚠️ Retencja (Nie wolno usuwać ticketów!)**: Foldery ticketów są trwale zachowywane w docelowym repozytorium. Agentom **nie wolno ich usuwać**, chyba że po zakończonym projekcie użytkownik wyraźnie wyda takie polecenie.

---

### 3. Bezpieczeństwo i Dobre Praktyki (`POLICY.md`)
* **Weryfikacja faktów**: Twierdzenia bez dowodów (np. "test przeszedł" bez uruchomienia komendy) są zabronione.
* **Ochrona sekretów**: Klucze API, tokeny i hasła nie mogą trafić do repozytorium ani logów.
* **Czyszczenie ścieżek**: W komitach i logach używamy ścieżek względnych. Zabronione jest wyciekanie lokalnych ścieżek bezwzględnych użytkownika (`C:/Users/...`).
* **Higiena kontekstu**: Wczytywanie dużych plików i logów odbywa się fragmentami (`head`, `tail`, paginacja), aby nie zapychać okna kontekstowego Agenta AI.
* **Zakaz niszczących komend**: Operacje takie jak `force push`, czyszczenie historii czy niezweryfikowane skasowanie plików wymagają zgody człowieka.

---

### 4. Wymagania Środowiskowe (Docker i Narzędzia)
* Każdy tworzony system **musi** być budowany i uruchamiany w odizolowanym środowisku **Docker** (`Dockerfile`, `compose.yml`).
* Należy obowiązkowo korzystać z zestawu narzędzi deweloperskich (`project.sh` / `project.bat`) do analizy i automatyzacji.

---

### 5. Maszyna Stanów (Przepływ Pracy)
Praca nad każdym zadaniem w docelowym repozytorium przechodzi przez cykl stanów:
`START` ➔ `ANALYSIS` ➔ `PLAN` ➔ `WAIT_FOR_APPROVAL` ➔ `TOOLS` ➔ `DELEGATION` ➔ `EDIT` ➔ `VALIDATION` ➔ `PUBLICATION` ➔ `DONE` (lub `BLOCKED` w przypadku braku dowodów/blokady).

---

## 📂 Szybki Indeks Dokumentów Zarządczych i Skryptów

| Dokument / Skrypt | Rola i Opis |
| :--- | :--- |
| 🛡️ **[POLICY.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/POLICY.md)** | Ścisłe zasady bezpieczeństwa, zakazy i limity (MODE STRICT). |
| 📋 **[CONTRIBUTING.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/CONTRIBUTING.md)** | Procedura pracy, tickety, Docker i maszyna stanów (MODE PROCEDURAL). |
| 🤖 **[AGENTS.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/AGENTS.md)** | Standardowy punkt wejścia dla agentów AI (Cursor, Claude Code, Antigravity itp.). |
| 🗺️ **[llms.txt](file:///c:/Users/Praca/fork/wellmanifest/new-project/llms.txt)** | Mapa dokumentacji dla modeli LLM. |
| 🛠️ **[project.sh](file:///c:/Users/Praca/fork/wellmanifest/new-project/project.sh)** / **[project.bat](file:///c:/Users/Praca/fork/wellmanifest/new-project/project.bat)** | Skrypty instalujące i uruchamiające zestaw narzędzi deweloperskich. |
| 📂 **[templates/](file:///c:/Users/Praca/fork/wellmanifest/new-project/templates)** | Czyste szablony dla ticketów i wpisów uczestników. |
