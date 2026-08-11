# Ticket 051: Make adoption defaults portable and owned

- **ID**: ticket-051
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-11

## Cel i Zakres

Uczynić bazowy pakiet governance przenośnym dla bibliotek i narzędzi, które nie
używają Dockera. Domyślny manifest nie powinien wymagać `Dockerfile`, Compose
ani deklarować stacku `docker`; target może nadal jawnie rozszerzyć manifest i
włączyć te wymagania.

Jednocześnie uzupełnić ownership governance o zarządzane rootowe entrypointy
`project.sh`, `project.bat`, `scripts/runtime.sh` oraz konfigurację `goal.yaml`.
Obecnie pierwsza adopcja zastępująca taki plik nie może przypisać go do żadnego
workstreamu.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Polecenie użytkownika, aby poprawiać komplikacje znalezione na
  `glon`, stanowi bounded `SESSION_EXECUTION_AUTHORIZATION` dla tej zmiany.
- [ ] AC-02: Domyślny manifest nie wymaga Dockerfile/Compose i ma pustą listę
  stacków; schemat nadal pozwala targetowi włączyć Docker.
- [ ] AC-03: Wszystkie entrypointy zarządzane poza katalogiem `project/` oraz
  `goal.yaml` mają jednoznacznego właściciela w workstreamie governance.
- [ ] AC-04: Regresje manifestu wymagają portable default i kompletnego
  ownershipu, a pełny kontrakt Linux przechodzi.
- [ ] AC-05: Nie zmieniają się schematy, validator, package manifest,
  zależności, wersja ani wydanie; istniejące adopcje pozostają przypięte do
  wcześniejszego immutable manifestu.

## Ryzyka i Uwagi

- To zmiana publicznego defaultu przyszłej adopcji i powinna wejść w kolejnym
  immutable minor release; ten ticket nie wykonuje publikacji.
- Docker pozostaje w schema, stack profiles i walidatorze. Target wymagający
  kontenera dodaje `Dockerfile` do `requiredFiles`, ustawia `docker.required`
  oraz deklaruje stack `docker` we własnym rozszerzonym manifeście.
- Pilot `glon` pokazał koszt obowiązkowego defaultu: dwa nowe pliki, osobny
  workstream/ticket, duplikację wersji zależności oraz trzy testy wymagające
  dodatkowej semantyki zapisu w kontenerze.
- Przypisanie `goal.yaml` do governance nie zmienia jego treści ani nie dodaje
  go do pakietu; usuwa tylko dotychczasową lukę ownershipu.

## Autoryzacja

Dozwolone są lokalne zmiany i testy z tego intentu. Push, PR, merge, bump,
tagowanie i publikacja wymagają osobnej dyspozycji.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-051/`.
