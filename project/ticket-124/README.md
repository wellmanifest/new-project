# Ticket 124: Bind change lease operations to normative policy

- **ID**: ticket-124
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-25

## Cel i Zakres
Powiązać opublikowany w ticket-123 kontrakt change lease z normatywnymi
regułami pracy wieloagentowej: claim przed efektem, monotoniczny CAS/fencing,
exact-head publication freeze oraz merge receipt przed close/GC. Audyt
enforcement ma uwzględniać kody emitowane przez companion checker.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: `POLICY.md` i `CONTRIBUTING.md` zawierają siedem zamkniętych reguł
      `P-LEASE-*` i `C-LEASE-*` bez rozszerzania authority runtime.
- [ ] AC-02: Wszystkie reguły mapują się deterministycznie do kodów
      `GOV-CHANGE-LEASE-*`, a audyt raportuje 0 unmapped i 0 unclaimed.
- [ ] AC-03: Rule-enforcement tests i governance hub przechodzą na dokładnej
      bazie `67a3421bc390c4285a094a631e7a7b7e8180720e`.

## Ryzyka i Uwagi
- Ryzyko: dokument może deklarować więcej niż checker egzekwuje. Mitygacja:
  każda reguła ma deterministyczny mapping, a audit skanuje companion checker.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-124/`.
