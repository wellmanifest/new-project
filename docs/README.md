# Indeks dokumentacji

## Źródła prawdy

- `GPT56Luna/CONTRIBUTING.md` — rzeczywista instrukcja operacyjna dla agentów AI w tym repozytorium.
- `GPT56Luna/ANALIZA-DOKUMENTACJI.md` — analiza zgodności dokumentacji z `project.sh`, historia decyzji i znane luki.
- `README.md` — ogólny, repozytoryjny standard pracy ludzi i agentów AI.
- `POLICY.md` — zasady nazewnictwa, modularności, zależności, bezpieczeństwa i współpracy.
- `project.sh` — aktualna automatyzacja przygotowania środowiska i analizy projektu.
- `.devin/workflows/analyze-documentation.md` — procedura weryfikacji dokumentacji dla agentów.

## Kolejność czytania przez agenta

1. `GPT56Luna/CONTRIBUTING.md`
2. `README.md`
3. `POLICY.md`
4. `project.sh`, jeżeli zadanie dotyczy skryptu lub narzędzi
5. `GPT56Luna/ANALIZA-DOKUMENTACJI.md`
6. `TODO.md`, jeżeli istnieje

## Ważne ograniczenie

Dokumentacja opisuje aktualny zestaw skryptów i standardów, a nie gotową aplikację. W repozytorium nie znaleziono obecnie `src/`, `tests/`, konfiguracji CI ani plików Docker. Agent musi zweryfikować każdy taki element przed użyciem lub opisaniem go jako dostępnego.
