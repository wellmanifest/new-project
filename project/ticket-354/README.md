# Ticket 354: Zarządzany hook pre-push blokuje bezpośredni push do gałęzi docelowej (GOV-PUSH-001)

- **ID**: ticket-354
- **Owner**: agent:claude
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-19

## Cel i Zakres

19.10.2026 agent wypchnął bezpośrednio na `main` w paxlet-com/willmux 13 commitów
(ticket-318..330) bez PR. CI (`new-project-governance`) uruchamia się tylko dla PR,
więc na `main` nie przeszła żadna kontrola; czysty klon pokazał 4 błędy i 32 wyjątki
testów zamiast 1. Repozytoria prywatne na planie darmowym nie mają ochrony gałęzi.

Nowy zarządzany hook `.githooks/pre-push` odrzuca push aktualizujący zadeklarowaną
gałąź docelową (`delivery.targetBranches`, domyślnie `main`), także refspec
`HEAD:main` i usunięcie gałęzi, z kodem `GOV-PUSH-001`. Profile `main-only-planfile`,
`main-only-files` i `local-audit` są zwolnione, jak w hookach commitów. Hook jest
zadeklarowany w `agent-hosts.json` (`additionalHooks`) i w `package-manifest.json`,
więc po aktualizacji standardu `agent_host_check` wymaga go w adoptujących
repozytoriach. Validator scala przez API GitHub i nie jest objęty hookiem. Wersja
standardu 0.20.106.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `tests/pre_push_hook_test.py` (prawdziwy push do repozytorium bare):
  push `main` i `HEAD:main` odrzucony z `GOV-PUSH-001`; gałąź ticketu przechodzi;
  zadeklarowana gałąź `master` jest chroniona; profile main-only/local-audit przechodzą.
- [x] AC-02: kontrakt hosta (`agent-hosts.json`, schemat, `agent_host_check.py` i jego
  kopia w pakiecie wellman) akceptuje `.githooks/pre-push`; kopia pakietu pozostaje identyczna.

## Ryzyka i Uwagi
- Człowiek może świadomie ominąć hook (`git push --no-verify`); agenci nie omijają hooków.
- Repozytoria dostaną hook dopiero po `goal governance adopt --upgrade` na nowym wydaniu.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-354/`.
