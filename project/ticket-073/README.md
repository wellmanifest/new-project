# Ticket 073: Make remediation intent projections atomic and analyzable

- **ID**: ticket-073
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-12

## Cel i zakres

Naprawić regresję ujawnioną przez rzeczywisty przepływ
`new-project -> goal -> todo2code`: projekcje z zaakceptowanego
`remediation-intent.dsl.json` mają zawierać dokładnie jeden kompletny,
atomowy rekord działania na akcję. Metadane, constraints i non-goals nie mogą
być interpretowane jako samodzielne wymagania.

Analizator ma najpierw powiązać rekordy grafu todo2code z deklarowanymi
`taskPath` i `todoPath`, a dopiero potem oceniać plany i diagnostyki. Historyczne
plany innych ticketów nie mogą rozszerzać ani blokować bieżącej intencji, ale
rzeczywista niejednoznaczność, konflikt, utrata kryterium, obniżenie priorytetu,
wyjście poza scope lub nieautoryzowane usunięcie nadal muszą być raportowane.

Kontrakt przechowywania pozostaje trójwarstwowy: stabilny kod i krótka naprawa
w `governance/diagnostics.json`, wieloetapowy lub ryzykowny runbook w
`error/*.md`, a konkretna intencja incydentu wyłącznie w ticketcie repozytorium
docelowego.

## Kryteria odbioru

- [ ] AC-01: ticket, `intent.json`, plan agenta i TODO zapisują bounded
  `SESSION_EXECUTION_AUTHORIZATION` przed zmianą plików implementacji.
- [ ] AC-02: renderer tworzy dokładnie jeden atomowy, todo2code-readable rekord
  na akcję w obu projekcjach, ze zidentyfikowanym działaniem, findingiem,
  ścieżkami, kryteriami i deterministyczną weryfikacją; metadane i guardraile są
  nagłówkami pomijanymi przez ekstraktor.
- [ ] AC-03: projekcje są atomowo zapisywane do deklarowanych ścieżek, a osobne
  polecenie wykrywa brak, drift bajtów i próbę wyjścia poza repository root jako
  `GOV-REMEDIATION-004`.
- [ ] AC-04: analizator używa grafu todo2code do ograniczenia diagnostyk i
  planów do rekordów bieżącej projekcji; ignoruje niepowiązaną historię, a
  zachowuje wykrywanie rzeczywistych scope/criterion/priority/deletion oraz
  ambiguity/conflict; overlay wiąże digest grafu i użyte record IDs.
- [ ] AC-05: zasady, dokumentacja, katalog diagnostyk, runbook i szablon AGENTS
  jednoznacznie definiują przepływ oraz poprawne miejsce zapisu każdego rodzaju
  wiedzy naprawczej.
- [ ] AC-06: focused i pełne testy, Ruff, governance gate oraz rzeczywisty
  deterministyczny todo2code przechodzą; projekcja nie wytwarza fałszywych
  `AMBIGUOUS_REQUIREMENT`, a advisory overlay zawiera wyłącznie powiązane plany.

## Ryzyka i uwagi

- Format Markdown jest wejściem do istniejącego ekstraktora todo2code. Regresja
  musi testować rzeczywisty ekstraktor, a nie tylko wygląd tekstu.
- Graph/diagnostics/plans pozostają pełnymi artefaktami wejściowymi związanymi
  digestem; filtrowanie dotyczy jedynie tego, które rekordy są relewantne dla
  bieżącej intencji.
- Brak grafu przy analizie nie daje wiarygodnej korelacji i musi być traktowany
  fail-closed, zamiast importować wszystkie historyczne sygnały.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-073/`.
