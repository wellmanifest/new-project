# Ticket 114: Report fleet drift from the adoption locks

- **ID**: ticket-114
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-23

## Cel i Zakres

Każdy fakt potrzebny do oceny stanu floty już istnieje w workspace: lock
adoptera nazywa przyjętą wersję i rewizję, digesty mówią, czy kopia jest
nienaruszona, a workflow mówią, czy cokolwiek uruchamia bramę. Nic tego nie
zbierało, więc flota rozjechana na pięć minorów wyglądała zdrowo z wnętrza
każdego pojedynczego repozytorium.

Pomiar z 2026-08-22 przed serią ticketów 106–113: dwadzieścia pięć adopterów
na dziesięciu różnych wersjach, od `0.14.0` do `0.18.4`, mediana sześć wydań
w tyle, jeden na bieżącym. Jednocześnie **zero driftu digestów na 806 kopiach**.
To rozróżnienie jest sednem raportu: mechanizm pinowania jest szczelny wobec
manipulacji i bezradny wobec zignorowania, a bez zestawienia obu liczb widać
tylko tę pierwszą.

Klasyfikacja rozdziela trzy stany, nie dwa. `claimed but not pinned` — repozytorium
z `AGENTS.md` bez locka — jest groźniejsze niż bycie poza standardem, bo każde
narzędzie AI czyta tam kontrakt, którego nic nie egzekwuje. Dziś jest w tym
stanie dziesięć repozytoriów.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `bash tests/fleet-report.test.sh` — syntetyczny workspace dowodzi
  liczenia wydań wstecz, wykrycia driftu digestu, stanu `claimed` oraz bramy
  progowej.
- [x] AC-02: `python3 scripts/check_required_checks.py` — nowy krok CI nie
  publikuje nowej nazwy checku, więc deklaracja pozostaje prawdziwa.
- [x] AC-03: `./project/governance-check.sh --actor agent` → `GOV-PASS`.

## Ryzyka i Uwagi

- Risk 1: narzędzie działa na poziomie workspace i wymaga sąsiadujących
  checkoutów, więc hostowany runner go nie uruchomi. To ta sama klasa co
  `workspace_lifecycle_check.py`; test używa syntetycznego workspace, więc CI
  sprawdza logikę bez dostępu do floty.
- Risk 2: kolumna porównania z rejestrem `subactor/validator-agent` zależy od
  ścieżki spoza repozytorium. Jest opcjonalna (`--validator-registry`), a jej
  brak daje `unregistered` zamiast błędu.
- Risk 3: „wydań wstecz" liczy się względem tagów huba, więc adopter na wersji
  bez tagu dostaje `?`, a nie fałszywe zero.

## Publication evidence

- Pull request: `wellmanifest/new-project#190`
- Merge commit: `72ef1ffb6e0d0c14f6682a3f0273dead9d9c9257`
- Trusted approval: `ifuri-validator-agent[bot]` at the exact frozen head.
- Post-merge on `main`: `./project/governance-check.sh --actor agent` → `GOV-PASS`,
  and all twelve `tests/*.test.sh` suites pass.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-114/`.
