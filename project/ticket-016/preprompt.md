# Preprompt i wytyczne techniczne (ticket-016)

- Dodaj `new-project.intent/v3` bez usuwania odczytu historycznych v1/v2.
- Wymagaj `classification.kind`, `classification.priority` i
  `classification.origin` dla aktywnej implementacji.
- Ładuj zarządzany `.governance/work-classification.dsl.json` fail-closed.
- Nie dodawaj zależności runtime ani klasyfikacji opartej na LLM.
- Release 0.12.0 pozostaje zablokowany do zakończenia tego ticketu.
