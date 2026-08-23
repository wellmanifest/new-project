# Ticket 112: Derive required-checks from the repository workflows

- **ID**: ticket-112
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-23

## Cel i Zakres

`ticket-009` w `wellmanifest/twin-lifecycle` był pierwszą adopcją 0.18.5 i
zatrzymał się na `GOV-SYNC-001`: `.governance/required-checks.json` deklarował
`test` i `windows-governance` z `.github/workflows/ci.yml`, workflow, którego to
repozytorium nie ma. Deklaracja była dosłowną kopią huba. Wszystkie 25 adopterów
nosi tę samą kopię, więc każda kolejna adopcja zatrzyma się tak samo.

Plik jest `extendable`, więc adopcja go nie nadpisuje i hub nie może go naprawić
centralnie. Naprawić może go tylko repozytorium — z jedynego pierwotnego
źródła, czyli nazw jobów publikowanych przez własne workflow pull-requestowe.

Narzędzie domyślnie raportuje. `--write` zapisuje wyłącznie wtedy, gdy każdą
nazwę da się wyprowadzić. Job wołający reusable workflow publikuje kontekst
`<caller> / <callee job>`, a callee mieszka w innym repozytorium — takie joby są
zgłaszane do potwierdzenia, nie zgadywane. Dotyczy to `deployment`, `dsl`,
`lifecycle` i `poa`, więc automatyczny zapis wstawiłby tam nazwę fałszywą.

Weryfikacja krzyżowa z niezależnym źródłem: `subactor/validator-agent`
utrzymuje własny rejestr nazw checków. Wyprowadzenie zgadza się z nim w **21 z
24** zarejestrowanych repozytoriów. Trzy rozjazdy są brakami rejestru
(`llm` i `merge` publikują więcej checków, niż rejestr zna) oraz jednym
przypadkiem nazwy prefiksowanej przez caller (`logs`).

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `bash tests/required-checks.test.sh` — klucze `on:` nie są mylone
  z jobami, callery są raportowane zamiast zgadywane, `--write` odmawia
  repozytorium z callerem, a wykluczenie cykliczne pozostaje wykluczone.
- [x] AC-02: `python3 scripts/generate_required_checks.py .` — hub zgadza się z
  własną deklaracją, łącznie z `circularGovernanceChecksIgnoredByValidator`.
- [x] AC-03: `bash tests/adoption-lock.test.sh` — nowe źródło pakietowe
  adoptuje się i zapisuje digest.
- [x] AC-04: `./project/governance-check.sh --actor agent` → `GOV-PASS`.

## Ryzyka i Uwagi

- Risk 1: narzędzie czyta nazwy jobów regexem, tak samo jak
  `check_required_checks.py`, żeby nie wprowadzać zależności od YAML w
  pakiecie adoptera. Test pokrywa przypadek, w którym klucze `on:` mają to samo
  wcięcie co joby.
- Risk 2: `--write` nadpisuje plik należący do repozytorium docelowego.
  Domyślnie narzędzie tylko raportuje, a odmawia zapisu tam, gdzie wynik byłby
  niepełny.
- Risk 3: uruchomienie na całej flocie pokazuje `1 of 25 agree`. Tym jednym jest
  `twin-lifecycle`, poprawiony ręcznie podczas pilota — niezależne potwierdzenie,
  że ręczna deklaracja była prawidłowa.

## Publication evidence

- Pull request: `wellmanifest/new-project#186`
- Frozen and approved head: `f0922b0449a5cf8bc8af9dcf83d1f77cf710f36e`
- Merge commit: `6c7caa25dfcc446e2d2ea892aa081df0e228ceb8`
- Trusted approval: `ifuri-validator-agent[bot]`.
- Post-merge on `main`: `./project/governance-check.sh --actor agent` → `GOV-PASS`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-112/`.
