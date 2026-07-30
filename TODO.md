# TODO Roadmap & Task Index

[![Status: Active](https://img.shields.io/badge/Status-Active_Roadmap-blue.svg)](#)

> Centralna lista zadań i kamieni milowych dla repozytorium **Governance & Onboarding Hub**.

---

## 📌 Etap 1: Przebudowa Przewodnika i Kolejności Plików w `README.md`

- [x] **Wytyczne i Specyfikacja w `README.md`**:
  - [x] Wyszczególnienie sekcji "Co z czego wynika" w czytelnych punktach i podpunktach.
  - [x] Zdefiniowanie ról plików: `user-{github_username}.md` (tworzony na żądanie z nazwy użytkownika GitHub), `preprompt.md` (techniczne wskazania i zasoby ticketu), `ai-{PROVIDER}.md` (MÓZG AI), `ai-{PROVIDER}-logs.txt` (dedykowane logi CLI) oraz `changelog.md` (lokalny rejestr zmian ticketu).
  - [x] Dodanie narzędzia `todo2code` (`https://github.com/semcod/todo2code`) do skryptów deweloperskich `project.sh` i `project.bat` oraz tabeli narzędzi.

---

## 📂 Etap 2: Struktura Katalogu `project/` i Skrypty Automatyzujące

- [ ] **Stworzenie `project/README.md`**:
  - [ ] Opisać przeznaczenie folderu `project/`.
  - [ ] Dodać linki do dokumentacji głównej `wellmanifest/new-project` oraz nawigacyjne menu ticketów.
- [ ] **Stworzenie skryptu `project/new-ticket.sh` oraz `project/new-ticket.bat`**:
  - [ ] Automatyczne generowanie katalogu `project/ticket-{NNN}/`.
  - [ ] Inicjalizacja w ticketze plików `preprompt.md` (techniczne wytyczne i zasoby) oraz `changelog.md` (lokalny changelog).
  - [ ] Automatyczna obsługa konfiguracji `.env` (`PROJECT_USERS`) i opcji CLI `--users` oraz `--agent`.
- [ ] **Stworzenie skryptu `project/readme.sh` oraz `project/readme.bat`**:
  - [ ] Automatyczne skanowanie ticketów i aktualizacja menu nawigacyjnego w `project/README.md`.
- [ ] **Integracja Narzędzi Deweloperskich (`todo2code`)**:
  - [ ] Zapewnienie wykorzystania `todo2code` w `project.sh` oraz `project.bat` do automatycznej zamiany zadań z `TODO.md` na wykonywalne procesy dla agentów AI.

---

## 📝 Etap 3: Plik Wytycznych `preprompt.md`

- [ ] Stworzyć plik `preprompt.md` w korzeniu repozytorium z szablonami promptów, schematami ekstrakcji technicznej i wytycznymi dopytywania użytkownika o nowe wymagania.

---

## 📚 Etap 4: Dokumentacja i Diagramy w `docs/`

- [ ] Rozbudowa dokumentacji w `docs/` o diagramy architektury, logiki i zakresów odpowiedzialności.
