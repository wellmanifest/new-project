---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-003
---
# Participant: codex (AI agent)

## Understanding

Upstream ma dwie rozbieżne gałęzie o tej samej wersji. `main` zawiera poprawę,
która zwalnia rezerwacje dla `PLAN/BLOCKED`, oraz bezpieczny generator adopcji.
Gałąź bounded-delivery zawiera wymagane limity i architekturę, ale jej domyślny
manifest nadal uznaje `PLAN/BLOCKED` za aktywne. `todo2code` jest przypięty do
tej drugiej gałęzi, co utrzymuje cztery fałszywe diagnostyki ticketu-019.

Koru workflow jest target-specific i istnieje w `todo2code`, nie w upstreamie.
Historyczne dowody benchmarku pozostaną historyczne; wykonywalny wybór modelu
zostanie zmieniony na `openrouter/z-ai/glm-5.2` bez płatnego wywołania.

## Execution plan

1. Zatwierdzenie planu i integracyjnego wyjątku plikowego otrzymano od
   człowieka 2026-08-04; przejść do `IN_PROGRESS / EDIT`.
2. Selektywnie przenieść bounded schema/validator/test na bazę `main`, zachowując
   jej lifecycle i generator adopcji.
3. Nadać połączonemu kontraktowi wersję `0.10.0` i udokumentować migrację.
4. Uruchomić testy validatora, skryptów i adopcji bez sieci oraz LLM.
5. Opublikować branch i dopiero wtedy użyć pełnego SHA w `todo2code`.
6. W ticket-018 zaktualizować pakiet `.governance`, lock, dokumentację i model
   Koru; porównać diagnostyki przed/po i wykonać pełne testy targetu.

## Actual changes

- Human approved AC-01 and dependent todo2code AC-36..AC-40; ticket entered
  `IN_PROGRESS / EDIT` before contract implementation.
- The first 0.10 adoption-lock run exposed one stale version assertion in the
  existing adoption fixture. Added that exact test path to `allowedPaths` as a
  bounded correction required by AC-06; no outcome, component, dependency or
  production surface was added.

## Blockers

- Nie istnieje jeszcze jeden kanoniczny SHA zawierający oba zestawy poprawek.
- Wykonywalna aktualizacja `todo2code` zależy od zakończenia upstreamu.
