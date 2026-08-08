# Ticket 036: Own root release and environment contracts

- **ID**: ticket-036
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: WAIT_FOR_APPROVAL
- **Utworzono**: 2026-08-08

## Cel i zakres

Przypisać dwa dokładne kontrakty główne, `CHANGELOG.md` i `.env.example`, do
domyślnego workstreamu `governance`. Pierwszy jest audytowalnym zapisem
wydania, drugi jest przeglądanym, niesekretnym kontraktem konfiguracji.

Zmiana dotyczy wyłącznie domyślnego manifestu standardu i regresji. Nie zmienia
znaczenia immutable `v0.11.0`: po scaleniu ticketu 036 osobny, zależny ticket
wydania podniesie wersję, przetestuje czysty checkout i opublikuje nowy tag.

## Kryteria odbioru

- [ ] AC-01: `governance/manifest.default.json` przypisuje dokładnie
  `CHANGELOG.md` i `.env.example` do workstreamu `governance`.
- [ ] AC-02: Manifest pozostaje zgodny ze schematem, a deklaracje workstreamów
  pozostają bez niejednoznacznego nakładania.
- [ ] AC-03: Fixture aktywnego ticketu governance może legalnie zadeklarować i
  zmienić każdy z dwóch kontraktów.
- [ ] AC-04: Fixture innego workstreamu deklarującego którykolwiek kontrakt
  kończy się stabilnym `GOV-WORKSTREAM-003`.
- [ ] AC-05: Test adopcji potwierdza, że świeży target otrzymuje oba wpisy w
  zasianym manifeście.

## Ryzyka i mitygacje

- Dokładne ścieżki, bez globów, ograniczają rozszerzenie odpowiedzialności.
- `.env.example` pozostaje plikiem niesekretnym; `.env` i sekrety pozostają
  zabronione.
- Istniejące, dostosowane manifesty nie są nadpisywane automatycznie. Każdy
  target przyjmie tę własność w osobnym, przejrzanym procesie adopcji.
- Nowy tag powstanie dopiero z chronionego `main`; istniejące tagi nie będą
  przesuwane ani nadpisywane.

## Poza zakresem

- Brak zmian w runtime walidatora i algorytmie dopasowania globów.
- Brak zmian w repozytoriach docelowych, w tym `semcod/todo2code`.
- Brak podniesienia `VERSION`, edycji głównego changeloga lub publikacji taga w
  tym ticketcie.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-036/`.
