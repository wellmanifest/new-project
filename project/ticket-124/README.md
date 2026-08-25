# Ticket 124: Bind change lease operations to normative policy

- **ID**: ticket-124
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-25

## Cel i Zakres
Powiązać opublikowany w ticket-123 kontrakt change lease z normatywnymi
regułami pracy wieloagentowej: claim przed efektem, monotoniczny CAS/fencing,
exact-head publication freeze oraz merge receipt przed close/GC. Audyt
enforcement ma uwzględniać kody emitowane przez companion checker.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `POLICY.md` i `CONTRIBUTING.md` zawierają siedem zamkniętych reguł
      `P-LEASE-*` i `C-LEASE-*` bez rozszerzania authority runtime.
- [x] AC-02: Wszystkie reguły mapują się deterministycznie do kodów
      `GOV-CHANGE-LEASE-*`, a audyt raportuje 0 unmapped i 0 unclaimed.
- [x] AC-03: Rule-enforcement tests i governance hub przechodzą na dokładnej
      bazie `67a3421bc390c4285a094a631e7a7b7e8180720e`.

## Ryzyka i Uwagi
- Ryzyko: dokument może deklarować więcej niż checker egzekwuje. Mitygacja:
  każda reguła ma deterministyczny mapping, a audit skanuje companion checker.

## Dowód integracji

- Pull request: `wellmanifest/new-project#212`
- Zatwierdzony implementation HEAD: `19a2ac7cfc8149dd5aced4058eda78a0496dd9bd`
- Merge commit: `5b4ef71224054a3b24c4d5bc56773f05ce0e34fa`
- Merged at: `2026-08-25T20:44:21Z`
- Validator run: `subactor/validator-agent#32896963260`

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-124/`.
