# Ticket 031: Log every autonomous decision as a recomputable DSL record

- **ID**: ticket-031
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: WAIT_FOR_APPROVAL
- **Utworzono**: 2026-08-06

## Cel i Zakres

Autonomia wymaga, żeby każdą decyzję podjętą przez agenta dało się później
sprawdzić — nie „przeczytać", tylko **przeliczyć ponownie**. Ten ticket
wprowadza kontrakt logu decyzji: markdown z blokami `dsl`, w tym samym języku
reguł co `CONTRIBUTING.md` i `POLICY.md`.

Co już istnieje i czego ten ticket nie dubluje:

| artefakt | rola |
|---|---|
| `governance/change-evaluation.schema.json` | maszynowy zapis oceny zmiany (`t2c.change-evaluation/v1`) |
| `governance/approval-evidence.schema.json` | dowód zaufanego zatwierdzenia |
| `governance/diagnostics.json` | stabilne kody diagnostyczne |
| `scripts/runtime.sh` | waliduje `change-evaluation.json` wobec kontraktu |

Czego brakuje: **reguły, że decyzja bez logu jest niedopuszczalna**, oraz
formy, w której człowiek i agent czytają ten sam zapis. Dziś ocena zmiany jest
walidowana, ale sam przebieg rozumowania — co odrzucono, na podstawie której
reguły, przy jakich wejściach — nie jest nigdzie utrwalony.

## Założenie projektowe, od którego wszystko zależy

**Log napisany przez LLM nie jest dowodem na temat LLM.** Jeśli wpis jest prozą
wyprodukowaną przez model, audyt mówi tylko, co model *twierdzi*, że zrobił.
Żeby wpis był sprawdzalny, musi nieść deterministyczne wejścia i zastosowaną
regułę, tak aby strona trzecia mogła wyprowadzić werdykt ponownie, nie ufając
narratorowi.

Stąd trzy wymagania, które odróżniają ten log od dziennika zdarzeń:

1. **Przeliczalność** — wpis zawiera wejścia, nie streszczenie wejść.
2. **Falsyfikowalność** — wpis zawiera odrzuconą alternatywę wraz z regułą, na
   której podstawie odpadła. Log rejestrujący wyłącznie to, co zrobiono, nie
   odróżnia decyzji trafnej od szczęśliwej.
3. **Nieodwracalność** — wpis jest dopisywany i związany z head SHA. Bez tego
   kolejna naprawa może przepisać własną historię.

Rozdział autorytetu pozostaje ten, który już obowiązuje w `P-CORE-016`:
werdykt pochodzi z bramki deterministycznej, opinia modelu jest logowana jako
`ADVISORY` i nigdy nie jest korzeniem zaufania.

## Proponowany kontrakt

```dsl
DOCUMENT DECISION_LOG
VERSION 1
LANGUAGE PL
MODE STRICT
PURPOSE "sprawdzalny zapis decyzji podejmowanych autonomicznie"
POLICY "POLICY.md"

RULE C-DECISION-001 TYPE REQUIRED
WHEN AGENT_DECISION_AFFECTS_REPOSITORY_STATE
DO APPEND DECISION_RECORD TO "project/{TICKET_ID}/decisions.md"
DO REQUIRE RECORD_BINDS (DECISION_ID AND TICKET AND HEAD_SHA AND CORRELATION_ID)
DO REQUIRE RECORD_NAMES APPLIED_RULE_ID
FORBID DECISION_WITHOUT_RECORD
ASSERT RECORD_IS_APPEND_ONLY
NEXT VALIDATION OR BLOCKED

RULE C-DECISION-002 TYPE REQUIRED
WHEN DECISION_RECORD_WRITTEN
DO REQUIRE DETERMINISTIC_INPUTS_STORED_VERBATIM
DO REQUIRE REJECTED_ALTERNATIVE_AND_ITS_BLOCKING_RULE
FORBID SUMMARY_IN_PLACE_OF_INPUTS
ASSERT VERDICT_RECOMPUTABLE_FROM_RECORD_ALONE
NEXT VALIDATION OR BLOCKED

RULE C-DECISION-003 TYPE FORBIDDEN
WHEN LLM_OUTPUT_PRESENT_IN_DECISION_RECORD
DO REQUIRE AUTHORITY_LABEL IN ["DETERMINISTIC", "ADVISORY"]
FORBID TREAT_ADVISORY_AS_VERDICT
ASSERT VERDICT_AUTHORITY = "DETERMINISTIC"
NEXT VALIDATION OR BLOCKED

RULE C-DECISION-004 TYPE REQUIRED
WHEN DECISION_RECORD_REVIEWED
DO REPLAY DETERMINISTIC_INPUTS_AGAINST_APPLIED_RULE
DO REQUIRE REPLAYED_VERDICT = RECORDED_VERDICT
FORBID ACCEPT_RECORD_THAT_CANNOT_BE_REPLAYED
ASSERT DIVERGENCE_REPORTED_WITH_STABLE_DIAGNOSTIC_CODE
NEXT PUBLICATION OR BLOCKED
```

Kształt pojedynczego wpisu, ten sam dla naprawy i dla walidacji:

```dsl
DECISION D-031-0007
TICKET ticket-031
HEAD_SHA 4116ae07a1c39f2b8d5e1c0a7b3f9d2e6c8a4b10
CORRELATION_ID new-project-pr-40-ticket-030-4116ae07a1
ACTOR agent:validator
APPLIED_RULE P-CORE-015
INPUT required_checks = ["test", "windows-governance"]
INPUT observed_checks = ["test=PASS", "windows-governance=PASS"]
INPUT author_login = "tom-sapletta-com"
INPUT reviewer_login = "ifuri-validator-agent[bot]"
VERDICT APPROVE AUTHORITY DETERMINISTIC
REJECTED REQUEST_CHANGES BECAUSE NO_UNSAFE_CHANGE_REASON_FOUND
ADVISORY llm_verdict = "APPROVE" MODEL "openrouter/z-ai/glm-5.2"
ASSERT VERDICT_AUTHORITY != "ADVISORY"
```

Wpis jest przeliczalny: mając `INPUT` i `APPLIED_RULE`, strona trzecia
wyprowadza `VERDICT` bez czytania `ADVISORY`. Jeśli nie wyprowadzi tego samego
— `C-DECISION-004` zgłasza rozjazd kodem diagnostycznym.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: Kontrakt `DECISION_LOG` jest zapisany w `CONTRIBUTING.md` w blokach
  `dsl`, w numeracji `C-DECISION-*`, z legendą spójną z istniejącą.
- [ ] AC-02: `governance/decision-record.schema.json` opisuje ten sam wpis
  maszynowo; forma DSL i forma JSON są wzajemnie wyprowadzalne.
- [ ] AC-03: Nowe kody w `governance/diagnostics.json` dla braku logu,
  wpisu nieprzeliczalnego i rozjazdu przy odtworzeniu.
- [ ] AC-04: Bramka w `tests/` odtwarza `INPUT` wobec `APPLIED_RULE` i failuje,
  gdy odtworzony werdykt różni się od zapisanego; test niesie przypadek
  pozytywny, przypadek rozjazdu i przypadek `ADVISORY` podanego jako werdykt.
- [ ] AC-05: Log jest append-only — test wykrywa modyfikację wcześniejszego
  wpisu, nie tylko jego usunięcie.
- [ ] AC-06: `docs/GOVERNANCE_ENFORCEMENT.md` opisuje, gdzie log powstaje przy
  naprawie, a gdzie przy walidacji, i który agent jest jego autorem.

## Ryzyka i Uwagi

- Ryzyko: log rozrasta się szybciej niż praca, którą opisuje. Mitygacja do
  rozważenia: wpis obowiązkowy tylko dla decyzji zmieniających stan
  repozytorium, nie dla każdego kroku rozumowania — stąd `WHEN` w
  `C-DECISION-001`.
- Ryzyko: `INPUT` z pełnym diffem uczyni log nieczytelnym. Mitygacja do
  rozstrzygnięcia: wejściem jest odniesienie o stabilnej treści (SHA, nazwa
  checku, ścieżka), nie sama treść.
- Uwaga: `t2c.change-evaluation/v1` niesie już `verdict`, `confidence`,
  `gates` i `provenance`. Wpis decyzji powinien być z niego **wyprowadzany**,
  a nie pisany niezależnie — inaczej powstaną dwie prawdy o tej samej ocenie.
- Uwaga: `repair-agent` nie jest zainstalowany na `wellmanifest`, więc log
  naprawy powstanie tu dopiero, gdy będzie. Log walidacji powstaje już teraz.
- Zależność: `ticket-028` — bez atrybucji ticketu wpis nie ma czym związać
  `TICKET` i `CORRELATION_ID`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-031/`.
