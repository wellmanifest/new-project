---
participant-id: agent:claude
participant: claude
role: agent
ticket: ticket-112
---
# Participant: claude (AI agent)

## Understanding

Wynika wprost z pilota adopcji w `twin-lifecycle`. Trzy slice'y (106, 107, 108)
zbudowały egzekwowalny kontrakt i włączyły bramę u adopterów, ale adopcja
zatrzymała się na deklaracji required-checks odziedziczonej po hubie. To jedyna
przewidywalna przeszkoda, która powtórzy się 24 razy.

## Execution plan

1. Wyprowadzić deklarację z nazw jobów publikowanych przez workflow repozytorium.
2. Raportować domyślnie; zapisywać tylko przy pełnej wyprowadzalności.
3. Rozesłać narzędzie adopterom przez `package-manifest.json`.

## Actual changes

- `scripts/generate_required_checks.py`: parser sekcji `jobs:` bez zależności
  od YAML, wykrywanie callerów reusable workflow, obsługa obu lokalizacji
  deklaracji (`governance/` w hubie, `.governance/` u adoptera), zachowanie
  `circularGovernanceChecksIgnoredByValidator`.
- `tests/required-checks.test.sh`: pięć przypadków na fixture repozytorium.
- `governance/package-manifest.json`: narzędzie jako managed
  `.governance/generate_required_checks.py`.

Dwa błędy własne wyłapane w trakcie, oba przez uruchomienie na prawdziwych
danych zamiast na fixture:

1. Pierwsza wersja brała klucze `pull_request`, `push`, `schedule` i
   `workflow_dispatch` za nazwy jobów, bo pod `on:` mają to samo wcięcie.
   Parser ogranicza się teraz do sekcji `jobs:`; test to pokrywa.
2. Druga wersja wypisywała `governance` jako nazwę checku dla jobów wołających
   reusable workflow. Prawdziwy kontekst to `<caller> / <callee job>`, czego z
   tego repozytorium wyprowadzić się nie da. Weryfikacja krzyżowa z rejestrem
   validatora potwierdziła to wprost: dla `logs` rejestr ma
   `governance / governance / enforce`.

Weryfikacja krzyżowa: 21 z 24 zarejestrowanych repozytoriów zgadza się z
rejestrem `subactor/validator-agent` przy zerowej wiedzy wspólnej. Trzy
rozjazdy to braki rejestru, nie błędy parsera.

## Blockers

- Naprawa deklaracji w każdym adopterze wymaga ticketu w tym adopterze; ten
  ticket dostarcza narzędzie, nie rollout.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion.
