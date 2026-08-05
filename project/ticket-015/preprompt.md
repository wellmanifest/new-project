# Preprompt i wytyczne techniczne (ticket-015)

- **Tytuł zadania**: Publikacja immutable 0.11.0
- **Utworzono**: 2026-08-05T08:48:00Z

## Wymagania

- Zaktualizuj wyłącznie pięć zatwierdzonych plików release.
- Zachowaj pustą sekcję `Unreleased` i przenieś wydawane zmiany do 0.11.0.
- Uruchom trzy testy huba oraz kontrolę składni JSON i diffu.
- Po chronionym merge testuj dokładny SHA w czystym detached checkoutcie.
- Nie twórz ani nie przesuwaj tagu, jeżeli `v0.11.0` już istnieje.
- Nie rozpoczynaj adopcji przed opublikowaniem pełnego SHA.

## Zasoby

- Runbook: `docs/RELEASES.md`
- Poprzedni release: `project/ticket-007/README.md`
- Kontrakt: `governance/work-classification.dsl.json`
