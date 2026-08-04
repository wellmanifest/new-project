# TODO Roadmap & Task Index

![Status: Active](https://img.shields.io/badge/Status-Active_Roadmap-blue.svg)

> Centralna lista zadań i kamieni milowych dla repozytorium **Governance & Onboarding Hub**.
> Etapy 1-4 poniżej są zakończonym planem historycznym. Aktywne zadania po
> wersji 0.9.0, wraz z kolejnością i kryteriami odbioru, znajdują się w
> [`docs/ROADMAP_AFTER_0.9.0.md`](docs/ROADMAP_AFTER_0.9.0.md).

## Aktywne utrzymanie standardu

- [ ] [`ticket-003`](project/ticket-003/README.md) — pogodzić dwa rozbieżne
  kontrakty 0.9.0 w kanoniczny 0.10.0, zachowując bounded delivery i zwalniając
  rezerwacje dla `PLAN/BLOCKED`. Stan: `PLAN / WAIT_FOR_APPROVAL`; zależna
  adopcja `todo2code` zmieni Koru na `z-ai/glm-5.2`.

- [x] [`ticket-001`](project/ticket-001/README.md) — ujednolicenie zasad
  edytowalnego utrzymania `wellmanifest/new-project`.
- [ ] [`ticket-002`](project/ticket-002/README.md) — integracja bezpiecznej
  adopcji manifestu z `goal`.

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
- [x] **Wprowadzenie Reguły Kontynuacji Ticketu (`P-CORE-009` / `C-TICKET-008`)**:
  - [x] Zakaz tworzenia nowych ticketów dla kolejnych promptów w ramach tego samego zadania.
  - [x] Zakaz modyfikowania notatek człowieka `user-{github_username}.md` przez Agenta AI.

---

## 📝 Etap 3: Wzorzec Techniczny `preprompt.template.md` i Wytyczne

- [x] **Przygotowanie Wzorca Technicznego w `template/files/preprompt.template.md`**:
  - [x] Stworzono w `template/files/preprompt.template.md` znormalizowany szablon dyrektyw technicznych ticketu (z polami na ograniczenia inżynieryjne, podlinkowaną specyfikację oraz twarde wymagania techniczne).
  - [x] Zaktualizowano skrypt `project/new-ticket.sh`, aby używał szablonu `template/files/preprompt.template.md` przy generowaniu ticketu.
  - [x] Udokumentowano rolę `preprompt.md` w `template/files/README.md` oraz w plikach zasad zarządczych.

---

## 📚 Etap 4: Obowiązek Tworzenia Diagramów Wizualnych w `docs/` Target Repozytorium

- [x] **Wprowadzenie Reguły Generowania Diagramów (`P-DOCS-001` & `C-DOCS-001`)**:
  - [x] Dodano regułę `P-DOCS-001` w `POLICY.md` oraz `C-DOCS-001` w `CONTRIBUTING.md` zobowiązującą Agentów AI do tworzenia wizualnych diagramów (Mermaid/Markdown) w katalogu `docs/` każdego docelowego repozytorium (np. `docs/ARCHITECTURE.md`, `docs/LOGIC_FLOW.md`).
  - [x] Zaktualizowano instrukcje dla agentów w `AGENTS.md` oraz w przewodniku `README.md`.
