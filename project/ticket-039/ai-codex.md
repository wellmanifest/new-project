---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-039
---
# Participant: codex (AI agent)

## Understanding

Ticket 038 jest zakończony na chronionym `main@31dd391`, lecz immutable
`v0.12.0` nie zawiera nowego pola intent ani runtime. Downstream nie może
legalnie użyć nieopublikowanego `main`; potrzebuje nowego numeru, tagu,
GitHub Release i pełnego merge SHA. Ponieważ zmiana jest kompatybilnym,
opcjonalnym rozszerzeniem publicznego intent/v3, właściwą wersją jest `0.13.0`.

## Execution plan

1. Po osobnej aprobacie przejść do `IN_PROGRESS / EDIT`.
2. Zmienić wyłącznie pięć zatwierdzonych plików wersji, changelogu i asercji.
3. Zachować `0.12.0` po stronie bazowej regresji 0.12→0.13.
4. Uruchomić focused version/adoption tests i pełny Linux contract.
5. Opublikować PR i wymagać Linux, Windows oraz exact-head Validator App.
6. Po merge uruchomić pełny contract w czystym detached checkout merge SHA.
7. Potwierdzić nieobecność `v0.13.0`, utworzyć annotowany tag i GitHub Release
   wskazujące dokładnie ten merge SHA.
8. Zweryfikować peeled tag, Release target i cleanup brancha; potem przekazać
   pełny SHA do todo2code ticket-050.

## Actual changes

- Ticket 038 zakończono na `main@31dd391`; release metadata nie zostały jeszcze
  zmienione.
- Użytkownik zatwierdził implementację i publikację `v0.13.0`; ticket przeszedł
  do `IN_PROGRESS / EDIT` przed pierwszą zmianą release metadata.

## Blockers

- Brak przed implementacją; chronione checki i review pozostają wymagane.
