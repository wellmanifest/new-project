# Ticket 108: Run the governance gate in adopter CI

- **ID**: ticket-108
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-23

## Cel i Zakres

Każdy z 25 adopterów nosi `.governance/governance_check.py`, a jedyny
zarządzany workflow, który dostaje, uruchamia wyłącznie
`branch_lifecycle_check.py`. Walidator jest zainstalowany i nieuruchamiany.

Pomiar wykonany przed zmianą: `.governance/governance_check.py --actor ci`
przechodzi w **24 z 25** adopterów. Jedyna porażka to `performance`, gdzie
`ticket-001` wisi w `IN_PROGRESS / PUBLICATION` z `acceptedBaseSha` `8693521`
przy `main` na `b9dfa47` — `GOV-BASE-001`, znalezisko prawdziwe. Dołożenie
joba włącza więc realną bramę w 24 repozytoriach i ujawnia jeden faktycznie
zawieszony ticket, zamiast zalać flotę czerwienią.

Drugą częścią jest domknięcie dwóch ślepych plamek audytu. Obie miały tę samą
przyczynę: listę plików utrzymywaną ręcznie zamiast wyprowadzanej ze źródła.
`audit_diagnostics.py` nie skanował `.githooks`, więc `GOV-AGENT-HOST-001..003`
emitowane przez hooka nigdy nie musiały trafić do katalogu. `audit_rule_enforcement.py`
nie znał `scripts/agent_host_check.py`, więc istniał deterministyczny walidator,
którego kodów żadna reguła normatywna nie musiała objąć. Reguły `C-HOST-001..003`
domykają mapowanie.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `python3 scripts/audit_diagnostics.py --root .` → 77 kodów, zero
  findings; `python3 scripts/audit_rule_enforcement.py --root .` → 178 reguł,
  0 unmapped, 0 unclaimed.
- [x] AC-02: `bash tests/adoption-lock.test.sh` — zmieniony szablon workflow
  nadal adoptuje się i zapisuje digest.
- [x] AC-03: `./project/governance-check.sh --actor agent` → `GOV-PASS`.

## Ryzyka i Uwagi

- Risk 1: job `governance / enforce` nie jest wymaganym checkiem u adopterów,
  dopóki ich ruleset go nie wymieni. Świadomie: ten ticket włącza sygnał, nie
  blokadę merge'a. Wymaganie go w rulesetach jest osobną decyzją, bo ruleset
  żyje poza repozytorium.
- Risk 2: `performance` zaświeci na czerwono przy pierwszym PR po adopcji. To
  jest cel, nie efekt uboczny — ticket-001 jest tam realnie zawieszony.
- Risk 3: krok sprawdzający nazwy required-checks został z joba usunięty.
  Sprawdziłem: bieżący `check_required_checks.py` na danych adoptera kończy się
  `workflow file not found: .github/workflows/ci.yml`, bo 25/25 adopterów nosi
  deklarację huba. Failowałby w 20 repozytoriach z powodu wady, którą naprawia
  osobny slice generujący deklarację per repozytorium.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-108/`.
