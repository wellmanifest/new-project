# Ticket 070: Format managed governance workflow for target repositories

- **ID**: ticket-070
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-12

## Cel i Zakres

Naprawić zarządzany workflow instalowany w repozytoriach docelowych. Szablon
0.16.0 zapisuje cron w pojedynczym cudzysłowie, podczas gdy Prettier 3 używany
przez żywy target wymaga cudzysłowu podwójnego. Ponieważ plik jest zarządzany i
chroniony hashem locka, target nie może poprawić go lokalnie bez wywołania
driftu. Poprawka musi zostać wydana jako immutable 0.16.1 i zaadoptowana przez
Goal.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Zarządzany workflow jest kanonicznym wyjściem Prettier 3 dla
      ustawienia cron, bez zmiany semantyki harmonogramu.
- [x] AC-02: Test kontraktowy blokuje ponowne wprowadzenie niekanonicznego
      zapisu i adopcja nadal wiąże dokładny hash zarządzanego pliku.
- [x] AC-03: Wersje source hub, manifestu targetu i testów są spójne jako
      0.16.1; pełny Linux i hosted Windows contract przechodzą.
- [x] AC-04: Exact-head Validator App zatwierdza PR przed merge, a czysty merge
      SHA przechodzi post-merge CI.
- [x] AC-05: Annotowany tag i finalny GitHub Release `v0.16.1` peelują dokładnie
      do czystego, ponownie przetestowanego `origin/main`.
- [x] AC-06: Żywy target aktualizuje lock przez `goal governance adopt
      --upgrade`, zachowuje własne rootowe skrypty i przechodzi format,
      governance oraz pełny pipeline.

## Ryzyka i Uwagi

- Ręczna poprawka w targetcie złamałaby managed hash; jedyną produkcyjną drogą
  jest nowy opublikowany SHA i Goal `--upgrade`.
- Zmiana jest semantycznie neutralna dla YAML, ale wymaga nowej wersji, ponieważ
  każdy byte zarządzanego artefaktu jest częścią locka.
- Publikacja pozostaje oddzielona od PR: najpierw trusted merge i post-merge
  testy, potem immutable tag/release z czystego `main`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-070/`.

## Zintegrowana publikacja

- PR #102 miał head `f0398d24fd7e8305e9f5610fda93ef5c469fb03e`;
  wymagane `test` i `windows-governance` zakończyły się sukcesem.
- `ifuri-validator-agent[bot]` zatwierdził dokładnie ten head przed merge'em.
- Payload został scalony jako `4e6ba5ec15873346446d67d8787f17f68f57f81e`;
  post-merge run `31601309628` zakończył się sukcesem.
- Annotowany tag `v0.16.1` peeluje do `4e6ba5e...`, a finalny GitHub Release
  został opublikowany 2026-08-12 bez draft/prerelease.
- Żywy `subactor/intent-contract-dsl-runtime` ma czysty `main` i lock
  `publicationStatus: published`, `version: 0.16.1`, `sourceRevision: 4e6ba5e...`;
  jego adopcja i governance-only closure są zintegrowane w PR #12 i #13.
