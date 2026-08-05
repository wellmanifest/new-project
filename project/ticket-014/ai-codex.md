---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-014
---
# Participant: codex (AI agent)

## Understanding

Użytkownik chce jednego mapowalnego kontraktu klasyfikacji pracy zamiast
nieporównywalnych pól `high/medium`, `P0/P1` i opisowych etykiet. Rodzaj pracy
oraz pilność muszą pozostać osobnymi wymiarami.

Kanoniczny model:

| Wymiar | Wartości | Znaczenie |
| :--- | :--- | :--- |
| `kind` | `BUG`, `FEATURE`, `SERVICE` | typ rezultatu; kolejność BUG → FEATURE → SERVICE |
| `priority` | `P0`, `P1`, `P2`, `P3` | pilność wewnątrz danego rodzaju |
| `origin` | `regression`, `requested`, `health` | dlaczego praca powstała |

Comparator: `dependencies → kind → priority → stableId`.

Reguły CC:

- CC zwiększone przez ocenianą zmianę lub nowo przekraczające próg:
  `BUG / regression`;
- CC istniejące w baseline i niepogorszone przez zmianę:
  `SERVICE / health`;
- refaktoryzacja CC wymagana jako zależność funkcji:
  `SERVICE`, ale wykonywana wcześniej przez graf zależności;
- przerwa działania lub ryzyko bezpieczeństwa związane z CC:
  `BUG`, z priorytetem wynikającym z wpływu.

## Execution plan

1. Dodać `governance/work-classification.dsl.json` jako jedyne źródło
   porządku, wymiarów i deterministycznych reguł CC.
2. Dodać schemat Draft 2020-12 odrzucający dryf enumów, kolejności i reguł.
3. Dodać normatywne reguły DSL do `POLICY.md` bez duplikowania danych
   konfiguracyjnych.
4. Włączyć oba artefakty do `governance/package-manifest.json`.
5. Rozszerzyć istniejący test governance o przypadki pozytywne i negatywne.
6. Po publikacji utworzyć osobne tickety adopcyjne:
   - `semcod/todo2code`: pola `kind/origin`, diff-aware CC i sortowanie;
   - `semcod/goal`: mapowanie planfile i zachowanie klasyfikacji;
   - oba repozytoria: upgrade locka do tego samego pełnego SHA standardu.

## Acceptance evidence

- `bash tests/governance-validator.test.sh`
- `python3 -m json.tool governance/work-classification.dsl.json`
- `python3 -m json.tool governance/work-classification.schema.json`
- `bash tests/adoption-lock.test.sh`
- `git diff --check`

## Actual changes

- Brak zmian implementacyjnych; plan oczekuje na zatwierdzenie.

## Blockers

- Wymagane jest jawne zatwierdzenie planu i `intent.json`.
