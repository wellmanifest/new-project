---
participant-id: agent:claude
participant: claude
role: agent
ticket: ticket-114
---
# Participant: claude (AI agent)

## Understanding

Narzędzie powstało jako analiza podczas serii 106–113 i było uruchamiane na
prawdziwej flocie przez cały ten czas. Ten ticket przenosi je do huba, bo bez
tego istnieje tylko w katalogu roboczym sesji.

Wartość jest w zestawieniu dwóch liczb obok siebie: zero driftu digestów przy
806 kopiach i mediana sześciu wydań w tyle. Osobno pierwsza wygląda jak sukces,
a druga jak zaniedbanie. Razem opisują dokładnie to, co ten standard robi
dobrze i czego nie robi wcale.

## Execution plan

1. Wnieść skrypt bez zmian merytorycznych, poza usunięciem zaszytej ścieżki.
2. Napisać test na syntetycznym workspace, żeby CI weryfikowało logikę bez
   dostępu do floty.
3. Podpiąć zestaw w `ci.yml`, czego wymaga własna asercja tego workflow.

## Actual changes

- `scripts/fleet_report.py`: read-only, bez zależności; trzy tryby (tabela,
  JSON, `--max-releases-behind` jako brama). Ścieżka do rejestru validatora
  stała się opcją `--validator-registry` zamiast zaszytego `Path.home()`.
- `tests/fleet-report.test.sh`: syntetyczny workspace z hubem i dwoma
  adopterami; pokrywa liczenie wydań wstecz, drift digestu po edycji pliku
  managed, stan `claimed but not pinned` i obie strony bramy progowej.
- `.github/workflows/ci.yml`: nowy krok.

Uwaga o wzorcu: `ci.yml` ma już asercję sprawdzającą, że każdy `tests/*.test.sh`
jest podpięty. To jedyna lista w tym repozytorium, która wyprowadza się ze
źródła zamiast być utrzymywana ręcznie, i zadziałała — dodanie pliku testu bez
kroku zepsułoby CI. Warto to mieć na uwadze przy pozostałych listach.

## Blockers

- None inside the recorded intent.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion.
