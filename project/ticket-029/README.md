# Ticket 029: Decide whether a trusted app review may also perform the merge

- **ID**: ticket-029
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: WAIT_FOR_APPROVAL
- **Utworzono**: 2026-08-06

## Cel i Zakres

Ticket rozstrzygnięcia, nie implementacji. Odpowiada na jedno pytanie: jakie
dowody musi nieść merge wykonany przez tożsamość, która wystawiła zaufane
zatwierdzenie.

Stan faktyczny, zweryfikowany 2026-08-06:

| warstwa | stan |
|---|---|
| ruleset `main-governance-protection` | `bypass_actors: []`; brak reguły ograniczającej, kto merguje |
| instalacja `ifuri-validator-agent` na `wellmanifest` | `contents: write`, `pull_requests: write` — technicznie potrafi |
| `P-CORE-015` | dopuszcza `github-app-review` jako zaufane zatwierdzenie; milczy o tym, kto merguje |
| `P-CORE-016` | `FORBID REQUIRED_MERGE_DECISION_FROM_LLM_OUTPUT` — decyzja musi być deterministyczna |
| kod `validator-agent`, ścieżka `direct-pr` | brak wywołania merge; approval kończy się zdaniem „Merge was not requested or performed" |

Dziś obowiązuje układ: bot zatwierdza, człowiek merguje. Nie wynika on z żadnej
reguły — wynika z braku implementacji. Ten ticket wymaga, żeby stał się
świadomą decyzją zapisaną w `POLICY.md`, w jedną albo w drugą stronę.

## Czego ten ticket NIE rozstrzyga

Wcześniejsza wersja tego opisu twierdziła, że automatyczny merge rozbraja
`required_approving_review_count: 1` jako kontrolę dwóch stron, bo approval
i merge należałyby do tej samej tożsamości. **To było błędne** i zostało
usunięte. Kontrola dwóch stron dotyczy relacji autor–zatwierdzający, nie
zatwierdzający–mergujący, i jest spełniona w obu scenariuszach:

| scenariusz | autor | zatwierdzający |
|---|---|---|
| potok agentowy w `if-uri` | App `repair-agent`, instalacja `147750504` | App `ifuri-validator-agent`, instalacja `151226354` |
| `wellmanifest/new-project` | człowiek — wszystkie otwarte PR-y od `tom-sapletta-com` | App `ifuri-validator-agent`, instalacja `151239784` |

Rozdział tożsamości jest realny, nie nominalny: osobne aplikacje GitHub, osobne
`REPAIR_APP_CLIENT_ID` i `VALIDATOR_APP_CLIENT_ID`, osobne klucze prywatne.
Dodatkowo `direct_validation.py:188` odrzuca recenzję, gdy recenzent jest
autorem. Merge wykonany przez zatwierdzającego niczego tu nie zabiera.

Odnotowana asymetria: `repair-agent` **nie jest zainstalowany** na
`wellmanifest`. W tym repozytorium parą jest więc człowiek plus walidator, a nie
dwa boty.

Nie jest też przedmiotem sporu jakość samej walidacji. Bramka intencji jest
deterministyczna z założenia — `deterministic_gate: required`,
`semantic_finding_authority: advisory_single_run` — a wynik LLM jest oznaczany
`advisory-only` i nie stanowi korzenia zaufania, czego wymaga `P-CORE-016`.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: `POLICY.md` rozstrzyga wprost, czy autor zaufanego zatwierdzenia
  może wykonać merge tego samego pull requesta — reguła, nie komentarz.
- [ ] AC-02: Jeżeli decyzja brzmi „tak", reguła wymienia dowody wymagane przy
  takim merge'u: merge dokładnie tego head SHA, który był zatwierdzony; zakaz
  obejścia branch protection uprawnieniami administratora; potwierdzenie stanu
  `MERGED` po fakcie.
- [ ] AC-03: Jeżeli decyzja brzmi „nie", reguła nazywa tożsamość uprawnioną do
  merge'a i sposób jej weryfikacji.
- [ ] AC-04: `governance/manifest.default.json` i
  `docs/GOVERNANCE_ENFORCEMENT.md` odzwierciedlają rozstrzygnięcie; bramka
  odrzuca konfigurację z nim sprzeczną.

## Ryzyka i Uwagi

- Ryzyko: lista wymaganych checków znana walidatorowi bywa węższa niż ruleset —
  dziś jest (`ticket-030`). Skutek jest jednak ograniczony: przy
  `strict_required_status_checks_policy: true` ruleset i tak odmówi merge'a, więc
  trybem awarii jest głośno nieudany merge, a nie merge niezweryfikowanego kodu.
- Uwaga: `--admin` obchodzi ruleset i nie może być częścią żadnego wariantu —
  próba użycia go na PR #36 słusznie odbiła się od `require_last_push_approval`.
- Uwaga: projekt techniczny po stronie `validator-agent` istnieje —
  `merge_at_head()` z `--match-head-commit` (atomowa kontrola heada po stronie
  GitHuba), bez `--admin`, z potwierdzeniem `MERGED`/`mergedAt`, za wyłączonym
  domyślnie interlockiem `DIRECT_PR_MERGE_ENABLED`. Nie zaimplementowany,
  ponieważ czeka na tę decyzję.
- Zależność: `ticket-028` musi być zamknięty wcześniej. Bez atrybucji ticketu
  approval nie spełnia `ASSERT APPROVAL_IDENTIFIES_CURRENT_ACTIVE_TICKET`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-029/`.
