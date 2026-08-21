# Ticket 100: Treat generated artifact receipts as governance carriers

- **ID**: ticket-100
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-21

## Cel i Zakres

Usunąć sprzeczność, w której target musi przebudować deterministyczny
`config/artifact-registry.json` po zmianie zarządzanego dokumentu, ale ten sam
plik jest liczony jako implementacja obcego workstreamu. Ustanowić ten dokładny
plik jako generowany governance carrier oraz dopuścić go w terminalnym
closure, nadal odrzucając dowolne inne źródła, usunięcia, kopie i rename.

Zmiana nie dodaje ogólnego wildcardu i nie zwalnia artefaktu z jego własnego
deterministycznego `artifacts:check`.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Default i hub manifest klasyfikują wyłącznie
  `config/artifact-registry.json` jako governance carrier.
- [x] AC-02: Ticket dowolnego workstreamu może dołączyć wygenerowany receipt
  bez fałszywego `GOV-WORKSTREAM-003` i bez przejęcia dowolnego `config/**`.
- [x] AC-03: DONE closure może zmienić dokładny receipt razem z własnym README
  i indeksami, ale nadal odrzuca inny plik `config/`, źródło i usunięcie.
- [x] AC-04: Pełne testy governance validatora, agent-hostów i adoption lock
  przechodzą wraz z exact-base governance gate.

## Dowody walidacji

- `tests/governance-validator.test.sh`: PASS; exact receipt przechodzi jako
  governance carrier, sąsiedni `config/other-generated.json` pozostaje
  `GOV-SCOPE-001`.
- `tests/agent-hosts.test.sh`: PASS; DONE closure przyjmuje exact receipt i
  odrzuca inny `config/` kodem `GOV-AGENT-HOST-003`.
- `tests/adoption-lock.test.sh`: PASS; pakiet adopcyjny pozostaje spójny.

## Ryzyka i Uwagi

- Receipt może być duży, ale jego zawartość nadal kontroluje targetowy,
  deterministyczny builder/checker; ta zmiana reguluje wyłącznie własność diffu.
- Nie rozszerzamy closure na całe `governancePaths`, ponieważ manifest targetu
  może zawierać szersze ścieżki, których terminalny ticket nie powinien pisać.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-100/`.
