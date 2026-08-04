# Ticket 007: Publikacja immutable 0.10.0

- **ID**: ticket-007
- **Owner**: unresolved:human
- **Status**: BACKLOG
- **Workflow state**: BACKLOG
- **Utworzono**: 2026-08-04

## Cel i zakres

Opublikować dokładny commit `0.10.0` jako chroniony tag i GitHub Release,
ponownie wykonać testy z czystego checkoutu oraz zapisać pełny SHA jako źródło
adopcji. Publikacja ma obejmować scalone uszczelnienie z PR #4.

## Kryteria odbioru

- [ ] Tag `v0.10.0` i Release wskazują ten sam pełny SHA.
- [ ] CI oraz trzy zestawy regresyjne przechodzą z czystego checkoutu.
- [ ] Dowód publikacji nie zawiera sekretów ani ścieżek lokalnej maszyny.
- [ ] Udokumentowano rollback do poprzedniego opublikowanego SHA.
