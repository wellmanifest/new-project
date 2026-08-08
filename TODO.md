# TODO Roadmap & Task Index

![Status: Active](https://img.shields.io/badge/Status-Active_Roadmap-blue.svg)

> Centralna lista zadań i kamieni milowych dla repozytorium **Governance & Onboarding Hub**.
> Etapy 1-4 poniżej są zakończonym planem historycznym. Aktywne zadania po
> wersji 0.9.0, wraz z kolejnością i kryteriami odbioru, znajdują się w
> [`docs/ROADMAP_AFTER_0.9.0.md`](docs/ROADMAP_AFTER_0.9.0.md).

## Aktywne utrzymanie standardu

- [x] [`ticket-043`](project/ticket-043/README.md) — opublikowano naprawę z
  ticketu 042 jako immutable patch v0.13.2 dla downstream exact-SHA adoption.
  PR #64 przeszedł Linux, Windows i exact-head Validator; annotowany tag oraz
  GitHub Release wskazują `85631ea`, a downstream todo2code PR #70 przeszedł
  chronioną adopcję. Stan: `DONE / DONE`; klasyfikacja:
  `SERVICE / P0 / regression`.

- [x] [`ticket-042`](project/ticket-042/README.md) — naprawiono regresję P0 w
  chronionym snapshotcie lifecycle: typed GraphQL ma dostarczać rzeczywisty
  boolean `deleteBranchOnMerge` bez osłabiania deterministycznego walidatora.
  PR #62 przeszedł Linux, Windows i exact-head Validator; wydanie v0.13.2
  wskazuje `85631ea`, a downstream todo2code PR #70 przeszedł chronioną
  walidację i został scalony jako `f60d3cc`. Stan: `DONE / DONE`;
  klasyfikacja: `BUG / P0 / regression`.

- [x] [`ticket-041`](project/ticket-041/README.md) — opublikowano
  behavior-preserving repair z ticketu 040 jako immutable patch `v0.13.1` dla
  downstream exact-SHA adoption. Linux, Windows, exact-head Validator, czysty
  merge checkout i Vallm przeszły; Release wskazuje `7979cfe`. Stan:
  `DONE / DONE`;
  klasyfikacja: `SERVICE / P1 / health`.
- [x] [`ticket-040`](project/ticket-040/README.md) — obniżono pięć
  pre-existing punktów złożoności w zarządzanych źródłach Pythona bez
  wyłączania downstream review ani zmiany zachowania. Linux, Windows i
  exact-head Validator przeszły; PR #58 scalono jako `main@efec2cf`. Stan:
  `DONE / DONE`; klasyfikacja: `SERVICE / P1 / health`.
- [x] [`ticket-039`](project/ticket-039/README.md) — opublikowano atomowy
  kontrakt adopcji jako immutable `v0.13.0`. PR #56 przeszedł Linux, Windows i
  exact-head Validator; czysty merge `12158ef` przeszedł pełny Linux contract,
  a annotowany tag i GitHub Release wskazują ten SHA. Stan: `DONE / DONE`;
  klasyfikacja: `SERVICE / P2 / health`.
- [x] [`ticket-038`](project/ticket-038/README.md) — wdrożono jawny,
  provenance-bound kontrakt atomowej adopcji, który rozlicza wyłącznie
  zweryfikowany zbiór `managed`, pozostawiając seed, lock i target-local diff
  pod zwykłym budżetem, ownership i protected approval. PR #54 przeszedł Linux,
  Windows i exact-head Validator, po czym został scalony jako `main@1aa2600`.
  Stan: `DONE / DONE`; klasyfikacja: `FEATURE / P1 / requested`.
- [x] [`ticket-036`](project/ticket-036/README.md) — przypisano dokładne ścieżki
  `CHANGELOG.md` i `.env.example` do domyślnego workstreamu governance oraz
  dodano regresje własności i adopcji. PR #50 przeszedł Linux, Windows i
  exact-head Validator App, po czym został scalony jako `main@450a362`. Stan:
  `DONE / DONE`; klasyfikacja: `FEATURE / P1 / requested`.
- [x] [`ticket-037`](project/ticket-037/README.md) — opublikowano własność z
  ticketu 036 jako immutable `0.12.0`. PR #52 przeszedł Linux, Windows i
  exact-head Validator; czysty merge SHA `7be2e26` przeszedł pełny kontrakt,
  a annotowany tag i GitHub Release wskazują ten SHA. Stan: `DONE / DONE`;
  klasyfikacja: `SERVICE / P2 / health`.
- [x] [`ticket-035`](project/ticket-035/README.md) — GOV-DECISION gate w governance_check.
- [x] [`ticket-032`](project/ticket-032/README.md) — DECISION DSL + append decisions.md (validator #13/#14).
- [x] [`ticket-033`](project/ticket-033/README.md) — required checks z pliku head (validator #13). DONE.
- [x] [`ticket-034`](project/ticket-034/README.md) — kompletne mapowanie rule-enforcement (148/37, 0 luk).
- [x] [`ticket-027`](project/ticket-027/README.md) — rule-enforcement traceability. `DONE` (PR #37).
- [x] [`ticket-025`](project/ticket-025/README.md) — CI runs governance-env suite + completeness guard (PR #34).
- [x] [`ticket-030`](project/ticket-030/README.md) — single source required check names. `DONE` (PR #42).
  wymaganych checków (`governance/required-checks.json`) + bramka vs
  `ci.yml`. Stan: `IN_PROGRESS / VALIDATION` (impl on PR).
- [x] [`ticket-031`](project/ticket-031/README.md) — recomputable decision log contract. `DONE` (PR #44).
  (`C-DECISION-*`, schema, replay). Stan: `PLAN` → implementacja po 030.
- [ ] [`ticket-024`](project/ticket-024/README.md) — strategia
  `extendable` w `package-manifest.json` dla pliku, który target musi
  rozszerzyć. Stan: `PLAN / WAIT_FOR_APPROVAL`; klasyfikacja:
  `FEATURE / P1 / requested`.
- [x] [`ticket-022`](project/ticket-022/README.md) — kanoniczny Change
  Evaluation Contract oraz deterministyczny runtime TypeScript uruchamiany
  przez Bash. Stan: `DONE / DONE`; PR #31 scalony jako `166ebea` po Linux,
  Windows i exact-head Validator App approval. Klasyfikacja:
  `FEATURE / P1 / requested`.

- [x] [`ticket-006`](project/ticket-006/README.md) — zsynchronizowano roadmapę,
  TODO i indeks z wersją 0.10.0 oraz utworzono bounded backlog. Stan:
  `DONE / DONE`; PR #6 przeszedł CI, exact-head approval i został scalony.

- [x] [`ticket-007`](project/ticket-007/README.md) — opublikowano immutable
  `v0.10.0` i GitHub Release dla pełnego SHA
  `62ffb0dac1dba9294aa825ca5cc0344fefb33b0d`. Stan: `DONE / DONE`; PR #8,
  exact-head approval i czyste testy zakończone.

- [ ] [`ticket-008`](project/ticket-008/README.md) — pilot adopcji przez `goal`
  w pojedynczym workstreamie. Stan: `BACKLOG`; zależy od 002 i 007.

- [ ] [`ticket-009`](project/ticket-009/README.md) — pilot równoległych agentów
  i exact-head Validator App. Stan: `BACKLOG`; zależy od 002, 007 i 008.

- [x] [`ticket-010`](project/ticket-010/README.md) — opublikowano wersjonowany
  manifest pakietu i meta-walidację schematów. Stan: `DONE / DONE`; PR #10
  przeszedł CI i exact-head approval, po czym został scalony jako
  `main@956f350`.

- [x] [`ticket-011`](project/ticket-011/README.md) — natywne Windows CI dla
  wrapperów i generatora. Stan: `DONE / DONE`; PR #11 przeszedł Linux/Windows
  CI i exact-head approval, a ruleset `main` wymaga `windows-governance`.

- [ ] [`ticket-012`](project/ticket-012/README.md) — test upgrade/rollback
  między rzeczywistymi wydaniami. Stan: `BACKLOG`; zależy od 007 i 010.

- [ ] [`ticket-013`](project/ticket-013/README.md) — runbook Validator App i
  OpenRouter z diagramami, rotacją i diagnostyką. Stan: `BACKLOG`; zależy od
  007 i 009.

- [x] [`ticket-014`](project/ticket-014/README.md) — kanoniczny DSL
  `BUG > FEATURE > SERVICE`, osobny priorytet `P0–P3`, diff-aware CC i pakiet
  adopcyjny. Stan: `DONE / DONE`; PR #13 scalony jako `main@f7e0fd1`.

- [x] [`ticket-015`](project/ticket-015/README.md) — immutable wydanie 0.11.0
  zawierające manifest pakietu i DSL klasyfikacji. Stan:
  `DONE / DONE`; release SHA `cc9b046`, annotowany tag i GitHub Release
  `v0.11.0` opublikowane po czystej walidacji.

- [x] [`ticket-016`](project/ticket-016/README.md) — runtime enforcement
  klasyfikacji `BUG/FEATURE/SERVICE` przez `intent/v3`. Stan:
  `DONE / DONE`; PR #17 scalony do `main` jako `c02962b` po aktualnym approval
  i zielonych testach.

- [x] [`ticket-017`](project/ticket-017/README.md) — domknięcie lifecycle
  krótkotrwałych branchy ticketowych po merge/close. Stan: `DONE / DONE`; PR
  #20 scalono jako `d3240c0` po zielonym CI i exact-head approval, a branch
  implementacyjny został usunięty.
- [x] [`ticket-021`](project/ticket-021/README.md) — intent/v3, ref-aware allocation,
  clone-wide reservation i ochrona przed wieloma writerami w jednym worktree.

- [x] [`ticket-018`](project/ticket-018/README.md) — deterministyczny audyt
  ustawienia auto-delete i własności branchy przez otwarte PR-y. Stan:
  `DONE / DONE`; PR #24 przeszedł Linux/Windows CI, exact-head approval i merge.

- [ ] [`ticket-005`](project/ticket-005/README.md) — implementacja uszczelnienia
  evidence została scalona w PR #4. Stan: `BLOCKED / BLOCKED`; czeka na
  immutable release 0.10.0 i adopcję jego SHA w `todo2code`.

- [x] [`ticket-004`](project/ticket-004/README.md) — pogodzić dwa rozbieżne
  kontrakty 0.9.0 w kanoniczny 0.10.0, zachowując bounded delivery i zwalniając
  rezerwacje dla `PLAN/BLOCKED`. Stan: `DONE / DONE`; kolizję ID
  usunięto jako `ticket-004`, połączono `main@c54694a`, a wskazany przez
  Validator App helper naprawiono, przetestowano i zatwierdzono dla exact HEAD.
  Zależny `todo2code` używa lokalnie `z-ai/glm-5.2`.

- [x] [`ticket-001`](project/ticket-001/README.md) — ujednolicenie zasad
  edytowalnego utrzymania `wellmanifest/new-project`.
- [ ] [`ticket-002`](project/ticket-002/README.md) — integracja bezpiecznej
  adopcji manifestu z `goal`. Stan: `BLOCKED / BLOCKED`; implementacja lokalna
  czeka na opublikowany pełny SHA standardu.
- [x] [`ticket-003`](project/ticket-003/README.md) — zaufana walidacja PR przez
  allowlistowaną GitHub App lub zweryfikowaną atestację.

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
