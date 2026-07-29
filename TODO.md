# TODO Roadmap & Task Index

[![Status: Active](https://img.shields.io/badge/Status-Active_Roadmap-blue.svg)](#)

> Centralna lista zadań i kamieni milowych dla repozytorium **Governance & Onboarding Hub**.

---

## 📌 Etap 1: Przebudowa Przewodnika i Kolejności Plików w `README.md`

- [ ] **Dodanie sekcji z diagramem ASCII w `README.md`**:
  - [ ] Stworzyć diagram sekwencji i zależności pokazujący **co z czego wynika** oraz **dokładną kolejność chronologiczną**:
        `USER_REQUEST` → `user-mateusz.md` → `project/ticket-{NNN}/README.md` → `TODO.md` → `ai-{NAME}.md` + `ai-{NAME}-logs.md` → `VERSION` + `CHANGELOG.md`
- [ ] **Zdefiniowanie ról plików w strukturze**:
  - [ ] **`user-{NAME}.md`**: Notatki, zadania i stały kontekst zapytania od użytkownika.
  - [ ] **`ai-{NAME}.md`**: Mózg agenta (rozumienie intencji, plan, akceptacja).
  - [ ] **`ai-{NAME}-logs.md`**: Dedykowany plik z surowymi logami agenta.
  - [ ] **`changelog.md`**: Rejestr zmian dla pojedynczego ticketu.
  - [ ] **`preprompt.md`**: Wyciągnięte wytyczne z `user-{NAME}.md` i workflow.

---

## 📂 Etap 2: Struktura Katalogu `project/` i Skrypty Automatyzujące

- [ ] **Stworzenie `project/README.md`**:
  - [ ] Opisać przeznaczenie folderu `project/`.
  - [ ] Dodać linki do dokumentacji głównej `wellmanifest/new-project` oraz nawigacyjne menu ticketów.
- [ ] **Stworzenie skryptu `project/new-ticket.sh`**:
  - [ ] Automatyczne generowanie katalogu `project/ticket-{NNN}/`.
  - [ ] Generowanie plików: `user-{NAME}.md`, `ai-{NAME}.md`, `ai-{NAME}-logs.md`, `changelog.md`, `preprompt.md`.
- [ ] **Stworzenie skryptu `project/readme.sh`**:
  - [ ] Skanowanie ticketów i automatyczne generowanie/aktualizacja menu w `project/README.md`.

---

## 📝 Etap 3: Plik Wytycznych `preprompt.md`

- [ ] Stworzyć plik `preprompt.md` w korzeniu repozytorium z szablonami promptów, schematami ekstrakcji i wytycznymi dopytywania użytkownika o nowe wymagania.

---

## 📚 Etap 4: Dokumentacja i Diagramy w `docs/`

- [ ] Rozbudowa dokumentacji w `docs/` o diagramy architektury, logiki i zakresów odpowiedzialności.
