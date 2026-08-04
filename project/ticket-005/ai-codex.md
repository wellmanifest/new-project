---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-005
---
# Participant: codex (AI agent)

## Understanding

Niezależny Validator App wskazał dwa miejsca wymagające defence-in-depth w
kanonicznym standardzie: niepoprawny dowód pozostawał zwracany po zgłoszeniu
`GOV-APPROVAL-004/005`, a zwykły odczyt ścieżki nie wymuszał `O_NOFOLLOW`.
Raport nadal zawierał błąd, więc nie potwierdzono działającego bypassu, ale
projekcja zaufania powinna kończyć się natychmiast i jednoznacznie.

Polecenie użytkownika „popraw wskazane błędy” jest jawną zgodą sesyjną na ten
dokładny zakres. Nie jest trusted merge evidence.

## Execution plan

1. Dodać bezpieczny, ograniczony odczyt zewnętrznego JSON bez podążania za
   symlinkiem i z kontrolą regularnego pliku.
2. Zakończyć walidację dowodu po niezgodnym bindingu lub authority.
3. Rozszerzyć istniejący shellowy kontrakt regresyjny o brak projekcji oraz
   odrzucenie symlinku.
4. Uruchomić pełne testy huba i adopcji, sprawdzić diff oraz sekrety.
5. Opublikować przez mały PR i uzyskać niezależny review dla exact HEAD.

## Actual changes

- Ticket i architektura zostały zawężone do jednej granicy zaufania.
- `load_external_approval_evidence` otwiera zewnętrzny dowód przez deskryptor
  `O_NOFOLLOW`, wymaga regularnego pliku i nie stosuje niebezpiecznego
  fallbacku na platformie bez tej flagi.
- Dowód z niezgodnym bindingiem lub authority kończy walidację jako `None`;
  test wymaga równocześnie diagnostyku szczegółowego i ogólnego braku zaufanej
  aprobaty.
- Dodano test symlinku i zachowano pozytywne przypadki GitHub App oraz signed
  attestation.
- PR #4 został scalony po zielonym CI i current-head approval Validator App.
- Ticket przeszedł do `BLOCKED`, ponieważ dalszy krok zależy od publikacji
  immutable `v0.10.0` i zewnętrznej adopcji w `todo2code`.

## Blockers

- Brakuje tagu/GitHub Release `v0.10.0` wskazującego pełny SHA.
- `semcod/todo2code` nie może zakończyć produkcyjnej adopcji przed publikacją.
