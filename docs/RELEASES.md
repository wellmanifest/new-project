# Publikacja i rollback standardu

Ten dokument opisuje publikację immutable wydania `wellmanifest/new-project`.
Branch `main`, skrócony SHA ani lokalny worktree nie są produkcyjnym
`sourceRevision`.

## Warunki publikacji

Wydanie można opublikować wyłącznie, gdy:

- drzewo zawiera oczekiwany numer w `VERSION`;
- przygotowujący PR ma zielone wymagane CI i niezależne approval dla exact HEAD;
- merge commit z `main` został ponownie przetestowany z czystego checkoutu;
- tag o wybranej nazwie jeszcze nie istnieje lokalnie ani na GitHub;
- release notes nie zawierają sekretów ani ścieżek konkretnej maszyny.

## Zarządzana publikacja przez Goal

Nowe repozytorium, które włącza zarządzaną publikację, deklaruje ją jawnie w
`goal.yaml`:

```yaml
governance:
  delivery:
    require_goal_a: true
    default_mode: pull-request
    allowed_modes: [pull-request, publish-only, direct-main]
    remote: origin
    base_branch: main
    require_clean_governance: true
```

Przed pierwszym skutkiem ubocznym należy sprawdzić rzeczywistą zdolność
wybranego pliku wykonywalnego Goal. Sam numer wersji nie wystarcza:

```bash
goal --help | grep -F -- '--delivery-mode'
goal governance verify-delivery --delivery-mode pull-request
```

Publikacja implementacji kończy się na branchu i PR. Nie publikuje pakietu,
taga ani Release:

```bash
goal --delivery-mode pull-request --no-publish -a push --ticket ticket-NNN
```

Opcja `--ticket` należy do podkomendy `goal push`, dlatego występuje po słowie
`push`; rootowa opcja `-a` nadal włącza pełny workflow. Zmianę wiążą z jednym
ticketem również governance intent, nazwa brancha i PR wskazujący current HEAD.

Po trusted merge, ponownym teście czystego merge SHA i sprawdzeniu, że docelowa
wersja lub tag jeszcze nie istnieją, osobny ticket wydania wybiera dokładnie
jeden skutek:

```bash
# Tylko skonfigurowany registry, bez Git push/tag/PR:
goal -a --delivery-mode publish-only --force-publish

# Skonfigurowany immutable Git/tag/GitHub Release z czystego origin/main:
goal -a --delivery-mode direct-main --force-publish
```

`--force-publish` oznacza wyłącznie, że zatwierdzone źródło jest już
commitowane. Nie omija testów, governance, kontroli istniejącego taga,
exact-head approval ani ochrony gałęzi. Lokalny pre-push hook oraz
`.governance/delivery-events.jsonl` są dowodem pomocniczym, nie trust rootem.
Po wykonaniu należy zweryfikować stan PR, registry, taga i GitHub Release przez
ich zdalne API.

Brak `goal.yaml`, brak `--delivery-mode`, niedozwolony tryb albo niezielona
bramka zatrzymują publikację. Nie wolno wtedy przechodzić na surowe `git push`,
`twine`, `npm publish`, `cargo publish` lub `gh release create` jako obejście.

## Historyczna procedura ręczna wydania 0.10.0

Poniższy zapis zachowuje odtwarzalny dowód sposobu publikacji `v0.10.0`.
Nie jest procedurą dla nowych wydań po adopcji zarządzanego Goal.

Po scaleniu PR przygotowującego release zapisz pełny SHA:

```bash
git fetch origin main --tags
RELEASE_SHA="$(git rev-parse origin/main^{commit})"
test "$(git show "${RELEASE_SHA}:VERSION")" = "0.10.0"
```

Utwórz odłączony, czysty checkout tego commita i uruchom:

```bash
bash tests/governance-scripts.test.sh
bash tests/governance-validator.test.sh
bash tests/adoption-lock.test.sh
git status --short
```

Każdy test musi przejść, a status pozostać czysty. Następnie utwórz annotowany
tag bez przesuwania jakiejkolwiek istniejącej referencji:

```bash
git tag -a v0.10.0 "${RELEASE_SHA}" -m "Release 0.10.0"
git push origin refs/tags/v0.10.0
gh release create v0.10.0 --repo wellmanifest/new-project --verify-tag
```

Release notes muszą zawierać pełny SHA. Po publikacji porównaj commit taga z
targetem Release i z SHA zapisanym w notes.

## Adopcja

Repozytorium docelowe przypina pełny commit, nie samą nazwę tagu:

```bash
goal governance adopt \
  --source-revision <FULL_RELEASE_SHA> \
  --target-root . \
  --check
```

Dopiero po przeglądzie planu wykonuje adopcję lub jawny `--upgrade`.

## Rollback

Tagu wydania nie przesuwa się ani nie usuwa w zwykłym rollbacku. Repozytorium
docelowe wraca do pełnego SHA poprzedniego zaufanego wydania:

1. zachowuje aktualny lock i diff jako dowód;
2. uruchamia `goal governance adopt --check` dla poprzedniego SHA;
3. przegląda plan przywrócenia zarządzanych artefaktów;
4. wykonuje jawny `--upgrade` do poprzedniego SHA;
5. uruchamia governance gate i testy projektu docelowego;
6. publikuje rollback przez jego własny ticket i PR.

Jeśli problem dotyczy kompromitacji authority lub rewizji, najpierw zablokuj
nowe adopcje i cofnij zaufanie na platformie. Nie ukrywaj incydentu przez
przesunięcie istniejącego tagu.

## Dowód wydania 0.10.0

- Tag: `v0.10.0`.
- Pełny SHA: `62ffb0dac1dba9294aa825ca5cc0344fefb33b0d`.
- Release: https://github.com/wellmanifest/new-project/releases/tag/v0.10.0
- GitHub publication time: `2026-08-04T19:33:48Z`.
- Tag type: annotated; peeled commit jest równy pełnemu SHA powyżej.
- Czysty detached checkout: governance scripts, deterministic validator i
  adoption lock — PASS; status drzewa pusty przed i po testach.
