---
participant-id: agent:claude
participant: claude
role: agent
ticket: ticket-031
---
# Participant: claude (AI agent)

## Understanding

Żądanie brzmi „loguj decyzje", ale samo logowanie celu nie osiąga. Cel to
możliwość sprawdzenia, czy decyzja podjęta autonomicznie była słuszna — a
prozy napisanej przez model nie da się w tym celu użyć, bo audyt takiej prozy
mówi wyłącznie, co model twierdzi. Log musi być **przeliczalny**: nieść
deterministyczne wejścia i zastosowaną regułę, żeby werdykt dało się
wyprowadzić ponownie bez ufania narratorowi.

Drugi punkt, który łatwo pominąć: log rejestrujący tylko to, co zrobiono, nie
odróżnia decyzji trafnej od szczęśliwej. Falsyfikowalna jest dopiero odrzucona
alternatywa wraz z regułą, która ją zablokowała. Dlatego `REJECTED ... BECAUSE`
jest w kontrakcie polem wymaganym, nie ozdobnym.

Trzeci: bez append-only i związania z head SHA kolejna naprawa może przepisać
własną historię, co czyni cały log bezwartościowym dokładnie w tym momencie,
w którym byłby potrzebny.

Świadomie nie proponuję nowego formatu obok istniejącego. `t2c.change-evaluation/v1`
niesie już `verdict`, `gates`, `confidence` i `provenance`; wpis decyzji ma być
z niego wyprowadzany, inaczej powstaną dwie prawdy o tej samej ocenie.

Rozdział autorytetu zostaje ten z `P-CORE-016`: werdykt deterministyczny,
opinia modelu oznaczona `ADVISORY`. Kontrakt to wymusza asercją
`VERDICT_AUTHORITY = "DETERMINISTIC"`, a nie komentarzem.

## Execution plan

1. Zapisać kontrakt `C-DECISION-001..004` w `CONTRIBUTING.md` w istniejącej
   konwencji DSL i numeracji.
2. Dodać `governance/decision-record.schema.json` wzajemnie wyprowadzalny
   z formy DSL, wraz z kodami w `governance/diagnostics.json`.
3. Dodać bramkę odtwarzającą `INPUT` wobec `APPLIED_RULE` i porównującą
   werdykt; przypadki: zgodny, rozjazd, `ADVISORY` podany jako werdykt.
4. Dodać test append-only wykrywający modyfikację wcześniejszego wpisu.
5. Opisać w `docs/GOVERNANCE_ENFORCEMENT.md` miejsce powstawania logu przy
   naprawie i przy walidacji.

## Actual changes

- None; waiting for approval.

## Blockers

- Human approval is required before implementation.
- Zależność od `ticket-028`: bez atrybucji ticketu wpis nie ma czym związać
  `TICKET` i `CORRELATION_ID`.
- Rozstrzygnięcia wymaga granica `INPUT`: odniesienie o stabilnej treści
  kontra treść dosłowna, przy diffach nietrywialnego rozmiaru.
