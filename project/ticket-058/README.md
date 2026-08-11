# Ticket 058: Preserve colliding target root wrappers

- **ID**: ticket-058
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
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
- [x] AC-02: Pre-existing `project.sh` i `project.bat` nie są raportowane jako
  drift, nie wymagają `--upgrade`, zachowują bajty i nie trafiają do locka.
- [x] AC-03: Pusty target nadal otrzymuje root wrappery z poprawnym trybem, a
  późniejsza lokalna zmiana seeda nie powoduje driftu pakietu.
- [x] AC-04: `project/governance-check.sh` i `.bat` pozostają zarządzane, a
  instrukcje agentów wskazują je jako kanoniczną bramę.
- [x] AC-05: Focused i pełny Linux contract oraz powtórzony pilot `hillm`
  przechodzą bez utraty jego `project.sh` i bez regresji testów produktu.

## Ryzyka i Uwagi
- Seed nie jest hash-bound; dlatego nie może być kanoniczną bramą. Hash-bound
  pozostają osobne `project/governance-check.*`.
- Istniejące immutable wydania i locki targetów nie są migrowane w tym
  lokalnym ticketcie.
- Nie implementujemy heurystycznego łączenia ani wstrzykiwania kodu do
  dowolnego skryptu targetu.
- Nie wykonujemy push, PR, merge, tagowania ani publikacji.

## Dowody walidacji

- Focused adoption fixture zachowuje custom `project.sh`/`.bat` wraz z trybem,
  nie raportuje `UPDATE`/`CHMOD`, instaluje pakiet bez `--upgrade` i wyklucza
  seedy z `managedFiles`.
- Pusty fixture nadal otrzymuje oba root seedy; ich późniejsze lokalne
  rozszerzenie nie generuje driftu, a canonical gates pozostają hash-bound.
- Wszystkie polecenia Linux CI, kompletność suite, kontrakty JSON oraz Ruff dla
  zmienionej powierzchni przechodzą na implementacji `98c403c`.
- Fresh `hillm` preflight exact-SHA zmienił poprzednie `UPDATE project.sh` w
  25 `CREATE`, nie zgłosił braków i nie zapisał plików.
- Adopcja `hillm` bez `--upgrade` zachowała hash `cd1791c0...c803f9` i tryb
  `775`; root seedy są poza lockiem, canonical gates w locku, a manifest
  deklaruje Python bez Dockera.
- Payload `6cc1429` po korekcie opisu `004871c` uzyskał trzy `GOV-PASS`.
  Frozen uv zachował `81 passed / 7 skipped`, Ruff pozostał na 77 istniejących
  findingach, a Goal dry-run nie zapisał zmian.
- Testy `hillm` ujawniły niezależny istniejący defekt: dopisują losowe wiersze
  do śledzonego event ledgeru. Dokładne wiersze testowe usunięto; oba repo są
  czyste i produktowej naprawy nie mieszano z tym ticketem standardu.

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
