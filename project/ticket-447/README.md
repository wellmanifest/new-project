# Ticket 447: Support wellmanifest/new-project scaffold ID across migration, work-start, and seed checks (0.20.154)

- **ID**: ticket-447
- **Owner**: agent:antigravity (SESSION_EXECUTION_AUTHORIZATION)
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-15

## Cel i Zakres

SESSION_EXECUTION_AUTHORIZATION: użytkownik zlecił kontynuację adopcji, testów i chronionego scalania (`kontynuuj,scalaj,testuj`).

1. **Obsługa identyfikatora `wellmanifest/new-project` w minimalnych scaffoldach Wellmana (`wellman adopt wellmanifest/new-project`)**:
   CLI `wellman adopt wellmanifest/new-project` zapisuje `.governance/manifest.json` ze schematem `wellmanifest.manifest/v1` i polem `standard: {"id": "wellmanifest/new-project", "version": "<semver>"}` (np. w `heyasa/guardian`). Rozszerzenie zamkniętego zbioru `WELLMAN_SCAFFOLD_PROFILES` o `"wellmanifest/new-project"` w `scripts/create_adoption_lock.py`, `scripts/work_start_check.py` oraz `scripts/governance_check.py` (wraz z ujednoliceniem wzorca SemVer z opcjonalnym sufiksem pre-release/build).
2. **Ujednolicenie `initial_adoption_seed_paths` w `scripts/governance_check.py` i `_bundled/governance_check.py`**:
   Zastąpienie zawężonego warunku `standard.get("id") != "profile:baseline"` w `initial_adoption_seed_paths` zamkniętym zbiorem `WELLMAN_SCAFFOLD_PROFILES`, aby pierwszy ticket migracji scaffoldu (dla dowolnego kanonicznego profilu Wellmana oraz `wellmanifest/new-project`) poprawnie autoryzował pliki seed utworzone przez `--bootstrap-prerequisites-plan` (`VERSION`, `CHANGELOG.md`, `TODO.md`, `project/TICKETS.md`).
3. **Wydanie standardu `0.20.154`**:
   Synchronizacja `packages/wellman/src/wellman/_bundled/governance_check.py` przez `packages/wellman/sync_bundled.py` oraz aktualizacja wersji `0.20.154` w `VERSION`, `CHANGELOG.md`, `governance/manifest.default.json`, `governance/manifest.hub.json` i `packages/wellman/pyproject.toml`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `validate_wellman_scaffold` (`scripts/create_adoption_lock.py`), `bootstrap_scaffold_at_head` (`scripts/work_start_check.py`) oraz `initial_adoption_seed_paths` (`scripts/governance_check.py`) akceptują minimalny scaffold `wellmanifest.manifest/v1` z `standard.id` należącym do zamkniętego zbioru `WELLMAN_SCAFFOLD_PROFILES` (w tym `"wellmanifest/new-project"`), odrzucając jednocześnie manifesty natywne (`new-project.governance/v2`), dodatkowe pola (np. `sourceRevision`, `coordination`) oraz nieznane identyfikatory.
- [x] AC-02: Testy regresyjne w `tests/adoption_legacy_scaffold_test.py` oraz `tests/scaffold_bootstrap_test.py` potwierdzają migrację i autoryzację plików seed dla `"wellmanifest/new-project"` i profili `profile:*` oraz odmowę dla manifestów niestandardowych/natywnych.
- [x] AC-03: Parytet bundla (`packages/wellman/sync_bundled.py --check`), parytet wersji `0.20.154` (`tests/version-parity.test.sh`), budowa paczki (`tests/wellman-package.test.sh`) oraz bramka `project/governance-check.sh` przechodzą bez błędów.

## Ryzyka i Uwagi
- Risk 1: Omyłkowe dopuszczenie natywnego manifestu `wellmanifest/new-project` jako scaffoldu — zmitygowane ścisłym wymogiem `schema == "wellmanifest.manifest/v1"`, `set(document) == {"schema", "standard"}`, `set(standard) == {"id", "version"}` oraz brakiem natywnych artefaktów (`manifest.base.json`, `package-manifest.json`, natywnego `manifest.lock.json`).

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-447/`.
