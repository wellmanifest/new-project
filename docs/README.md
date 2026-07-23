# Indeks dokumentacji

## Zrodla prawdy

- `README.md` - ogolny standard pracy ludzi i agentow AI w repozytorium.
- `POLICY.md` - zasady zgodnosci, bezpieczenstwa, dowodow i ograniczen pracy.
- `CONTRIBUTING.md` - proceduralny proces pracy nad repozytorium.
- `TODO.md` - glowna kolejka pracy i kolejnosc etapow projektu.
- `docs/architecture.md` - architektura MVP, role uczestnikow, przeplywy NL/DSL, akceptacje, mocki i decyzja dotyczaca `project.sh`.
- `docs/research-migration-audit.md` - audyt przeniesienia historycznych materialow badawczych do `research/`.
- `project.sh` - historyczny skrypt analityczno-narzedziowy; nie jest aktywnym bootstrapem MVP.
- `.devin/workflows/analyze-documentation.md` - procedura weryfikacji dokumentacji dla agentow, jezeli jest potrzebna w dalszej pracy.

## Materialy badawcze

Historyczne foldery badawcze zostaly przeniesione do `research/` i nie powinny byc przywracane do starych lokalizacji:

- `research/GPT56Luna/`
- `research/Opus48Medium/`
- `research/SWE17/`
- `research/perplexity/22.07/`
- `research/perplexity/23.07/`

## Aktualna struktura robocza

Repozytorium zawiera obecnie implementacje MVP i artefakty testowe:

- `packages/` - pakiety TypeScript: model DSL, runtime, planner LLM/mock i CLI.
- `apps/` - backend demonstracyjny i statyczny frontend.
- `verifier/` - Python verifier.
- `examples/` - scenariusze regresyjne MVP.
- `tests/` - testy TypeScript.
- `mock-data/` - dane przykladowe dla trybu offline.

## Kolejnosc czytania przez agenta

1. `TODO.md`
2. `README.md`
3. `POLICY.md`
4. `CONTRIBUTING.md`
5. `docs/README.md`
6. `docs/architecture.md`, jezeli zadanie dotyczy celu, przeplywow, rol albo granic MVP
7. `docs/research-migration-audit.md`, jezeli zadanie dotyczy migracji materialow badawczych
8. `project.sh`, jezeli zadanie dotyczy historycznych narzedzi lub decyzji o ich niewykorzystywaniu
9. Odpowiednie katalogi `packages/`, `apps/`, `verifier/`, `examples/` i `tests/`

## Ograniczenie MVP

Domyslny tryb pracy MVP ma dzialac offline, na mockach i bez klucza OpenRouter. Komendy instalujace zaleznosci albo pobierajace narzedzia z sieci wymagaja osobnej diagnozy i nie sa czescia tego etapu dokumentacyjnego.
