# Ticket 058: Preserve colliding target root wrappers

- **ID**: ticket-058
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-11

## Cel i Zakres

Usunąć znany blocker adopcji z ticketu 024, ponownie ujawniony przez
`semcod/hillm`. Pakiet traktuje obecnie rootowe `project.sh` i `project.bat`
jako zarządzane, dlatego preflight chce zastąpić 139-liniową automatyzację
`hillm` 38-liniowym wrapperem standardu. Bez `--upgrade` adopcja jest
zablokowana, a z `--upgrade` utraciłaby zachowanie targetu.

Opcjonalne root wrappery mają używać strategii `seed`: standard tworzy je tylko
gdy nie istnieją. Jedynym bezwarunkowym, zarządzanym gate pozostaje
`project/governance-check.sh` lub `.bat`, a instrukcje targetu muszą kierować
właśnie tam.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Polecenie użytkownika stanowi bounded
  `SESSION_EXECUTION_AUTHORIZATION` dla lokalnej implementacji i testów.
- [ ] AC-02: Pre-existing `project.sh` i `project.bat` nie są raportowane jako
  drift, nie wymagają `--upgrade`, zachowują bajty i nie trafiają do locka.
- [ ] AC-03: Pusty target nadal otrzymuje root wrappery z poprawnym trybem, a
  późniejsza lokalna zmiana seeda nie powoduje driftu pakietu.
- [ ] AC-04: `project/governance-check.sh` i `.bat` pozostają zarządzane, a
  instrukcje agentów wskazują je jako kanoniczną bramę.
- [ ] AC-05: Focused i pełny Linux contract oraz powtórzony pilot `hillm`
  przechodzą bez utraty jego `project.sh` i bez regresji testów produktu.

## Ryzyka i Uwagi
- Seed nie jest hash-bound; dlatego nie może być kanoniczną bramą. Hash-bound
  pozostają osobne `project/governance-check.*`.
- Istniejące immutable wydania i locki targetów nie są migrowane w tym
  lokalnym ticketcie.
- Nie implementujemy heurystycznego łączenia ani wstrzykiwania kodu do
  dowolnego skryptu targetu.
- Nie wykonujemy push, PR, merge, tagowania ani publikacji.

## Autoryzacja

Bieżące polecenie użytkownika zleca lokalne poprawianie standardu na podstawie
kolejnych pilotów. Operacje zewnętrzne wymagają osobnej dyspozycji.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-058/`.
