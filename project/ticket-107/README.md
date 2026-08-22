# Ticket 107: Distribute the host contract to adopters

- **ID**: ticket-107
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-22

## Cel i Zakres

`ticket-106` dał deterministyczną kontrolę kontraktu host-agnostycznego, ale
kontrakt istniał tylko w hubie. Adopterzy dostawali `AGENTS.md` jako plik
managed z digestem, a `CLAUDE.md`, `GEMINI.md`, regułę Cursora i
`.githooks/pre-commit` — wcale. Reguła 22 obiecywała je od `ticket-090`, który
świadomie nie ruszał `package-manifest.json`.

Ten ticket dopisuje pliki hostów do kanału dystrybucji, który już działa dla
`AGENTS.md`. Dzięki temu `GOV-SYNC-001` pilnuje ich digestów u wszystkich 25
adopterów bez nowego mechanizmu. Dochodzi host `aider`, bo `.aider.conf.yml`
z kluczem `read:` ładuje `AGENTS.md` i `CLAUDE.md` do każdej sesji, a
`auto-commits: false` nie pozwala narzędziu commitować poza hookiem.

Instalator przestaje być listą plików wpisaną na sztywno: czyta kontrakt i
`package-manifest.json`, i rozróżnia dwie operacje. Aktywacja w miejscu
weryfikuje pliki, nadaje hookowi bit wykonywalności i ustawia `core.hooksPath`.
Bootstrap do innego checkoutu kopiuje pliki z huba. To naprawia defekt, który
utrzymywał `core.hooksPath` nieustawiony wszędzie: stary skrypt robił `cp -f`
z pliku na ten sam plik i przewracał się na „same file", więc żadne
repozytorium nie mogło zainstalować własnego kontraktu.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `bash tests/agent-hosts.test.sh` — bootstrap do świeżego klonu
  dostarcza każdy zadeklarowany plik hosta oraz sam kontrakt i ustawia
  `core.hooksPath`; fixture wyprowadza listę hostów z `agent-hosts.json`, więc
  dodanie hosta nie może go po cichu wyprzedzić.
- [x] AC-02: `bash tests/adoption-lock.test.sh` — adopcja rozwiązuje każde nowe
  źródło z `package-manifest.json` i zapisuje jego digest w locku.
- [x] AC-03: `./scripts/install-agent-hosts.sh --check` w klonie huba raportuje
  aktywny kontrakt zamiast przewracać się na kopiowaniu pliku na siebie.
- [x] AC-04: `./project/governance-check.sh --actor agent` kończy się `GOV-PASS`.

## Ryzyka i Uwagi

- Risk 1: adopter, który wykona upgrade, dostanie `.governance/agent-hosts.json`
  i od tej chwili jego brama wymaga wszystkich plików hostów. Mitigacja: pliki
  przychodzą tą samą transakcją adopcyjną, więc kontrakt i jego przedmiot nigdy
  nie rozjeżdżają się w czasie.
- Risk 2: `.aider.conf.yml` ustawia `auto-commits: false`, co zmienia domyślne
  zachowanie aidera w każdym adopterze. To jest zamierzone — commit ma
  przechodzić przez hooka, nie obok niego.
- Risk 3: host `copilot` nie zmieścił się w budżecie dziewięciu plików i
  przechodzi do slice'u CI razem z rozszerzeniem audytu diagnostyk.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-107/`.
