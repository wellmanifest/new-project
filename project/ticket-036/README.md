# Ticket 036: Own root release and environment contracts

- **ID**: ticket-036
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-08

## Cel i zakres

Przypisać dwa dokładne kontrakty główne, `CHANGELOG.md` i `.env.example`, do
domyślnego workstreamu `governance`. Pierwszy jest audytowalnym zapisem
wydania, drugi jest przeglądanym, niesekretnym kontraktem konfiguracji.

Zmiana dotyczy wyłącznie domyślnego manifestu standardu i regresji. Nie zmienia
znaczenia immutable `v0.11.0`: po scaleniu ticketu 036 osobny, zależny ticket
wydania podniesie wersję, przetestuje czysty checkout i opublikuje nowy tag.

## Kryteria odbioru

- [x] AC-01: `governance/manifest.default.json` przypisuje dokładnie
  `CHANGELOG.md` i `.env.example` do workstreamu `governance`.
- [x] AC-02: Manifest pozostaje zgodny ze schematem, a deklaracje workstreamów
  pozostają bez niejednoznacznego nakładania.
- [x] AC-03: Fixture aktywnego ticketu governance może legalnie zadeklarować i
  zmienić każdy z dwóch kontraktów.
- [x] AC-04: Fixture innego workstreamu deklarującego którykolwiek kontrakt
  kończy się stabilnym `GOV-WORKSTREAM-003`.
- [x] AC-05: Test adopcji potwierdza, że świeży target otrzymuje oba wpisy w
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

## Zatwierdzenie interaktywne

Użytkownik poleceniem „kontynuuj” 2026-08-08 zatwierdził przedstawiony plan i
`intent.json`. Zgoda obejmuje implementację ticketu 036, ale nie jest zaufanym
dowodem merge.

## Walidacja

- Pełny kontrakt Linux CI huba: PASS.
- `governance-validator.test.sh`: PASS, w tym pozytywne i negatywne fixture'y
  nowych ścieżek.
- `adoption-lock.test.sh`: PASS, w tym asercje zasianego manifestu.
- Składnia JSON i `git diff --check`: PASS.
- Windows pozostaje wymaganym chronionym checkiem PR i nie był uruchamiany
  lokalnie na hoście Linux.

## Publikacja

- PR #50: scalony do chronionego `main` jako
  `450a36272f2552bb92df99c4f49c00f3618260e9`.
- Exact-head Validator App: APPROVED dla
  `367f588c2fda5404e7da2ae6db641a47159f956b`.
- Chronione checki `test` i `windows-governance`: PASS.
- Branch implementacyjny został usunięty po merge.
