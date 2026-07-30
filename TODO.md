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

## 📂 Etap 2: Uniwersalne Skrypty Automatyzujące i Wzorzec `project/`

- [x] **Stworzenie Wzorca `template/files/project.template.md` oraz `project/README.md`**:
  - [x] Stworzono szablon `project.template.md` w `template/files/` wg standardu `*.template.md`.
  - [x] Opisano przeznaczenie folderu `project/` z odnośnikami do dokumentacji `wellmanifest/new-project` i indeksem ticketów.
- [x] **Stworzenie Uniwersalnego Skryptu `project/new-ticket.sh`**:
  - [x] Automatyczne numerowanie i tworzenie katalogu `project/ticket-{NNN}/`.
  - [x] Inicjalizacja w ticketze plików `preprompt.md` (techniczne wytyczne i podlinkowane zasoby) oraz `changelog.md` (lokalny changelog).
  - [x] Automatyczne wywołanie `./project/readme.sh`.
- [x] **Stworzenie Uniwersalnego Skryptu `project/readme.sh`**:
  - [x] Skanowanie ticketów i automatyczna regeneracja tabeli menu w `project/README.md`.
- [x] **Uaktualnienie Reguł DSL (`C-TOOLS-006` w `CONTRIBUTING.md`)**:
  - [x] Nakaz kopiowania gotowych skryptów z huba zamiast ich ponownego generowania z braku tokenów.

---

## 📝 Etap 3: Plik Wytycznych `preprompt.md`

- [ ] Stworzyć plik `preprompt.md` w korzeniu repozytorium z szablonami promptów, schematami ekstrakcji technicznej i wytycznymi dopytywania użytkownika o nowe wymagania.

---

## 📚 Etap 4: Dokumentacja i Diagramy w `docs/`

- [ ] Rozbudowa dokumentacji w `docs/` o diagramy architektury, logiki i zakresów odpowiedzialności.
