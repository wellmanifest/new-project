# Adopcja `new-project` przez `goal`

Integracja z `goal` upraszcza pobranie i uruchomienie generatora, ale nie
osłabia granicy zaufania: standard musi być wskazany pełnym, opublikowanym
40-znakowym SHA commita. Ruchomy branch, tag bez zweryfikowanego SHA albo
lokalny niezatwierdzony worktree nie jest źródłem produkcyjnej adopcji.

## Retrofit istniejącego projektu

Pracuj na osobnym branchu z czystym worktree. Najpierw wykonaj preflight bez
zapisu:

```bash
STANDARD_REVISION=<FULL_PUBLISHED_SHA>
goal governance adopt \
  --source-revision "$STANDARD_REVISION" \
  --target-root . \
  --check
```

Kod wyjścia `0` oznacza zgodność. Kod `1` oznacza, że raportowane operacje
`CREATE`, `UPDATE` lub `CHMOD` są wymagane; `--check` nie zapisuje plików.

Po przeglądzie planu wykonaj pierwszą adopcję:

```bash
goal governance adopt \
  --source-revision "$STANDARD_REVISION" \
  --target-root .
```

`goal` pobiera dokładnie wskazany commit domyślnego repozytorium
`wellmanifest/new-project`, sprawdza, czy checkout ma żądany SHA, a następnie
uruchamia `create_adoption_lock.py`. Generator instaluje zarządzane kontrakty,
docelowy `AGENTS.md`, rootowe wrappery `project.sh` / `project.bat`, skrypty
ticketów i lock z hashami SHA-256.

## Dokończenie bootstrapu lokalnego

Generator nie zgaduje konfiguracji stacka. Przed zmianą implementacji projekt
musi mieć lokalnie poprawne `Dockerfile` i Compose oraz wymagane pliki bazowe z
manifestu. Następnie utwórz pierwszy ticket w repozytorium docelowym:

```bash
./project/new-ticket.sh \
  --title "Adopt new-project governance" \
  --agent codex \
  --workstream governance
```

Uzupełnij ticket, `intent.json` i `TODO.md`, po czym zatrzymaj się w
`WAIT_FOR_APPROVAL`. Dopiero po zatwierdzeniu zakresu przejdź do
`IN_PROGRESS`/`EDIT` i uruchom:

```bash
./project/governance-check.sh --actor agent
```

Nie kopiuj do projektu ticketów ani logów z repozytorium standardu.

## Kontrola driftu i upgrade

Okresowa kontrola jest bezstanowa:

```bash
goal governance adopt \
  --source-revision "$STANDARD_REVISION" \
  --target-root . \
  --check
```

Upgrade do nowego, opublikowanego SHA najpierw sprawdź przez `--check`. Jeżeli
zarządzane pliki różnią się lokalnie, zwykła adopcja odmówi nadpisania. Dopiero
po przeglądzie różnic użyj:

```bash
goal governance adopt \
  --source-revision <NEW_FULL_PUBLISHED_SHA> \
  --target-root . \
  --upgrade
```

Istniejący, zgodny wersją `.governance/manifest.json` pozostaje lokalnym
kontraktem projektu. `--upgrade` dotyczy artefaktów zarządzanych przez standard;
nie jest zgodą na zmianę lokalnego zakresu ticketu ani obejściem review.

## Lokalne lustro standardu

Do testów lub kontrolowanego mirrora można jawnie zmienić źródło:

```bash
goal governance adopt \
  --standard-repository ../new-project \
  --source-revision <FULL_COMMIT_SHA> \
  --target-root . \
  --check
```

Repozytorium przekazane przez `--standard-repository` jest wykonywalnym,
zaufanym źródłem generatora. Nie wskazuj niezweryfikowanego forka.

## Stan 0.9.0

Do czasu opublikowania tagu `v0.9.0`, zielonego CI, zaufanego current-head
review i pełnego SHA powyższy workflow służy do testów integracyjnych. Nie
należy wpisywać bieżącego, niezatwierdzonego worktree jako produkcyjnego locka.
