# Ticket 012: Fixture upgrade i rollback między wydaniami

- **ID**: ticket-012
- **Owner**: unresolved:human
- **Status**: BACKLOG
- **Workflow state**: BACKLOG
- **Utworzono**: 2026-08-04

## Cel i zakres

Dodać deterministyczny test upgrade'u między dwoma rzeczywistymi,
opublikowanymi wersjami standardu, z zachowaniem lokalnego manifestu,
raportem konfliktów i odwracalnym rollbackiem.

## Kryteria odbioru

- [ ] Fixture używa dwóch pełnych SHA opublikowanych wydań.
- [ ] `--check` nie zapisuje plików i pokazuje plan migracji.
- [ ] Drift blokuje zwykły upgrade, a jawny upgrade zachowuje lokalny manifest.
- [ ] Rollback odtwarza poprzedni lock i artefakty bez utraty lokalnych plików.
