# Ticket 003: Zaufana walidacja PR przez agentów

- **ID**: ticket-003
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-04

## Cel i Zakres

Rozszerzyć standard governance o bezpieczną walidację PR przez dedykowanego
agenta GitHub App. Zgoda agenta ma być ważna wyłącznie dla jawnie dozwolonej
tożsamości, konkretnego repozytorium, numeru PR, aktywnego ticketu i bieżącego
SHA. Dowolny review typu `Bot` oraz niezweryfikowana deklaracja w plikach PR
pozostają niezaufane.

Zakres obejmuje DSL w `POLICY.md` i `CONTRIBUTING.md`, instrukcje agentów,
manifest i kontrakt dowodu approval, reusable workflow, deterministyczny
walidator, generator adopcji, dokumentację migracji oraz regresje.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: DSL rozróżnia zaufane review człowieka, jawnie dozwolonej GitHub
  App i kryptograficznie zweryfikowaną atestację; dowolny Bot jest odrzucany.
- [x] AC-02: Dowód approval wiąże źródło z `repository`, `pullRequest`,
  `headSha`, aktywnym ticketem i tożsamością wystawcy.
- [x] AC-03: Reusable workflow przyjmuje osobne, jawne konfiguracje ludzi i
  Validator Apps oraz przekazuje walidatorowi dowód dla dokładnego HEAD.
- [x] AC-04: Walidator deterministycznie odrzuca zły typ aktora, login spoza
  allowlisty, stare SHA, inny PR/repo/ticket i niezweryfikowaną atestację.
- [x] AC-05: Dokumentacja opisuje instalację Validator GitHub App,
  least-privilege, ochronę konfiguracji oraz migrację `validator-agent` i
  `todo2code` bez dopuszczania wszystkich botów.
- [x] AC-06: Przykładowa konfiguracja Validatora używa
  `openrouter/z-ai/glm-5.2`; wynik LLM pozostaje doradczy i nie jest źródłem
  zaufania.
- [x] AC-07: Testy pozytywne i negatywne governance/adoption przechodzą, a
  `git diff --check` nie zgłasza błędów.

## Ryzyka i Uwagi

- Review `Bot` bez allowlisty umożliwiłby obejście niezależnej akceptacji;
  mitygacją jest rozdzielenie typów authority i domyślna pusta lista App.
- Atestacja zapisana przez autora PR nie jest sama w sobie dowodem; zaufany
  workflow musi najpierw zweryfikować podpis i tożsamość wystawcy.
- Zmiana konfiguracji authority w tym samym PR może rozszerzać własne
  uprawnienia; ścieżki workflow i governance wymagają niezależnej ochrony
  CODEOWNERS/ruleset.
- Instalacja GitHub App w repozytoriach zależnych jest osobną operacją
  administracyjną i nie zostanie zasymulowana przez lokalne testy.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
testy i skrypty pozostają w zwykłych katalogach repozytorium.
