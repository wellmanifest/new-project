# Ticket 007: Publikacja immutable 0.10.0

- **ID**: ticket-007
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-04

## Cel i zakres

Opublikować dokładny commit `0.10.0` jako chroniony tag i GitHub Release,
ponownie wykonać testy z czystego checkoutu oraz zapisać pełny SHA jako źródło
adopcji. Publikacja ma obejmować scalone uszczelnienie z PR #4.

## Kryteria odbioru

- [x] Tag `v0.10.0` i Release wskazują ten sam pełny SHA.
- [x] CI oraz trzy zestawy regresyjne przechodzą z czystego checkoutu.
- [x] Dowód publikacji nie zawiera sekretów ani ścieżek lokalnej maszyny.
- [x] Udokumentowano rollback do poprzedniego opublikowanego SHA.

## Walidacja przygotowania

- `git diff --check` — PASS.
- `tests/governance-scripts.test.sh` — PASS.
- `tests/governance-validator.test.sh` — PASS.
- `tests/adoption-lock.test.sh` — PASS.
- Kontrola ścieżek lokalnych i unsafe markerów — PASS.

Test czystego merge commita, tag i Release wykonano po scaleniu PR
przygotowującego wydanie.

## Dowód publikacji

- PR przygotowujący: #8, exact-head approval dla
  `ed32136c7af9b24e9c0aac1cd0bb5a0a7488d6de`.
- Release commit: `62ffb0dac1dba9294aa825ca5cc0344fefb33b0d`.
- Annotowany tag: `v0.10.0`; peeled commit jest równy release commitowi.
- GitHub Release: `https://github.com/wellmanifest/new-project/releases/tag/v0.10.0`.
- Czysty detached checkout: trzy zestawy testów PASS, status pusty przed i po.

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
