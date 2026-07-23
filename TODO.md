# TODO

## Etap 0 - analiza repozytorium

- [x] Przeanalizowac cala strukture repozytorium.
- [x] Przeanalizowac README.md.
- [x] Przeanalizowac POLICY.md.
- [x] Przeanalizowac CONTRIBUTING.md.
- [x] Przeanalizowac docs/README.md.
- [x] Przeanalizowac wybrane warianty dokumentow badawczych w GPT56Luna i Opus48Medium.
- [x] Przeanalizowac project.sh.
- [x] Sprawdzic istniejace testy i skrypty.
- [ ] Zapisać decyzje architektoniczne w docs/architecture.md.

Uwagi:

- Repozytorium startowalo jako zbior dokumentacji, polityk i analiz DSL, bez aplikacji, testow, CI i backendu.
- Foldery `GPT56Luna/`, `Opus48Medium/`, `SWE17/` i `perplexity/` pozostaja materialem referencyjnym.
- Aktualna dokumentacja projektu MVP bedzie utrzymywana w plikach glownych oraz w `docs/`.
- `project.sh` nie zostanie uruchomiony jako domyslny test/install runner dla MVP, poniewaz instaluje nieprzypiete zaleznosci, generuje artefakty analityczne i uruchamia `doql --force`. Zostanie opisany jako narzedzie analizy repozytorium.
- Przed utworzeniem tego planu powstala czesc szkieletu implementacji podczas przerwanego przebiegu. Nie jest oznaczana jako ukonczona, dopoki nie zostanie doprowadzona, przetestowana i udokumentowana.

## Etap 1 - specyfikacja DSL

- [ ] Zdefiniowac zakres MVP.
- [ ] Zdefiniowac kanoniczny model DSL.
- [ ] Zdefiniowac AST.
- [ ] Zdefiniowac JSON Schema.
- [ ] Przygotowac czytelna reprezentacje human-readable DSL.
- [ ] Przygotowac przyklady w `examples/`.

## Etap 2 - implementacja TypeScript

- [ ] Utworzyc parser i walidator DSL.
- [ ] Utworzyc TypeScript runtime.
- [ ] Utworzyc deterministic policy engine.
- [ ] Utworzyc state machine.
- [ ] Utworzyc registry akcji.
- [ ] Utworzyc mockowe konektory.
- [ ] Utworzyc zapis audytu.
- [ ] Utworzyc CLI dla Windows/Linux.

## Etap 3 - integracje

- [ ] Utworzyc LLM planner w trybie mock.
- [ ] Utworzyc opcjonalny LLM planner OpenRouter.
- [ ] Utworzyc Python verifier w trybie mock.
- [ ] Utworzyc opcjonalny Python verifier LiteLLM/OpenRouter.
- [ ] Utworzyc backend API.
- [ ] Utworzyc frontend demonstracyjny.

## Etap 4 - jakosc

- [ ] Dodac testy jednostkowe.
- [ ] Dodac testy integracyjne.
- [ ] Dodac testy E2E.
- [ ] Dodac testy bezpieczenstwa.
- [ ] Dodac CI dla Windows i Linux.
- [ ] Uruchomic pelny zestaw testow lokalnych.

## Etap 5 - zakonczenie

- [ ] Sprawdzic wszystkie przyklady.
- [ ] Zaktualizowac README.md.
- [ ] Zaktualizowac docs/architecture.md.
- [ ] Zaktualizowac docs/dsl-specification.md.
- [ ] Zaktualizowac docs/security-model.md.
- [ ] Zaktualizowac docs/testing.md.
- [ ] Zaktualizowac docs/windows-installation.md.
- [ ] Zaktualizowac docs/linux-installation.md.
- [ ] Zaktualizowac docs/openrouter-configuration.md.
- [ ] Utworzyc VERSION.md.
- [ ] Utworzyc lub zaktualizowac CHANGELOG.md.
- [ ] Sprawdzic zgodnosc TODO.md, VERSION.md, CHANGELOG.md, README.md, implementacji i testow.
- [ ] Wykonac koncowy audyt repozytorium.

## Nowe zadania wykryte podczas pracy

- [ ] Rozwazyc osobne uporzadkowanie `project.sh`: rozdzielenie instalacji od analizy, przypiecie wersji zaleznosci i usuniecie uzycia globalnego `pip`.
- [ ] Rozwazyc migracje historycznych analiz do `docs/research/` bez usuwania oryginalnych katalogow.
