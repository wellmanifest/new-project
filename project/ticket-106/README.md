# Ticket 106: Deterministic validator for the host-agnostic agent contract

- **ID**: ticket-106
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-22

## Cel i Zakres

`AGENTS.md` rule 22 wymaga, żeby każdy host LLM ładował ten sam fail-closed
kontrakt, a hook odrzucał commit niezwiązany z ticketem `IN_PROGRESS`. Reguła
jest napisana, ale nic jej nie sprawdza: `ticket-090` świadomie nie ruszał
`package-manifest.json` ani `governance_check.py`, więc `core.hooksPath` nie był
ustawiony w żadnym klonie, worktree ani adopterze — jedyny tool-agnostyczny
egzekutor był martwy wszędzie, mimo że hook był poprawnie napisany.

Ten ticket dodaje warstwę kontrolną: jedno SSOT (`governance/agent-hosts.json`),
deterministyczny walidator (`scripts/agent_host_check.py`) wpięty w
`governance_check.py`, oraz komplet zarejestrowanych diagnostyk z runbookami.
Walidator sprawdza również punkty styku z paczkami (`pyproject.toml`,
`package.json`), bo `npm install` i `pytest` wykonują się niezależnie od tego,
czy model przeczytał jakikolwiek plik instrukcji.

Zakres jest ograniczony do warstwy walidacji. Dystrybucja plików hostów do
adopterów i job CI to jawnie zależne slice'y — limit `maxImplementationFiles: 9`
z `governance/manifest.hub.json` wymusił podział i został uszanowany.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `python3 scripts/agent_host_check.py --root .` zwraca
  `GOV-AGENT-HOST-PASS` w aktywowanym klonie i kod niezerowy, gdy hook nie jest
  aktywny.
- [x] AC-02: `./tests/agent-hosts.test.sh` pokrywa przypadki negatywne: brak
  pliku hosta, hook bez bitu wykonywalności, nieustawiony `core.hooksPath`,
  brak deklaracji governance w metadanych paczki, rozjazd deklaracji z lockiem
  oraz brak lifecycle bindingu.
- [x] AC-03: `python3 scripts/audit_diagnostics.py --root .` przechodzi, a
  `bash tests/adoption-lock.test.sh` potwierdza, że oba runbooki nowych kodów
  są rozsyłane do adopterów przez `governance/package-manifest.json`.
- [x] AC-04: `./project/governance-check.sh --actor agent` kończy się `GOV-PASS`
  na branchu ticketu.

## Ryzyka i Uwagi

- Risk 1: `GOV-AGENT-HOST-006` jest sprawdzeniem lokalnym; runner CI nigdy nie
  uruchamia hooków. Mitigacja: `--actor ci` pomija ten kod, a test potwierdza,
  że pomija go tylko tam.
- Risk 2: adopterzy nie mają jeszcze `.governance/agent-hosts.json`, więc do
  czasu slice'u dystrybucyjnego walidator zgłosi u nich `GOV-AGENT-HOST-004`.
  Mitigacja: ten slice nie zmienia żadnego repozytorium adoptera ani żadnego
  managed digestu; ich bramy pozostają bez zmian aż do jawnego upgrade'u.
- Risk 3: `GOV-PACKAGING-003` dla Pythona wymaga pluginu pytest, którego
  standard jeszcze nie publikuje. Mitigacja: kod uruchamia się dopiero, gdy
  repozytorium ma marker stacku, a runbook `error/GOV-PACKAGING.md` opisuje
  dokładną zawartość deklaracji.
- Risk 4: `scripts/audit_rule_enforcement.py` widzi tylko kody obecne w
  `governance_check.py` i walidatorach lifecycle, więc `GOV-AGENT-HOST-004..006`
  i `GOV-PACKAGING-001..003` nie są jeszcze związane z regułą normatywną. To ta
  sama klasa ślepej plamki co nieskanowany `.githooks`. Mitigacja: slice 3
  dodaje regułę `C-HOST-*` do `CONTRIBUTING.md`, rozszerza obie powierzchnie
  audytu i mapuje kody; ten ticket nie obchodzi audytu — brakujący managed
  moduł raportuje `GOV-SYNC-001`, co jest jego właściwą semantyką.

## Slice'y zależne

Kolejność merge jest istotna, bo każdy slice zakłada poprzedni:

1. `ticket-106` (ten) — kontrakt i walidator.
2. dystrybucja — `governance/package-manifest.json` rozsyła `CLAUDE.md`,
   `GEMINI.md`, regułę Cursora, `.aider.conf.yml`, instrukcje Copilota i
   `.githooks/pre-commit`; `scripts/install-agent-hosts.sh` aktywuje kontrakt
   w miejscu. Gotowe pliki: `slice2/` w katalogu roboczym sesji.
3. egzekucja CI i domknięcie audytów — job `governance / enforce` w
   `template/files/new-project-governance.workflow.yml`, rozszerzenie
   `scripts/audit_diagnostics.py` o katalog `.githooks` wraz z rejestracją
   `GOV-AGENT-HOST-001..003`, reguła `C-HOST-*` w `CONTRIBUTING.md` i jej
   mapowanie w `governance/rule-enforcement.json`, dokumentacja praktyki
   w `docs/`. Gotowe pliki: `slice3/` w katalogu roboczym sesji.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-106/`.
