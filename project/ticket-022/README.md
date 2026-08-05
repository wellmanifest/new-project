# Ticket 022: Canonical change evaluation runtime

- **ID**: ticket-022
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-08-05
- **Klasyfikacja**: `FEATURE / P1 / requested`

## Cel i Zakres
Wprowadzić jeden kanoniczny Change Evaluation Contract zamiast równoległego
DSL-a oceniającego pracę. Kontrakt wiąże raport z dokładnym zakresem Git,
ticketem i intentem, bieżącą polityką, manifest lockiem, dowodami oraz
zatwierdzeniem. Dodać zależnościowo wolny runtime TypeScript uruchamiany przez
`bash scripts/runtime.sh`, który deterministycznie waliduje reguły
`C-EVALUATION-*` z `CONTRIBUTING.md` i artefakt `change-evaluation.json`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Użytkownik zatwierdził wymagania i rozpoczęcie implementacji.
- [x] AC-02: Implementacyjne publikacje wymagają ticketowego PR-a; bezpośredni
  push nie stanowi równoważnego procesu zatwierdzenia.
- [x] AC-03: Raport jest związany z `baseSha`, `headSha`, `mergeBaseSha`,
  `intentHash`, `policyHash`, `manifestLockHash` i `approvalScopeHash`.
- [x] AC-04: Twardych bramek nie można skompensować punktacją; runtime wylicza
  `BLOCKED`, `REVIEW_REQUIRED` albo `ALLOWED` z bramek i wymiarów.
- [x] AC-05: Kryterium `SATISFIED` wymaga dowodu implementacji i walidacji, a
  approval musi dotyczyć dokładnego `headSha` i zaufanego źródła.
- [x] AC-06: Runtime generuje stabilne diagnostyki oraz maszynowy JSON i krótki
  raport Markdown; identyczne wejścia dają identyczny wynik.
- [x] AC-07: Testy obejmują przypadek poprawny, niezgodny hash, wyjście poza
  `allowedPaths`, brak dowodów, stary approval i brak reguły polityki.

## Ryzyka i Uwagi
- Runtime nie interpretuje dowolnego DSL-a ani nie wykonuje treści dokumentu;
  sprawdza obecność wersjonowanych reguł i egzekwuje ich zamknięty kontrakt.
- LLM pozostaje źródłem doradczym; wynik modelu nigdy nie jest trust rootem.
- Pierwszy slice nie wykonuje semantic diff ani oceny kierunku przez LLM.
  Przyjmuje jawne, dowodowe pola producenta raportu (np. `todo2code`) i
  determistycznie waliduje wiązania, bramki, zakres oraz spójność werdyktu.

## Autoryzacja sesji

Użytkownik 2026-08-05 polecił kontynuować i dostarczył szczegółowy kontrakt,
reguły DSL oraz kolejność wdrożenia. Jest to zgoda interaktywna na ten zakres,
ale nie zaufany dowód merge.

## Dowody walidacji

- `bash tests/governance-scripts.test.sh` — PASS, w tym pozytywna ocena,
  deterministyczne powtórzenie i siedem przypadków blokujących.
- `bash tests/governance-validator.test.sh` — PASS.
- `bash tests/governance-env.test.sh` — PASS.
- `bash tests/adoption-lock.test.sh` — PASS; runtime i schema są zarządzanymi
  artefaktami pakietu.
- `bash tests/branch-lifecycle.test.sh` — PASS.
- `python3 -m json.tool governance/change-evaluation.schema.json` — PASS.
- `bash -n scripts/runtime.sh` oraz `git diff --check` — PASS.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-022/`.
