# Ticket 153: Bind adoption workflow pins from required-check registry

- **ID**: ticket-153
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-30

## Cel i Zakres

Usunąć bootstrap deadlock między aktualizacją targetowego wrappera CI a
adopcją nowego manifestu. Standard ma dostarczać zarządzany rejestr dokładnych
workflowów, których dwa niezmienne piny muszą zostać zmienione razem z
`standardAdoption.toRevision`.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: ścieżka workflow pochodzi z zarządzanego rejestru, nie z
      hardkodowanej listy runtime ani z intentu targetu.
- [x] AC-02: workflow jest bindingiem adopcji tylko przy zgodnych `uses@SHA`
      i `standard-ref: SHA` równych `toRevision`.
- [x] AC-03: niezarejestrowana ścieżka i błędny pin nadal kończą się
      `GOV-WORKSTREAM-003`.
- [x] AC-04: pełna suita standardu przechodzi.

## Ryzyka i Uwagi

- Rejestr jest plikiem `managed` objętym lockiem publikacji; target nie może
  poszerzyć go lokalnie jak pliku `extendable`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-153/`.
