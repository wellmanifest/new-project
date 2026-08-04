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

## Procedura

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

Pełny SHA, URL Release oraz wynik czystego testu zostaną wpisane po publikacji.
