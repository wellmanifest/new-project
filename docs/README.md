# Indeks dokumentacji

## Źródła prawdy

- `GPT56Luna/CONTRIBUTING.md` — proceduralna instrukcja operacyjna dla agentów AI w tym repozytorium.
- `GPT56Luna/POLICY.md` — proceduralne reguły zgodności, dowodów, bezpieczeństwa i walidacji.
- `GPT56Luna/ANALIZA-DOKUMENTACJI.md` — analiza zgodności dokumentacji z `project.sh`, historia decyzji i znane luki.
- `README.md` — ogólny, repozytoryjny standard pracy ludzi i agentów AI.
- `POLICY.md` — zasady nazewnictwa, modularności, zależności, bezpieczeństwa i współpracy.
- `project.sh` — aktualna automatyzacja przygotowania środowiska i analizy projektu.
- `.devin/workflows/analyze-documentation.md` — procedura weryfikacji dokumentacji dla agentów.

## Kolejność czytania przez agenta

1. `GPT56Luna/CONTRIBUTING.md`
2. `GPT56Luna/POLICY.md`
3. `README.md`
4. `POLICY.md`
5. `project.sh`, jeżeli zadanie dotyczy skryptu lub narzędzi
6. `GPT56Luna/ANALIZA-DOKUMENTACJI.md`
7. `TODO.md`, jeżeli istnieje

## Ważne ograniczenie

Dokumentacja opisuje aktualny zestaw skryptów i standardów, a nie gotową aplikację. W repozytorium nie znaleziono obecnie `src/`, `tests/`, konfiguracji CI ani plików Docker. Agent musi zweryfikować każdy taki element przed użyciem lub opisaniem go jako dostępnego.
