# Ticket 044: Publish extendable target manifest contract

- **ID**: ticket-044
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: WAIT_FOR_APPROVAL
- **Utworzono**: 2026-08-08

## Cel i Zakres

Opublikować scalony kontrakt `extendable` z ticketu 024 jako nowe, immutable
wydanie `v0.14.0`. Jest to minor release, ponieważ
`new-project.package-manifest/v1` otrzymał nową publiczną strategię, adopcja
materializuje nowy zarządzany artefakt `.governance/manifest.base.json`, a
semantyka locka rozdziela pliki `managed` od targetowego manifestu.

Wydanie musi związać `VERSION`, domyślny manifest, changelog oraz aktywne
asercje wersji, przejść pełny Linux i Windows contract na dokładnym HEAD,
zostać niezależnie zatwierdzone, a następnie otrzymać nowy annotowany tag i
opublikowany GitHub Release wskazujące dokładny, ponownie przetestowany merge
commit. Ticket nie migruje todo2code; jego pełny release SHA stanie się wejściem
dla osobnego downstream ticketu 062.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: `VERSION`, `manifest.default.json`, bieżące asercje testowe i
  `CHANGELOG.md` jednoznacznie wskazują `0.14.0`; historyczne fixture’y
  wcześniejszych wydań pozostają przypięte.
- [ ] AC-02: Pełny kontrakt Linux, chroniony `windows-governance` i niezależny
  exact-head Validator przechodzą przed merge.
- [ ] AC-03: Pełny kontrakt Linux przechodzi ponownie w czystym detached
  checkout merge/release SHA.
- [ ] AC-04: Nowy annotowany tag `v0.14.0` i opublikowany, nie-draftowy,
  nie-prerelease GitHub Release wskazują dokładnie zwalidowany merge SHA.
- [ ] AC-05: Nie istnieje force-update ani przesunięcie wcześniejszego taga;
  downstream otrzymuje pełny SHA, nie branch lub ruchomą nazwę.

## Ryzyka i Uwagi

- Tag i release są nieodwracalne operacyjnie: przed publikacją muszą przejść
  chronione checki, exact-head review i czysty checkout merge SHA.
- `0.14.0` jest wymagane przez zmianę publicznego kontraktu adopcji; patch
  `0.13.3` zaniżyłby kompatybilnościowy zakres zmiany.
- Nigdy nie przesuwać, nie nadpisywać ani nie usuwać opublikowanego taga.
- Brak zmian implementacji `extendable`, authority, approval, AQL, sekretów,
  zależności, Dockera i mechanizmu runtime evolution.
- Brak migracji repozytoriów downstream w tym ticketcie.

## Bramka zatwierdzenia

Ticket jest `PLAN / WAIT_FOR_APPROVAL`. Zgoda na implementację ticketu 024 nie
jest automatycznie zgodą na podniesienie wersji, utworzenie taga lub GitHub
Release. Przed zmianą pięciu plików wydania wymagana jest osobna, jawna zgoda
na ten plan.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-044/`.
