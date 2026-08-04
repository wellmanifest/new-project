# Preprompt & Wytyczne Techniczne (ticket-003)

- **Tytuł Zadania**: Zaufana walidacja PR przez agentów
- **Utworzono**: 2026-08-04T13:34:12Z

## Wymagania i Ograniczenia Techniczne

- Nie traktuj `review.user.type == Bot` jako wystarczającego dowodu.
- Authority musi być jawnie skonfigurowane poza decyzją modelu LLM.
- Każdy approval musi wskazywać dokładne repozytorium, PR, HEAD i ticket.
- Zmiana HEAD unieważnia wcześniejszy approval.
- Podpisana atestacja jest zaufana dopiero po deterministycznej weryfikacji
  podpisu i wystawcy przez chroniony workflow.
- Zachowaj kompatybilność dla istniejącej ścieżki zaufanego review człowieka.
- Przykłady OpenRouter mają używać `openrouter/z-ai/glm-5.2`, nie Gemini 3.1
  Pro Preview.

## Podlinkowane zasoby

- `POLICY.md`, `CONTRIBUTING.md`
- `.github/workflows/governance.yml`
- `governance/manifest.schema.json`
- `scripts/governance_check.py`
- `docs/GOVERNANCE_ENFORCEMENT.md`
- Dowody wejściowe użytkownika dotyczące `subactor/validator-agent` i
  `semcod/todo2code` z 2026-08-04.

## Dyrektywy wykonawcze

- Przed implementacją uzyskaj zatwierdzenie niniejszego planu.
- Zmiany wykonuj wyłącznie w `intent.json.allowedPaths`.
- Najpierw dodaj kontrakt i negatywne przypadki testowe, potem workflow i
  dokumentację.
- Nie instaluj GitHub App ani nie zmieniaj repozytoriów zależnych w ramach tego
  ticketu; przygotuj dla nich jednoznaczną instrukcję i wymagania osobnych
  ticketów integracyjnych.
