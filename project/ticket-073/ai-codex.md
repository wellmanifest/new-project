---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-073
---
# Participant: codex (AI agent)

## Understanding

Ticket 067 poprawnie rozdzielił reusable diagnostics/runbooks od targetowego
DSL, ale jego adapter nie odpowiada rzeczywistemu kontraktowi ekstraktora
todo2code. Każda niebędąca nagłówkiem linia Markdown jest tam osobnym rekordem;
obecny renderer emituje więc `Ticket:`, `Repository:`, digest, outcome,
constraints i non-goals jako pozorne wymagania. W `goal/ticket-055` dało to 12
fałszywych `AMBIGUOUS_REQUIREMENT`.

Obecny analizator sprawdza również każdy plan i każdą diagnostykę z całego
repozytorium przed korelacją. W tym samym przypadku 20 historycznych planów
spoza ticketu dało 22 fałszywe rozszerzenia scope. Wiarygodną granicą są rekordy
grafu todo2code, których `source.path` wskazuje deklarowane projekcje, oraz
`evidence.recordIds`/`recordIds` w planach i diagnostykach.

## Execution plan

1. Zatwierdzić bounded intent i indeks ticketu przed implementacją.
2. Zmienić renderer na jeden kompletny, konwencjonalnie sklasyfikowany rekord
   na akcję oraz atomowy zapis do deklarowanych ścieżek.
3. Dodać byte-exact `verify-todo2code` z fail-closed
   `GOV-REMEDIATION-004`.
4. Wymagać grafu przy analizie, wyznaczać rekordy projekcji po `source.path` i
   oceniać wyłącznie plany/diagnostyki cytujące te rekordy, wiążąc digest grafu
   i użyte record IDs w advisory overlay.
5. Uaktualnić regułę DSL, runbook, katalog, dokumentację i instrukcje adopcji.
6. Uruchomić test regresyjny oraz realny todo2code, pełne testy, Ruff i gate;
   zapisać dowody i dostarczyć przez Goal/PR z exact-head Validator review.

## Actual changes

- Initialized the bounded ticket and recorded `SESSION_EXECUTION_AUTHORIZATION`
  from the request to execute this work.
- Przeanalizowano realne artefakty `goal/ticket-055` i kod ekstraktora oraz
  generatora planów todo2code 0.5.1; potwierdzono oba źródła false-positive.
- Renderer emituje metadane i guardraile wyłącznie jako nagłówki oraz jeden
  kompletny conventional-commit-like rekord na akcję w task i TODO.
- Dodano atomowy zapis, deklarowane ścieżki oraz `verify-todo2code`, który
  wykrywa brak, byte drift i symlink/path escape jako `GOV-REMEDIATION-004`.
- Analyzer wymaga grafu, koreluje źródła przez `source.path`, filtruje plany i
  diagnostyki przez record IDs oraz wiąże graph/input digests i record IDs w
  advisory overlay.
- Pełny kontrakt dziewięciu zestawów shell, Ruff i testy schematów przechodzą.
- Rzeczywisty todo2code 0.5.1 na kopii `goal/ticket-055` wyekstrahował po trzy
  kompletne rekordy task/TODO bez brakujących pól i bez
  `AMBIGUOUS_REQUIREMENT`. Z 1888 rekordów i 50 planów repozytorium overlay
  przyjął wyłącznie 6 planów cytujących projekcję, bez blocking, ambiguity ani
  scope expansion. Zachował realną poradę `T2C_PRIORITY_DRIFT` P1 -> P2.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority is still required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.
