# TODO Roadmap & Task Index

![Status: Active](https://img.shields.io/badge/Status-Active_Roadmap-blue.svg)

> Centralna lista zadań i kamieni milowych dla repozytorium **Governance & Onboarding Hub**.
> Etapy 1-4 poniżej są zakończonym planem historycznym. Aktywne zadania po
> wersji 0.9.0, wraz z kolejnością i kryteriami odbioru, znajdują się w
> [`docs/ROADMAP_AFTER_0.9.0.md`](docs/ROADMAP_AFTER_0.9.0.md).

## Aktywne utrzymanie standardu

- [x] [`ticket-105`](project/ticket-105/README.md) — publish integrated managed
  text hygiene as immutable `new-project 0.18.4`. Stan: `DONE / DONE`;
  workstream: `governance`; depends on `ticket-104`; PR #172 merged as
  `ecf0792c`, and tag/release `v0.18.4` point to the same commit.

- [x] [`ticket-104`](project/ticket-104/README.md) — reject trailing whitespace
  in every `managed` or `extendable` package source after the Platform adoption
  pilot found it in generated `AGENTS.md`. Stan: `DONE / DONE`; klasyfikacja:
  `BUG / P1 / regression`; workstream: `governance`; PR #170 merged as
  `fb318a6a` after exact-head Validator approval.

- [x] [`ticket-103`](project/ticket-103/README.md) — publish digest-bound
  managed target takeover as immutable `new-project 0.18.3`. Stan:
  `DONE / DONE`; workstream: `governance`; depends on `ticket-102`; PR #168
  merged as `04ced312`, then tag and release `v0.18.3` were published.

- [x] [`ticket-102`](project/ticket-102/README.md) — allow a changed,
  pre-existing target to enter managed ownership only through an exact-path,
  exact-base-digest declaration. Stan: `DONE / DONE`; klasyfikacja:
  `BUG / P1 / regression`; workstream: `governance`; found by Platform 0.18.2
  adoption pilot; PR #166 merged as `5cf4c869` after exact-head Validator approval.

- [x] [`ticket-101`](project/ticket-101/README.md) — opublikować zintegrowaną
  własność generated artifact receipt jako immutable `new-project 0.18.2`.
  Stan: `DONE / DONE`; klasyfikacja:
  `SERVICE / P1 / requested`; workstream: `governance`; zależy od
  `ticket-100`; PR #164 scalono jako `5c9aef93`, a tag i release `v0.18.2`
  opublikowano z tego dokładnego merge commit.

- [x] [`ticket-100`](project/ticket-100/README.md) — traktować dokładny,
  deterministycznie generowany `config/artifact-registry.json` jako governance
  carrier także w DONE closure, bez otwierania całego `config/**`. Stan:
  `DONE / DONE`; klasyfikacja: `BUG / P1 / regression`; workstream:
  `governance`; PR #162 scalono jako `73dba483` po exact-head Validator
  approval.

- [x] [`ticket-097`](project/ticket-097/README.md) — naprawiać istniejące
  instalacje, w których idempotentny installer pozostawił wywołanie worktree
  guard po terminalnym `exit 0`. Stan: `DONE / DONE`; klasyfikacja:
  `BUG / P1 / regression`; workstream: `governance`; zależy od `ticket-096`;
  PR #156 scalono jako `c34ab3bc` po exact-head Validator approval.

- [x] [`ticket-096`](project/ticket-096/README.md) — zachować wykonywalność
  worktree guard po złożeniu z istniejącym hookiem kończącym się `exit 0`.
  Stan: `DONE / DONE`; klasyfikacja: `BUG / P1 / regression`; workstream:
  `governance`; PR #154 scalono jako `e0148f79` po exact-head Validator
  approval.

- [x] [`ticket-095`](project/ticket-095/README.md) — audyt stosowania i
  egzekwowalności 15 standardów Wellmanifest, macierz dowodów oraz docelowy
  kontrakt naprawczy. Stan: `DONE / DONE`; klasyfikacja:
  `SERVICE / P1 / requested`; workstream: `governance`; PR #152 scalono jako
  `a0ea533e` po exact-head Validator approval.

- [ ] [`ticket-092`](project/ticket-092/README.md) — proaktywny
  `worktree-guard.yaml` (jak `pyqual.yaml`): fail-closed przy nachodzących
  zmianach w dwóch worktree tego samego repo. Stan: `IN_PROGRESS / EDIT`;
  klasyfikacja: `FEATURE / P1 / requested`; workstream: `governance`.

- [x] [`ticket-090`](project/ticket-090/README.md) — ten sam kontrakt
  `new-project` niezależnie od hosta LLM: `GEMINI.md`, `CLAUDE.md`,
  reguła Cursor, hook git i `scripts/install-agent-hosts.sh`. Stan:
  `DONE / DONE`; klasyfikacja: `FEATURE / P1 / requested`;
  workstream: `governance`.

- [x] [`ticket-085`](project/ticket-085/README.md) — ustanowić opcjonalny,
  deterministyczny kontrakt domenowy, w którym `operations/index.json` jest
  jedynym źródłem prawdy C/Q, a standardy CQRS obowiązkowo publikują katalogi
  `events/` i `error/`. Stan: `DONE / DONE`; klasyfikacja:
  `FEATURE / P1 / requested`; workstream: `governance`.

- [x] [`ticket-084`](project/ticket-084/README.md) — opublikować zintegrowaną
  poprawkę bezpiecznych markerów bootstrapu jako immutable
  `new-project 0.18.1`. Stan: `DONE / DONE`; klasyfikacja:
  `SERVICE / P1 / requested`; workstream: `governance`; zależy od
  `ticket-083`.

- [x] [`ticket-083`](project/ticket-083/README.md) — rozpoznać wyłącznie pełne
  markery bootstrapu `__GENERATE_[A-Z0-9_]+__` jako bezpieczne placeholdery,
  zachowując `GOV-SECRET-001` dla podobnych wartości i rzeczywistych tokenów.
  Stan: `DONE / DONE`; klasyfikacja: `BUG / P1 / regression`;
  workstream: `governance`.

- [x] [`ticket-080`](project/ticket-080/README.md) — adopted reviewed Policy DSL
  source conformance as integrated commit
  `50892fbec07dfaae90b74d219737f999d8409eed`. Managed package/runtime adoption
  remains the next bounded slice before release.

- [x] [`ticket-081`](project/ticket-081/README.md) — zintegrowano Policy DSL v1
  jako jawny standard `CONTRIBUTING VERSION 13`, digest-bound profil,
  kanoniczne selektory Markdown i regresję. Stan: `DONE / DONE`; managed
  package/runtime adoption pozostaje osobnym, ograniczonym zakresem.

- [x] [`ticket-079`](project/ticket-079/README.md) — opublikowano zintegrowany
  kontrakt HOME vs ADOPT jako immutable `new-project 0.18.0`. Stan:
  `DONE / DONE`; klasyfikacja: `SERVICE / P1 / requested`; workstream:
  `governance`; zależy od `ticket-078`. PR #122 przeszedł exact-head trusted
  approval i został scalony jako `769183ca`; finalny tag/release wskazuje ten
  sam merge SHA.

- [x] [`ticket-078`](project/ticket-078/README.md) — dodano opcjonalny kontrakt
  HOME vs ADOPT `placement` do intentów. Stan: `DONE / DONE`; klasyfikacja:
  `FEATURE / P1 / requested`; workstream: `governance`. PR #120 przeszedł
  Linux/Windows i exact-head Validator approval, a następnie został scalony
  jako `335b0f1975c4c9d3f2f99aeeeaba109a2cc41c2d`.

- [x] [`ticket-076`](project/ticket-076/README.md) — rozdzielić autoryzację
  uruchomienia chronionego procesu Validatora od exact-head trusted approval,
  usuwając ponowne pytanie o merge w już autoryzowanym zakresie. Stan:
  `DONE / DONE`; klasyfikacja: `BUG / P0 / requested`; workstream:
  `governance`. PR #118 otrzymał exact-head approval Validatora dla
  `85fc7d5...` i został scalony jako
  `0b4170a353fa30cb5857a4b3c97c6f0b2d2df5b0`.

- [x] [`ticket-075`](project/ticket-075/README.md) — opublikowano zintegrowane
  tryby repozytorium, warunkowy Docker i profile dostawy XS/S/M/L jako
  immutable `new-project 0.17.0`. Stan: `DONE / DONE`; klasyfikacja:
  `SERVICE / P0 / requested`; workstream: `governance`; zależy od
  `ticket-074`. PR #116 przeszedł exact-head Validator approval i został
  scalony jako `4d0a618`; finalny tag/release wskazuje ten sam merge SHA.

- [x] [`ticket-074`](project/ticket-074/README.md) — uzgodnić tryby standalone i
  monorepo, warunkowy Docker oraz profile dostawy XS/S/M/L w jednej
  deterministycznej projekcji; oddzielić status `IN_PROGRESS` od stanów
  workflow. Stan: `DONE / DONE`; klasyfikacja:
  `FEATURE / P1 / requested`; workstream: `governance`.
  PR #114 przeszedł exact-head Validator approval i został scalony jako
  `7ce09f1737f757c0e6d1fc4072b311d5453fd4f7`.

- [x] [`ticket-073`](project/ticket-073/README.md) — naprawiono projekcję
  remediation DSL tak, aby każda akcja była jednym atomowym rekordem todo2code,
  dodano byte-exact weryfikację deklarowanych plików i korelację analizy przez
  rekordy grafu bieżącej projekcji zamiast historycznych planów całego repo.
  Stan: `DONE / DONE`; PR #111 przeszedł Linux/Windows i exact-head Validator
  approval, został scalony jako `b50b581`, a post-merge CI jest zielone.
  Klasyfikacja: `BUG / P0 / regression`; workstream: `governance`; zależy od
  `ticket-067`.

- [x] [`ticket-072`](project/ticket-072/README.md) — opublikowano zintegrowany
  audyt osieroconych lokalnych branchy jako immutable `new-project 0.16.2`,
  używając Goal po exact-head Validator approval, identycznym drzewie merge i
  czystym reteście `main`; tag i finalny release wskazują `63a03d0c...`. Stan:
  `DONE / DONE`; klasyfikacja: `SERVICE / P1 / requested`; workstream:
  `governance`; zależy od `ticket-071`.

- [x] [`ticket-071`](project/ticket-071/README.md) — wykrywać pozostawione
  lokalne branche po usunięciu worktree, zachować aktywne dokładnie
  allowlistowane checkouty i nigdy nie usuwać unikalnych danych automatycznie.
  Stan: `DONE / DONE`; klasyfikacja: `BUG / P1 / regression`;
  workstream: `governance`.

- [x] [`ticket-070`](project/ticket-070/README.md) — skanonizowano quoting cron w
  zarządzanym workflow targetów, dodano regresję, opublikowano immutable 0.16.1 i
  potwierdzono upgrade żywego targetu przez Goal. Stan: `DONE / DONE`;
  klasyfikacja: `BUG / P1 / regression`; workstream: `governance`.

- [x] [`ticket-069`](project/ticket-069/README.md) — wydzielono i zwalidowano
  `git-lifecycle` i `ticket-lifecycle` jako wersjonowane podprojekty z
  zamkniętymi schema/GBNF oraz bezpieczną transakcją autonomicznego seed
  baseline. Stan: `DONE / DONE`; PR #108 przeszedł Linux/Windows, exact-head
  Validator approval i został scalony jako `5484605`; branch został usunięty.
  Oba moduły wydzielono równolegle do osobnych repozytoriów Wellmanifest. Klasyfikacja:
  `FEATURE / P1 / requested`; workstream: `governance`; zależy od zamknięcia
  publikacji ticketu 068.

- [x] [`ticket-068`](project/ticket-068/README.md) — naprawiono wygenerowany poza
  zakresem ticketu 065 `goal.yaml`, uruchamiać deterministyczną walidację na
  rzeczywistym diffie PR Governance Hub i opublikować DSL remediacji jako
  immutable `v0.16.0`. PR #100 scalono jako `6800f01`, post-merge Linux/Windows
  są zielone, a annotowany tag i finalny release wskazują ten sam SHA. Stan:
  `DONE / DONE`; klasyfikacja:
  `BUG / P1 / regression`; workstream: `governance`.

- [x] [`ticket-067`](project/ticket-067/README.md) — zdefiniowano target-owned
  DSL intencji naprawy z faktami, wykluczeniami false-positive, zależnościami,
  weryfikacją i bezpieczeństwem; dodać deterministyczny validator, brief dla
  LLM i hash-bound analizę todo2code. Pełny Linux contract przechodzi, a
  rzeczywisty todo2code wykrył drift priorytetu P1→P2 i dodał advisory hint.
  PR #98 przeszedł exact-head Validator App oraz Linux/Windows, został scalony
  jako `main@711766d`, a post-merge CI jest zielone. Stan: `DONE / DONE`;
  klasyfikacja: `FEATURE / P1 / requested`; workstream: `integration`.

- [x] [`ticket-065`](project/ticket-065/README.md) — usunąć bezwarunkowe
  `publicationStatus: published` z generatora, wymagać dokładnego annotowanego
  tagu i finalnego GitHub Release, a jawne fixture'y oznaczać jako
  `unpublished-test`; następnie opublikować pełny standard v0.15.0 i sprawdzić
  go przez publiczny Goal najpierw na glon. Stan: `DONE / DONE`;
  klasyfikacja: `BUG / P0 / regression`.

- [x] [`ticket-066`](project/ticket-066/README.md) — naprawiono ręczny bypass
  clone-wide alokacji oraz przedwczesne `DONE` po otwarciu PR; zdefiniowano
  kanoniczny katalog remediacji i kontrakt `error/*.md`, objęto wszystkie
  emitowane kody `GOV-*` deterministycznym audytem. PR #94 oraz post-merge
  Linux/Windows przeszły dla exact-head-approved payloadu. Stan:
  `DONE / DONE`; klasyfikacja: `BUG / P1 / regression`.

- [x] [`ticket-064`](project/ticket-064/README.md) — audyt workspace poprawnie
  reprezentuje unborn HEAD jako `null`, nadal wykrywa duplikaty pustych
  checkoutów i nie maskuje uszkodzonego HEAD. PR #92 oraz post-merge
  Linux/Windows przechodzą. Stan: `DONE / DONE`; klasyfikacja:
  `BUG / P1 / regression`.

- [x] [`ticket-063`](project/ticket-063/README.md) — lokalny lifecycle
  worktree/klonów ma read-only audyt z ochroną unikalnych danych, a pakiet
  adopcyjny instaluje rzeczywisty zdalny enforcement. PR #89 oraz post-merge
  Linux/Windows przechodzą, exact-head Validator GLM zatwierdza bez findings.
  Stan: `DONE / DONE`; klasyfikacja: `BUG / P1 / regression`.

- [x] [`ticket-060`](project/ticket-060/README.md) — własne workflow huba i
  reusable governance używają pełnych SHA oficjalnych akcji Node.js 24 bez
  zmiany kontraktu; downstream `twin` potwierdza rzeczywiste wykonanie bez
  adnotacji Node.js 20. Stan: `DONE / DONE`; klasyfikacja:
  `SERVICE / P1 / health`.

- [x] [`ticket-059`](project/ticket-059/README.md) — rootowy Compose jest
  markerem stosu Docker, a nested Dockerfiles nadal są wyliczane jawnie i
  kontrolowane. Pełny Linux contract przechodzi; pilot `mcp` nie ma już
  `GOV-STACK-001` i poprawnie ujawnia osobny dług pinowania. Stan:
  `DONE / DONE`; klasyfikacja: `BUG / P1 / regression`; bez publikacji.

- [x] [`ticket-058`](project/ticket-058/README.md) — istniejące rootowe
  `project.sh`/`.bat` są target-owned seedami, brakujące aliasy nadal powstają,
  a zarządzane `project/governance-check.*` pozostają kanoniczną bramą. Pełny
  Linux contract i exact-SHA pilot `hillm` przechodzą bez utraty automatyzacji.
  Stan: `DONE / DONE`; klasyfikacja: `BUG / P1 / regression`; bez publikacji.

- [x] [`ticket-057`](project/ticket-057/README.md) — przypisano obowiązkowy
  root `VERSION` do workstreamu `integration` także dla profilu stackless;
  dodatnia i ujemna granica własności, pełny Linux contract oraz Ruff
  przechodzą, a exact-SHA pilot `godot` uzyskał `GOV-PASS` bez Dockera i
  stosu językowego. Stan: `DONE / DONE`; klasyfikacja:
  `BUG / P1 / regression`; bez publikacji.

- [x] [`ticket-056`](project/ticket-056/README.md) — raportować podczas
  adopcji brakujące pliki bazowe należące do targetu po uwzględnieniu całego
  planu instalacji. Raport ma być deterministyczny i informacyjny, bez
  tworzenia plików, zmiany semantyki kodów wyjścia ani przejmowania własności
  nad targetem. Focused i pełny Linux contract oraz exact-SHA pilot `fixop`
  przez Goal przechodzą. Stan: `DONE / DONE`; klasyfikacja:
  `BUG / P1 / regression`; bez publikacji.

- [x] [`ticket-055`](project/ticket-055/README.md) — naprawiono domyślne
  wyznaczanie bazy dla wielocommitowej adopcji: przypięty walidator ma użyć
  `delivery.acceptedBaseSha` z jednego aktywnego ticketu adopcyjnego, zachowując
  pierwszeństwo jawnego `--base`. Stan: `IN_PROGRESS / EDIT`; klasyfikacja:
  `BUG / P1 / regression`; standardowy Linux contract i izolowany pilot
  `codot` przechodzą. Stan: `DONE / DONE`; bez publikacji.

- [x] [`ticket-054`](project/ticket-054/README.md) — doprecyzowano, że lokalny
  build pomija `image:`, natomiast `build:` z mutowalnym `image:` nadal może
  wykonać pull i pozostaje fail-closed; bez parsera YAML i nowego wyjątku.
  Stan: `DONE / DONE`; klasyfikacja:
  `BUG / P1 / requested`; zależy od lokalnego `ticket-052`.

- [x] [`ticket-053`](project/ticket-053/README.md) — usunięto 17 błędów Ruffa
  wprowadzanych przez zarządzany payload Pythona w żywej adopcji `code2docs`,
  zachowując semantykę validatora i poprawne tryby wykonywalne. Stan:
  `DONE / DONE`; klasyfikacja: `BUG / P1 / regression`.

- [x] [`ticket-052`](project/ticket-052/README.md) — pełne SHA-256 digesty są
  egzekwowane dla Dockerfile `FROM` i Compose `image:` w targetach z Docker
  opt-in.
  Stan: `DONE / DONE`; focused, traceability i full Linux contract przechodzą.

- [x] [`ticket-051`](project/ticket-051/README.md) — Docker jest opt-in w
  domyślnym manifeście, a ownership zarządzanych launcherów i `goal.yaml` jest
  kompletny. Stan: `DONE / DONE`; focused i full Linux contract przechodzą,
  bez external delivery.

- [x] [`ticket-049`](project/ticket-049/README.md) — obsłużono pierwszą,
  provenance-bound adopcję managed package bez bazowego locka, nie wyłączając
  z ownershipu plików targetu zastępowanych podczas bootstrapu. Stan:
  `DONE / DONE`; pełny Linux contract przechodzi, bez external delivery.

- [x] [`ticket-047`](project/ticket-047/README.md) — ujednolicono autonomiczny
  stan generowanych ticketów i opublikować pełną naprawę jako immutable
  `v0.14.1` wskazujące `main@63a3d56`. PR #75 przeszedł Linux, Windows i
  exact-head Validator; clean merge retest przeszedł. Stan: `DONE / DONE`; klasyfikacja:
  `SERVICE / P1 / requested`; zależy od `ticket-046`.

- [x] [`ticket-046`](project/ticket-046/README.md) — zmigrowano hash-locked legacy
  target manifest jako właściwą bazę kontraktu `extendable` oraz przyjmować
  jawne zlecenie wykonania/autonomii jako bounded session authorization bez
  ponownego pytania. PR #73 przeszedł Linux, Windows i exact-head Validator,
  a następnie został scalony jako `main@cc898c1`. Stan: `DONE / DONE`; klasyfikacja:
  `BUG / P1 / regression`.

- [x] [`ticket-045`](project/ticket-045/README.md) — ustanowiono zarządzaną
  publikację przez `goal -a` z jawnym trybem dostawy, feature probe oraz
  separacją publikacji implementacji od registry/release. PR #71 przeszedł
  Linux, Windows i exact-head Validator App, po czym został scalony jako
  `main@38fe787`. Stan: `DONE / DONE`; klasyfikacja:
  `FEATURE / P1 / requested`.

- [x] [`ticket-044`](project/ticket-044/README.md) — opublikowano scalony
  kontrakt `extendable` jako immutable minor `v0.14.0`, po pełnym Linux,
  Windows, exact-head Validator i czystym detached merge teście. Stan:
  `DONE / DONE`; PR #69 przeszedł Linux, Windows i exact-head Validator,
  a annotowany tag i GitHub Release `v0.14.0` wskazują dokładny, ponownie
  przetestowany merge `a22eb47`. Klasyfikacja: `SERVICE / P1 / requested`.

- [x] [`ticket-043`](project/ticket-043/README.md) — opublikowano naprawę z
  ticketu 042 jako immutable patch v0.13.2 dla downstream exact-SHA adoption.
  PR #64 przeszedł Linux, Windows i exact-head Validator; annotowany tag oraz
  GitHub Release wskazują `85631ea`, a downstream todo2code PR #70 przeszedł
  chronioną adopcję. Stan: `DONE / DONE`; klasyfikacja:
  `SERVICE / P0 / regression`.

- [x] [`ticket-042`](project/ticket-042/README.md) — naprawiono regresję P0 w
  chronionym snapshotcie lifecycle: typed GraphQL ma dostarczać rzeczywisty
  boolean `deleteBranchOnMerge` bez osłabiania deterministycznego walidatora.
  PR #62 przeszedł Linux, Windows i exact-head Validator; wydanie v0.13.2
  wskazuje `85631ea`, a downstream todo2code PR #70 przeszedł chronioną
  walidację i został scalony jako `f60d3cc`. Stan: `DONE / DONE`;
  klasyfikacja: `BUG / P0 / regression`.

- [x] [`ticket-041`](project/ticket-041/README.md) — opublikowano
  behavior-preserving repair z ticketu 040 jako immutable patch `v0.13.1` dla
  downstream exact-SHA adoption. Linux, Windows, exact-head Validator, czysty
  merge checkout i Vallm przeszły; Release wskazuje `7979cfe`. Stan:
  `DONE / DONE`;
  klasyfikacja: `SERVICE / P1 / health`.
- [x] [`ticket-040`](project/ticket-040/README.md) — obniżono pięć
  pre-existing punktów złożoności w zarządzanych źródłach Pythona bez
  wyłączania downstream review ani zmiany zachowania. Linux, Windows i
  exact-head Validator przeszły; PR #58 scalono jako `main@efec2cf`. Stan:
  `DONE / DONE`; klasyfikacja: `SERVICE / P1 / health`.
- [x] [`ticket-039`](project/ticket-039/README.md) — opublikowano atomowy
  kontrakt adopcji jako immutable `v0.13.0`. PR #56 przeszedł Linux, Windows i
  exact-head Validator; czysty merge `12158ef` przeszedł pełny Linux contract,
  a annotowany tag i GitHub Release wskazują ten SHA. Stan: `DONE / DONE`;
  klasyfikacja: `SERVICE / P2 / health`.
- [x] [`ticket-038`](project/ticket-038/README.md) — wdrożono jawny,
  provenance-bound kontrakt atomowej adopcji, który rozlicza wyłącznie
  zweryfikowany zbiór `managed`, pozostawiając seed, lock i target-local diff
  pod zwykłym budżetem, ownership i protected approval. PR #54 przeszedł Linux,
  Windows i exact-head Validator, po czym został scalony jako `main@1aa2600`.
  Stan: `DONE / DONE`; klasyfikacja: `FEATURE / P1 / requested`.
- [x] [`ticket-036`](project/ticket-036/README.md) — przypisano dokładne ścieżki
  `CHANGELOG.md` i `.env.example` do domyślnego workstreamu governance oraz
  dodano regresje własności i adopcji. PR #50 przeszedł Linux, Windows i
  exact-head Validator App, po czym został scalony jako `main@450a362`. Stan:
  `DONE / DONE`; klasyfikacja: `FEATURE / P1 / requested`.
- [x] [`ticket-037`](project/ticket-037/README.md) — opublikowano własność z
  ticketu 036 jako immutable `0.12.0`. PR #52 przeszedł Linux, Windows i
  exact-head Validator; czysty merge SHA `7be2e26` przeszedł pełny kontrakt,
  a annotowany tag i GitHub Release wskazują ten SHA. Stan: `DONE / DONE`;
  klasyfikacja: `SERVICE / P2 / health`.
- [x] [`ticket-035`](project/ticket-035/README.md) — GOV-DECISION gate w governance_check.
- [x] [`ticket-032`](project/ticket-032/README.md) — DECISION DSL + append decisions.md (validator #13/#14).
- [x] [`ticket-033`](project/ticket-033/README.md) — required checks z pliku head (validator #13). DONE.
- [x] [`ticket-034`](project/ticket-034/README.md) — kompletne mapowanie rule-enforcement (148/37, 0 luk).
- [x] [`ticket-027`](project/ticket-027/README.md) — rule-enforcement traceability. `DONE` (PR #37).
- [x] [`ticket-025`](project/ticket-025/README.md) — CI runs governance-env suite + completeness guard (PR #34).
- [x] [`ticket-030`](project/ticket-030/README.md) — single source required check names. `DONE` (PR #42).
  wymaganych checków (`governance/required-checks.json`) + bramka vs
  `ci.yml`. Stan: `IN_PROGRESS / VALIDATION` (impl on PR).
- [x] [`ticket-031`](project/ticket-031/README.md) — recomputable decision log contract. `DONE` (PR #44).
  (`C-DECISION-*`, schema, replay). Stan: `PLAN` → implementacja po 030.
- [x] [`ticket-024`](project/ticket-024/README.md) — strategia
  `extendable` w `package-manifest.json`: zarządzana baza JSON i targetowy
  manifest rozszerzany bez ręcznej edycji locka. Potwierdzony downstream:
  własność `test/python-runtime.test.ts` w `semcod/todo2code`. Stan:
  `DONE / DONE`; PR #67 przeszedł Linux, Windows i exact-head Validator, po
  czym został scalony jako `main@2fbf23f`. Klasyfikacja:
  `FEATURE / P1 / requested`.
- [x] [`ticket-022`](project/ticket-022/README.md) — kanoniczny Change
  Evaluation Contract oraz deterministyczny runtime TypeScript uruchamiany
  przez Bash. Stan: `DONE / DONE`; PR #31 scalony jako `166ebea` po Linux,
  Windows i exact-head Validator App approval. Klasyfikacja:
  `FEATURE / P1 / requested`.

- [x] [`ticket-006`](project/ticket-006/README.md) — zsynchronizowano roadmapę,
  TODO i indeks z wersją 0.10.0 oraz utworzono bounded backlog. Stan:
  `DONE / DONE`; PR #6 przeszedł CI, exact-head approval i został scalony.

- [x] [`ticket-007`](project/ticket-007/README.md) — opublikowano immutable
  `v0.10.0` i GitHub Release dla pełnego SHA
  `62ffb0dac1dba9294aa825ca5cc0344fefb33b0d`. Stan: `DONE / DONE`; PR #8,
  exact-head approval i czyste testy zakończone.

- [ ] [`ticket-008`](project/ticket-008/README.md) — pilot adopcji przez `goal`
  w pojedynczym workstreamie. Stan: `BACKLOG`; zależy od 002 i 007.

- [ ] [`ticket-009`](project/ticket-009/README.md) — pilot równoległych agentów
  i exact-head Validator App. Stan: `BACKLOG`; zależy od 002, 007 i 008.

- [x] [`ticket-010`](project/ticket-010/README.md) — opublikowano wersjonowany
  manifest pakietu i meta-walidację schematów. Stan: `DONE / DONE`; PR #10
  przeszedł CI i exact-head approval, po czym został scalony jako
  `main@956f350`.

- [x] [`ticket-011`](project/ticket-011/README.md) — natywne Windows CI dla
  wrapperów i generatora. Stan: `DONE / DONE`; PR #11 przeszedł Linux/Windows
  CI i exact-head approval, a ruleset `main` wymaga `windows-governance`.

- [ ] [`ticket-012`](project/ticket-012/README.md) — test upgrade/rollback
  między rzeczywistymi wydaniami. Stan: `BACKLOG`; zależy od 007 i 010.

- [ ] [`ticket-013`](project/ticket-013/README.md) — runbook Validator App i
  OpenRouter z diagramami, rotacją i diagnostyką. Stan: `BACKLOG`; zależy od
  007 i 009.

- [x] [`ticket-014`](project/ticket-014/README.md) — kanoniczny DSL
  `BUG > FEATURE > SERVICE`, osobny priorytet `P0–P3`, diff-aware CC i pakiet
  adopcyjny. Stan: `DONE / DONE`; PR #13 scalony jako `main@f7e0fd1`.

- [x] [`ticket-015`](project/ticket-015/README.md) — immutable wydanie 0.11.0
  zawierające manifest pakietu i DSL klasyfikacji. Stan:
  `DONE / DONE`; release SHA `cc9b046`, annotowany tag i GitHub Release
  `v0.11.0` opublikowane po czystej walidacji.

- [x] [`ticket-016`](project/ticket-016/README.md) — runtime enforcement
  klasyfikacji `BUG/FEATURE/SERVICE` przez `intent/v3`. Stan:
  `DONE / DONE`; PR #17 scalony do `main` jako `c02962b` po aktualnym approval
  i zielonych testach.

- [x] [`ticket-017`](project/ticket-017/README.md) — domknięcie lifecycle
  krótkotrwałych branchy ticketowych po merge/close. Stan: `DONE / DONE`; PR
  #20 scalono jako `d3240c0` po zielonym CI i exact-head approval, a branch
  implementacyjny został usunięty.
- [x] [`ticket-021`](project/ticket-021/README.md) — intent/v3, ref-aware allocation,
  clone-wide reservation i ochrona przed wieloma writerami w jednym worktree.

- [x] [`ticket-018`](project/ticket-018/README.md) — deterministyczny audyt
  ustawienia auto-delete i własności branchy przez otwarte PR-y. Stan:
  `DONE / DONE`; PR #24 przeszedł Linux/Windows CI, exact-head approval i merge.

- [ ] [`ticket-005`](project/ticket-005/README.md) — implementacja uszczelnienia
  evidence została scalona w PR #4. Stan: `BLOCKED / BLOCKED`; czeka na
  immutable release 0.10.0 i adopcję jego SHA w `todo2code`.

- [x] [`ticket-004`](project/ticket-004/README.md) — pogodzić dwa rozbieżne
  kontrakty 0.9.0 w kanoniczny 0.10.0, zachowując bounded delivery i zwalniając
  rezerwacje dla `PLAN/BLOCKED`. Stan: `DONE / DONE`; kolizję ID
  usunięto jako `ticket-004`, połączono `main@c54694a`, a wskazany przez
  Validator App helper naprawiono, przetestowano i zatwierdzono dla exact HEAD.
  Zależny `todo2code` używa lokalnie `z-ai/glm-5.2`.

- [x] [`ticket-001`](project/ticket-001/README.md) — ujednolicenie zasad
  edytowalnego utrzymania `wellmanifest/new-project`.
- [ ] [`ticket-002`](project/ticket-002/README.md) — integracja bezpiecznej
  adopcji manifestu z `goal`. Stan: `BLOCKED / BLOCKED`; implementacja lokalna
  czeka na opublikowany pełny SHA standardu.
- [x] [`ticket-003`](project/ticket-003/README.md) — zaufana walidacja PR przez
  allowlistowaną GitHub App lub zweryfikowaną atestację.

---

## 📌 Etap 1: Przebudowa Przewodnika i Kolejności Plików w `README.md`

- [x] **Wytyczne i Specyfikacja w `README.md`**:
  - [x] Wyszczególnienie sekcji "Co z czego wynika" w czytelnych punktach i podpunktach.
  - [x] Zdefiniowanie ról plików: `user-{github_username}.md` (tworzony na żądanie z nazwy użytkownika GitHub), `preprompt.md` (techniczne wskazania i zasoby ticketu), `ai-{PROVIDER}.md` (MÓZG AI), `ai-{PROVIDER}-logs.txt` (dedykowane logi CLI) oraz `changelog.md` (lokalny rejestr zmian ticketu).
  - [x] Dodanie narzędzia `todo2code` (`https://github.com/semcod/todo2code`) do skryptów deweloperskich `project.sh` i `project.bat` oraz tabeli narzędzi.

---

## 📂 Etap 2: Uniwersalne Skrypty Automatyzujące i Wzorzec `project/`

- [x] **Stworzenie Wzorca `template/files/project.template.md` oraz `project/README.md`**:
  - [x] Stworzono szablon `project.template.md` w `template/files/` wg standardu `*.template.md`.
  - [x] Opisano przeznaczenie folderu `project/` z odnośnikami do dokumentacji `wellmanifest/new-project` i indeksem ticketów.
- [x] **Stworzenie Uniwersalnego Skryptu `project/new-ticket.sh`**:
  - [x] Automatyczne numerowanie i tworzenie katalogu `project/ticket-{NNN}/`.
  - [x] Inicjalizacja w ticketze plików `preprompt.md` (techniczne wytyczne i podlinkowane zasoby) oraz `changelog.md` (lokalny changelog).
  - [x] Automatyczne wywołanie `./project/readme.sh`.
- [x] **Stworzenie Uniwersalnego Skryptu `project/readme.sh`**:
  - [x] Skanowanie ticketów i automatyczna regeneracja tabeli menu w `project/README.md`.
- [x] **Uaktualnienie Reguł DSL (`C-TOOLS-006` w `CONTRIBUTING.md`)**:
  - [x] Nakaz kopiowania gotowych skryptów z huba zamiast ich ponownego generowania z braku tokenów.
- [x] **Wprowadzenie Reguły Kontynuacji Ticketu (`P-CORE-009` / `C-TICKET-008`)**:
  - [x] Zakaz tworzenia nowych ticketów dla kolejnych promptów w ramach tego samego zadania.
  - [x] Zakaz modyfikowania notatek człowieka `user-{github_username}.md` przez Agenta AI.

---

## 📝 Etap 3: Wzorzec Techniczny `preprompt.template.md` i Wytyczne

- [x] **Przygotowanie Wzorca Technicznego w `template/files/preprompt.template.md`**:
  - [x] Stworzono w `template/files/preprompt.template.md` znormalizowany szablon dyrektyw technicznych ticketu (z polami na ograniczenia inżynieryjne, podlinkowaną specyfikację oraz twarde wymagania techniczne).
  - [x] Zaktualizowano skrypt `project/new-ticket.sh`, aby używał szablonu `template/files/preprompt.template.md` przy generowaniu ticketu.
  - [x] Udokumentowano rolę `preprompt.md` w `template/files/README.md` oraz w plikach zasad zarządczych.

---

## 📚 Etap 4: Obowiązek Tworzenia Diagramów Wizualnych w `docs/` Target Repozytorium

- [x] **Wprowadzenie Reguły Generowania Diagramów (`P-DOCS-001` & `C-DOCS-001`)**:
  - [x] Dodano regułę `P-DOCS-001` w `POLICY.md` oraz `C-DOCS-001` w `CONTRIBUTING.md` zobowiązującą Agentów AI do tworzenia wizualnych diagramów (Mermaid/Markdown) w katalogu `docs/` każdego docelowego repozytorium (np. `docs/ARCHITECTURE.md`, `docs/LOGIC_FLOW.md`).
  - [x] Zaktualizowano instrukcje dla agentów w `AGENTS.md` oraz w przewodniku `README.md`.

---

## 🔒 Etap 5: Egzekwowalny kontrakt host-agnostyczny (ticket-106)

Opublikowane jako `#174`, merge `1dff15b`. Slice'y zależne pozostają otwarte.

- [x] **Warstwa kontrolna kontraktu hostów (`GOV-AGENT-HOST-004..006`)**:
  - [x] Zadeklarowano hosty, hooka i bindingi pakietowe w `governance/agent-hosts.json` wraz ze schematem.
  - [x] Dodano `scripts/agent_host_check.py` i wpięto go w `scripts/governance_check.py`, więc brama wykrywa nieaktywny `core.hooksPath`, brakujący plik hosta i hooka bez bitu wykonywalności.
  - [x] Rozszerzono `scripts/audit_diagnostics.py` o katalog `.githooks`; zarejestrowano `GOV-AGENT-HOST-001..003` emitowane przez hooka.
- [x] **Punkty styku z paczkami (`GOV-PACKAGING-001..003`)**:
  - [x] Walidator czyta `[tool.wellmanifest]` z `pyproject.toml` i klucz `wellmanifest` z `package.json`, porównuje wersję i rewizję z `manifest.lock.json` i wymaga lifecycle bindingu (`scripts.prepare`, `pytest addopts`).
  - [x] Runbooki `error/GOV-AGENT-HOST.md` i `error/GOV-PACKAGING.md` opisują dokładną remediację.
- [x] **Dystrybucja kontraktu do adopterów** (ticket-107, `#176`, merge `9328b7e`):
  - [x] `governance/package-manifest.json` rozsyła `CLAUDE.md`, `GEMINI.md`, regułę Cursora, `.githooks/pre-commit` oraz sam kontrakt i walidator jako managed.
  - [x] `scripts/install-agent-hosts.sh` aktywuje kontrakt w miejscu zamiast kopiować plik na samego siebie; bootstrap dostarcza również kontrakt.
  - [ ] Hosty `aider` i `copilot` przeniesione do slice'u CI (nie mieściły się w budżecie dziewięciu plików).
- [x] **Egzekucja w CI** (ticket-108):
  - [x] Job `governance / enforce` w `template/files/new-project-governance.workflow.yml` uruchamia `governance_check.py`; zmierzono, że brama przechodzi w 24 z 25 adopterów.
  - [x] `audit_diagnostics.py` skanuje `.githooks`, a `audit_rule_enforcement.py` zna `agent_host_check.py`; reguły `C-HOST-001..003` mapują sześć kodów.
  - [x] Źródło standardu zmergowane jako PR `#178` po exact-head approval
        `5001242554`; merge `5aefa91`.
  - [ ] Wymaganie `governance / enforce` w rulesetach adopterów — decyzja poza repozytorium.
  - [ ] `required-checks.json` generowany per repozytorium zamiast kopii huba (blokuje krok required-checks w jobie).

- [ ] **Publikacja adoptowalnego wydania 0.18.5** (ticket-109):
  - [ ] Zaktualizować mechaniczne nośniki wersji i aktywne asercje.
  - [ ] Przejść pełny kontrakt testowy i exact-head Validator merge.
  - [ ] Opublikować niezmienne `v0.18.5` z ponownie przetestowanego merge SHA.
