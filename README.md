# Centrum Zasad i Onboardingu (Governance & Onboarding Hub)

[![Purpose: Governance](https://img.shields.io/badge/Purpose-Governance_%26_Policy-blue.svg)](#)
[![AI Agent Ready](https://img.shields.io/badge/AI_Agents-Ready-success.svg)](#)

Witamy w **Centrum Zasad i Onboardingu**. Repozytorium to stanowi wyłączne, oficjalne źródło wytycznych, reguł bezpieczeństwa, automatyzacji oraz procedur współpracy pomiędzy **ludźmi (Human)** a **autonomicznymi agentami AI**.

---

## 📌 Standard Tworzenia Nowych Systemów

> [!IMPORTANT]
> **Obowiązkowe zasady dla każdego nowego projektu:**
> 1. **Każdy nowy system / aplikacja powstaje w OSOBNYM, dedykowanym repozytorium na GitHubie.**
> 2. **Każdy system obowiązkowo korzysta ze środowiska Docker (`Dockerfile`, `compose.yml`) oraz zestawu dedykowanych narzędzi deweloperskich.**
> 3. Niniejsze repozytorium jest centrum zarządczym (Governance Hub) i służy do prowadzenia ticketów, onboarding'u oraz egzekwowania polityk bezpieczeństwa.

---

## 🛠️ Zestaw Narzędzi Deweloperskich (Dev Tools)

Wszystkie wymagane narzędzia automatyzujące są instalowane i uruchamiane automatycznie poprzez skrypt **`./project.sh`** (w środowisku Linux/macOS) lub **`project.bat`** (w środowisku Windows).

Oto zwięzły opis narzędzi wchodzących w skład zestawu deweloperskiego:

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

> **Uruchomienie instalacji i analizy:**
> * Linux / macOS: `bash project.sh`
> * Windows: `project.bat`

---

## 📖 Przewodnik i Zasady Pracy (Opis w Języku Naturalnym)

*Poniższy opis stanowi przystępną wykładnię zasad zawartych w ścisłych plikach polityk [POLICY.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/POLICY.md) oraz [CONTRIBUTING.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/CONTRIBUTING.md). Jeśli formuła DSL w plikach jest dla kogoś trudna do zinterpretowania, ten przewodnik służy jako oficjalne wyjaśnienie.*

### 1. Hierarchia Ważności Źródeł Prawdy
W przypadku wystąpienia konfliktu informacji obowiązuje następująca kolejność ważności:
1. 👑 **Bezpośrednie polecenie użytkownika (`USER_REQUEST`)** – najwyższy autorytet.
2. 📁 **Aktualny stan plików w repozytorium (`FILESYSTEM`)**.
3. 🛡️ **[POLICY.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/POLICY.md)** – bezwzględne zasady i zakazy bezpieczeństwa.
4. 📋 **[CONTRIBUTING.md](file:///c:/Users/Praca/fork/wellmanifest/new-project/CONTRIBUTING.md)** – procedura pracy i maszyna stanów.
5. 📄 **README.md / Historia Git** – informacje pomocnicze i kontekstowe.

---

### 2. System Ticketów (`project/ticket-{NNN}`)
* **Wymóg zakładania**: Każde zadanie składające się z więcej niż 1 kroku lub wymagające użycia Agenta AI **musi** posiadać swój folder pod `project/ticket-{NNN}`.
* **Plik główny (`README.md`)**: Definiuje cel zadania, zakres, ryzyka i kryteria odbioru. Jest jedynym źródłem prawdy dla zakresu ticketu.
* **Pliki uczestników (`user-{NAME}.md`, `AI-{NAME}.md`)**: Każdy pracujący człowiek lub Agent AI zapisuje tam swoje instrukcje, plan i wykonane zmiany na podstawie szablonów z katalogu [templates/](file:///c:/Users/Praca/fork/wellmanifest/new-project/templates).
* **Logi (`logs.txt`)**: Wszystkie surowe wyniki komend i testów są dopisywane do pliku logów w formacie tekstowym.
* **⚠️ Retencja (Nie wolno usuwać ticketów!)**: Foldery ticketów są trwale zachowywane. Agentom **nie wolno ich usuwać**, chyba że po zakończonym projekcie użytkownik wyraźnie wyda takie polecenie.

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
Praca nad każdym zadaniem przechodzi przez cykl stanów:
`START` ➔ `ANALYSIS` ➔ `PLAN` ➔ `TOOLS` ➔ `DELEGATION` ➔ `EDIT` ➔ `VALIDATION` ➔ `PUBLICATION` ➔ `DONE` (lub `BLOCKED` w przypadku braku dowodów/blokady).

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
