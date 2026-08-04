# Ticket 007: Publikacja immutable 0.10.0

- **ID**: ticket-007
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-04

## Cel i zakres

Opublikować dokładny commit `0.10.0` jako chroniony tag i GitHub Release,
ponownie wykonać testy z czystego checkoutu oraz zapisać pełny SHA jako źródło
adopcji. Publikacja ma obejmować scalone uszczelnienie z PR #4.

## Kryteria odbioru

- [ ] Tag `v0.10.0` i Release wskazują ten sam pełny SHA.
- [ ] CI oraz trzy zestawy regresyjne przechodzą z czystego checkoutu.
- [ ] Dowód publikacji nie zawiera sekretów ani ścieżek lokalnej maszyny.
- [x] Udokumentowano rollback do poprzedniego opublikowanego SHA.

## Walidacja przygotowania

- `git diff --check` — PASS.
- `tests/governance-scripts.test.sh` — PASS.
- `tests/governance-validator.test.sh` — PASS.
- `tests/adoption-lock.test.sh` — PASS.
- Kontrola ścieżek lokalnych i unsafe markerów — PASS.

Test czystego merge commita, tag i Release pozostają do wykonania po scaleniu
PR przygotowującego wydanie.

## Plan publikacji

1. Scalić wyłącznie dokumentację wydania po zielonym CI i exact-head approval.
2. Ustalić pełny SHA merge commita z chronionego `main`.
3. W czystym, odłączonym checkoutcie tego SHA uruchomić trzy zestawy regresji.
4. Utworzyć jeden annotowany tag `v0.10.0`, wypchnąć go bez force i utworzyć
   GitHub Release wskazujący ten sam commit.
5. Zweryfikować tag i Release przez niezależne od lokalnego brancha odczyty.

## Warunki zatrzymania

- Istniejący tag lub Release o tej nazwie — STOP, bez przesuwania referencji.
- Niezielone CI, test lub brak exact-head approval — STOP, bez publikacji.
- HEAD `main` inny niż przetestowany SHA — ponowny czysty test nowego SHA.
