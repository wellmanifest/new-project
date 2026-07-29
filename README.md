# Centrum Zasad i Onboardingu (Governance & Onboarding Hub)

[![Purpose: Governance](https://img.shields.io/badge/Purpose-Governance_%26_Policy-blue.svg)](#)
[![AI Agent Ready](https://img.shields.io/badge/AI_Agents-Ready-success.svg)](#)

Witamy w **Centrum Zasad i Onboardingu**. Repozytorium to stanowi wyłączne, oficjalne źródło wytycznych, reguł bezpieczeństwa, automatyzacji oraz procedur współpracy pomiędzy **ludźmi (Human)** a **autonomicznymi agentami AI**.

---

## 📐 Chronologia i Kolejność Tworzenia Plików ("Co z Czego Wynika")

Poniższy diagram ASCII ilustruje **dokładny przepływ i kolejność powstawania dokumentów** podczas realizowania nowego projektu / ticketu:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                1. USER_REQUEST                                   │
│            (Polecenie biznesowe / notatki przesłane przez Człowieka)             │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             2. user-{NAME}.md                                    │
│  (Ręczne notatki człowieka, surowe wytyczne i stały kontekst w ticket-00X)       │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                    3. project/ticket-{NNN}/README.md                             │
│   (Mózg Rozumienia: jak AI zrozumiało intencję, ryzyka, Acceptance Criteria)    │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                 4. TODO.md                                       │
│    (Checklista i harmonogram zadań krok-po-kroku w docelowym repozytorium)     │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                                         ▼
               🛑 ZATRZYMANIE PRAC & WERYFIKACJA UŻYTKOWNIKA 🛑
                   (Odbiór rozumienia intencji oraz TODO)
                                         │
                                         ▼
┌────────────────────────────────────────┴─────────────────────────────────────────┐
│              5. ai-{NAME}.md   ORAZ   ai-{NAME}-logs.md                           │
│  (Dziennik wykonawczy Agenta z planem) │ (Dedykowany plik surowych logów Agenta) │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                          6. VERSION & CHANGELOG.md                               │
│      (Aktualizacja numeru wersji oraz rejestru zmian po wykonaniu zadania)       │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📌 Standard Tworzenia Nowych Systemów

> [!CAUTION]
> 🛑 **BEZWZGLĘDNY ZAKAZ TWORZENIA TICKETÓW ANI PLIKÓW ZADAŃ W TYM REPOZYTORIUM:**
> Repozytorium `wellmanifest/new-project` jest wyznaczonym źródłem prawdy dla polityk (READ-ONLY Governance Hub).
> **W tym repozytorium NIE TWORZY SIĘ żadnych ticketów (`project/ticket-{NNN}`), zadań, logów ani plików projektu.**

> [!IMPORTANT]
> **Obowiązkowy przepływ pracy dla każdego nowego projektu (System X):**
> 1. **Czytanie Zasad:** Agent AI odczytuje polityki i reguły z niniejszego repozytorium `wellmanifest/new-project`.
> 2. **Przejście do Docelowego Repozytorium:** Agent przenosi się całkowicie do docelowego/nowego repozytorium wskazanego dla Systemu X (lub tworzy nowy folder projektu zadeklarowany przez użytkownika).
> 3. **Bootstrap w Nowym Repozytorium (Przed pisaniem kodu!):** W docelowym repozytorium Systemu X Agent od razu tworzy:
>    * `README.md` (architektura i zakres planowanego Systemu X)
>    * `VERSION` (wersja projektu, np. `0.1.0`)
>    * `CHANGELOG.md` (rejestr zmian)
>    * `TODO.md` (szczegółowa lista zadań i kroków do zrealizowania)
>    * `project/ticket-{NNN}/README.md` (rozumienie intencji zadania przez AI, zakres, ryzyka i kryteria odbioru)
>    * `project/ticket-{NNN}/user-{NAME}.md` (notatki człowieka & stały kontekst zapytania)
>    * `project/ticket-{NNN}/ai-{NAME}.md` & `project/ticket-{NNN}/ai-{NAME}-logs.md` (dziennik i logi agenta)
>    * `project/ticket-{NNN}/changelog.md` (rejestr zmian specyficzny dla ticketu)
>    * `project/ticket-{NNN}/preprompt.md` (wyciągnięte wytyczne i workflow)
>    * `Dockerfile` & `compose.yml` (środowisko kontenerowe)
>    * Skopiowane skrypty `project.sh` / `project.bat` oraz szablony z katalogu `templates/`.
> 4. 🛑 **ZATRZYMANIE PRAC I PRZEDSTAWIENIE 2 WIDOKÓW UŻYTKOWNIKOWI:** Agent zatrzymuje się przed napisaniem jakiegokolwiek kodu i przedstawia Użytkownikowi dwa kluczowe dokumenty do weryfikacji:
>    * 🧠 **Zrozumienie Intencji (`project/ticket-{NNN}/README.md`)**: Użytkownik sprawdza, czy AI poprawnie zrozumiało jego pomysł, cel i kryteria odbioru.
>    * 📋 **Plan Zadań (`TODO.md`)**: Użytkownik sprawdza, czy zaplanowana przez AI krok-po-kroku lista zadań jest odpowiednia i logiczna.
> 5. **Praca po Odbiorze Planu:** Po akceptacji planu przez Użytkownika, Agent uruchamia `project.sh` / `project.bat` w docelowym repozytorium do automatyzacji analizy i przechodzi do realizacji zadań z `TODO.md` wyłącznie tam.

---

## 📜 Opis Ról Plików w Strukturze Ticketu

| Plik | Rola i Opis |
| :--- | :--- |
| 👤 **`user-{NAME}.md`** | **Ręczne notatki człowieka**: zawiera surowe polecenia, wytyczne i kontekst. Służy jako stały kotwiczący kontekst przy zapytaniach do AI. |
| 🧠 **`project/ticket-{NNN}/README.md`** | **Mózg Rozumienia**: zawiera przemyślaną koncepcję AI, zakres, ryzyka i kryteria odbioru (Acceptance Criteria). |
| 🤖 **`ai-{NAME}.md`** | **Dziennik Wykonawczy Agenta**: plan krok-po-kroku, przypisane instrukcje i rejestr zrealizowanych zmian. |
| 📝 **`ai-{NAME}-logs.md`** | **Dedykowany plik logów Agenta**: surowe wyniki komend i testów wykonywanych wyłącznie przez danego agenta (logi nie mieszają się). |
| 📋 **`changelog.md`** | **Rejestr zmian ticketu**: historia wydań i modyfikacji specyficzna tylko dla tego jednego ticketu. |
| 🎯 **`preprompt.md`** | **Wytyczne i Workflow**: ustrukturyzowane informacje wyciągnięte przez AI z pliku `user-{NAME}.md` oraz zdefiniowane schematy pracy. |
| 🗺️ **`README.md`** (Master Menu) | **Główne Menu Nawigacyjne**: spina całą dokumentację, polityki, tickety i logi w czytelny spis treści z linkami. |

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
* **Plik główny (`README.md`)**: Definiuje cel zadania, zakres, ryzyka i kryteria odbioru w docelowym repozytorium. Jest jedynym źródłem prawdy dla zakresu ticketu.
* **Pliki uczestników (`user-{NAME}.md`, `ai-{NAME}.md`)**: Każdy pracujący człowiek lub Agent AI zapisuje tam swoje instrukcje, plan i wykonane zmiany na podstawie szablonów z katalogu `templates/`.
* **Logi (`ai-{NAME}-logs.md`)**: Wszystkie surowe wyniki komend i testów danego agenta są dopisywane do jego pliku logów w formacie tekstowym.
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
