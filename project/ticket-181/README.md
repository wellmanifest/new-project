# Ticket 181: Allow digest-bound target-owned adoption transitions

- **ID**: ticket-181
- **Owner**: requesting user, represented by the conversation
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-01

## Cel i zakres

Usunąć deadlock ujawniony przez adopcję DSL: target-owned workflow musi
zmienić swój parser kontraktu w tej samej transakcji co standard, lecz nie jest
plikiem zarządzanym przez paczkę. Adopcja może objąć taki plik wyłącznie przez
jawny wpis z dokładną ścieżką oraz SHA-256 treści bazowej i docelowej.

Mechanizm jest ograniczony do wzorców target-owned zadeklarowanych w
zarządzanym rejestrze adoption bindings. Deklaracja nieużyta, nakładająca się
na managed takeover/restoration, nieobecna w bazie lub niezgodna z którymkolwiek
digestem ma pozostać fail-closed.

## Kryteria odbioru

- [x] AC-01: `standardAdoption.targetOwnedTransitions` akceptuje tylko
  unikalne exact paths z poprawnymi `baseDigest` i `headDigest`.
- [x] AC-02: Walidator zwalnia z ownership/scope wyłącznie plik, którego baza
  i head są byte-exact zgodne z deklaracją oraz z zarządzanym allowlistem.
- [x] AC-03: Testy odrzucają brakujący, niezmieniony, nieallowlistowany,
  nakładający się, błędnie hashowany i nieużyty transition.
- [x] AC-04: Pełne testy POSIX, test adopcji Worktrees oraz exact-range
  governance przechodzą, a materialna zmiana publikuje `new-project 0.20.3`.
- [ ] AC-05: Chroniony Validator scala PR i issue #290 zostaje zamknięte.

## Ryzyka i uwagi

- Ryzyko zbyt szerokiego bypassu ogranicza zarządzany allowlist ścieżek,
  podwójny digest i wymóg jednokrotnego zużycia deklaracji.
- Mechanizm nie pozwala na tworzenie ani usuwanie plików target-owned i nie
  zmienia zasad managed takeover/restoration.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-181/`.
