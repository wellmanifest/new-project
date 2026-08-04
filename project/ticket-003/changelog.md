# Ticket Changelog (ticket-003)

## [0.2.1] - 2026-08-04

- Reopened the matching integration slice after a hosted push run exposed the
  workflow-owned standard checkout as an untracked target path. The reusable
  workflow now excludes only that injected directory through `.git/info/exclude`;
  tracked PR files remain enforceable.

## [0.1.0] - 2026-08-04

- Utworzono plan bezpiecznej walidacji PR przez allowlistowaną GitHub App lub
  zweryfikowaną atestację.
- Zakres ograniczono do standardu governance i dokumentacji migracji;
  repozytoria zależne wymagają własnych ticketów integracyjnych.

## [0.2.0] - 2026-08-04

- Dodano kontrakt evidence, osobny allowlist Validator Apps, walidację
  repozytorium/PR/HEAD/ticketu/aktora oraz obsługę zweryfikowanych atestacji.
- Zaktualizowano DSL, workflow, generator adopcji, instrukcje i dokumentację.
- Wszystkie zestawy regresyjne i kontrole składni zakończyły się powodzeniem.
