# Ticket 029: Decide whether a trusted app review may also perform the merge

- **ID**: ticket-029
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: WAIT_FOR_APPROVAL
- **Utworzono**: 2026-08-06

## Cel i Zakres

Ticket rozstrzygnięcia, nie implementacji. Odpowiada na jedno pytanie: czy
tożsamość, która wystawiła zaufane zatwierdzenie, może również wykonać merge —
i pod jakimi dowodami.

Stan faktyczny, zweryfikowany 2026-08-06:

| warstwa | stan |
|---|---|
| ruleset `main-governance-protection` | `bypass_actors: []`; brak reguły ograniczającej, kto merguje |
| instalacja `ifuri-validator-agent` na `wellmanifest` | `contents: write`, `pull_requests: write` — technicznie potrafi |
| `P-CORE-015` | dopuszcza `github-app-review` jako zaufane zatwierdzenie; milczy o tym, kto merguje |
| kod `validator-agent`, ścieżka `direct-pr` | nie zawiera wywołania merge — approval kończy się zdaniem „Merge was not requested or performed" |

Czyli dziś obowiązuje układ: bot zatwierdza, człowiek merguje. Nie wynika on z
żadnej reguły — wynika z braku implementacji. Ten ticket wymaga, żeby stał się
świadomą decyzją zapisaną w `POLICY.md`, w jedną albo w drugą stronę.

Rdzeń problemu: `required_approving_review_count: 1` jest kontrolą dwóch stron
tylko dopóki approval i merge należą do różnych tożsamości. Jeśli walidator
zrobi oba, obie strony to ta sama tożsamość i nic nie łapie błędnego approvala.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: `POLICY.md` rozstrzyga wprost, czy autor zaufanego zatwierdzenia
  może wykonać merge tego samego pull requesta — reguła, nie komentarz.
- [ ] AC-02: Jeżeli decyzja brzmi „tak", reguła wymienia dowody wymagane przy
  takim merge'u: dokładny head SHA zgodny z zatwierdzonym, zakaz obejścia
  branch protection uprawnieniami administratora, oraz potwierdzenie stanu
  `MERGED` po fakcie.
- [ ] AC-03: Jeżeli decyzja brzmi „nie", reguła nazywa tożsamość uprawnioną do
  merge'a i sposób jej weryfikacji.
- [ ] AC-04: `governance/manifest.default.json` i
  `docs/GOVERNANCE_ENFORCEMENT.md` odzwierciedlają rozstrzygnięcie; bramka
  odrzuca konfigurację z nim sprzeczną.

## Ryzyka i Uwagi

- Ryzyko: automatyzacja ostatniego kroku usuwa jedyny moment, w którym człowiek
  ogląda zmianę przed jej wejściem na `main`. Mitygacja rozważana w AC-02, nie
  rozstrzygnięta tutaj.
- Uwaga: projekt techniczny po stronie `validator-agent` istnieje i jest opisany
  — `merge_at_head()` z `--match-head-commit`, bez `--admin`, z potwierdzeniem
  `MERGED`/`mergedAt`, za wyłączonym domyślnie interlockiem
  `DIRECT_PR_MERGE_ENABLED`. Nie został zaimplementowany, ponieważ czeka na tę
  decyzję.
- Uwaga: `--admin` obchodzi ruleset i nie może być częścią żadnego wariantu —
  próba użycia go na PR #36 słusznie odbiła się od `require_last_push_approval`.
- Zależność: `ticket-028` musi być zamknięty wcześniej. Bez atrybucji ticketu
  approval nie spełnia `ASSERT APPROVAL_IDENTIFIES_CURRENT_ACTIVE_TICKET`, więc
  wariant „tak" nie ma jak być zgodny z `P-CORE-015`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-029/`.
