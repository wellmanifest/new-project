# Ticket 065: Verify immutable publication evidence before adoption

- **ID**: ticket-065
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-12

## Cel i Zakres

Usunąć fałszywe poświadczenie publikacji z bezpośredniego generatora adopcji.
Produkcja ma korzystać z pakietu Goal i przyjąć wyłącznie pełny SHA związany z
annotowanym tagiem oraz finalnym GitHub Release. Jawny tryb testowy może ominąć
zewnętrzny dowód, lecz musi zapisać prawdziwe `unpublished-test`, którego
zwykły governance gate nie uzna za opublikowany standard.

Po walidacji opublikować kompletny standard jako immutable minor `v0.15.0`,
obejmujący także zmiany scalone od v0.14.1, i wykonać read-only pilot przez
publiczny pakiet Goal 2.1.295 na żywym glon przed szerszą adopcją.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: Bezpośrednia produkcyjna adopcja nieopublikowanego commita kończy
  się przed pierwszym zapisem i nie może utworzyć locka z `published`.
- [ ] AC-02: Generator weryfikuje pełny SHA przez dokładny annotowany tag oraz
  finalne metadane GitHub Release; draft, prerelease, zły tag i brak daty
  publikacji są odrzucane.
- [ ] AC-03: `--allow-unpublished-for-testing` jest jawnym wyjątkiem tylko dla
  fixture'ów, zapisuje `unpublished-test`, a produkcyjny validator nadal
  odrzuca taki lock.
- [ ] AC-04: Dokumentacja kieruje produkcyjną adopcję przez opublikowany pakiet
  Goal; `VERSION`, manifest, changelog i aktywne asercje zgadzają się na 0.15.0.
- [ ] AC-05: Focused i pełny Linux contract, Ruff, Windows CI oraz exact-head
  Validator App przechodzą przed trusted merge.
- [ ] AC-06: Czysty merge przechodzi ponowną walidację, annotowany `v0.15.0`
  i finalny GitHub Release wskazują ten merge, a pilot glon przez publiczny Goal
  potwierdza opublikowany standard bez zapisu.
- [ ] AC-07: Po terminalnym delivery zdalny/lokalny branch, worktree i wszystkie
  własne artefakty testowe zostają usunięte po dowodzie osiągalności.

## Ryzyka i Uwagi

- Sprawdzenie publikacji w generatorze jest obroną w głąb; zalecanym publicznym
  interfejsem pozostaje `goal governance adopt` z Goal 2.1.295 lub nowszym.
- Fixture'y nie mogą wykonywać sieci ani udawać opublikowanego pochodzenia.
- Tag i Release są nieodwracalne operacyjnie, więc powstaną dopiero po
  zewnętrznej aprobacie, merge i ponownym teście czystego merge SHA.
- Polecenie użytkownika tworzy bounded `SESSION_EXECUTION_AUTHORIZATION` dla
  tego zakresu, ale nie stanowi trusted merge approval.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-065/`.
