# Ticket 127: Adopt canonical wellmanifest/worktrees standard

- **ID**: ticket-127
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-26

## Cel i Zakres

Adopt the immutable `wellmanifest/worktrees` contract in the generated
`wellmanifest/new-project` package. Generated repositories receive the schema,
pure checker and source lock, while actual Git/filesystem effects remain owned
by an adopting runtime.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: POSIX and Windows layout planning uses workspace-level `.worktrees`.
- [ ] AC-02: The source revision and packaged bytes are SHA-256 bound.
- [ ] AC-03: Drift between the published standard and vendored files is rejected.
- [ ] AC-04: Generated projects receive the schema, checker and lock as managed files.
- [ ] AC-05: Package tests and repository governance pass.
- [ ] AC-06: Git, worktree, merge, attestation, ticket and LLM responsibilities
  resolve to one HOME pack each.
- [ ] AC-07: `wellmanifest/git` resolves to `wellmanifest/git-lifecycle` without
  creating a duplicate standard.
- [ ] AC-08: Standard-pack profiles reuse the canonical `S0-S5` model and map
  repository roles to minimum deterministic evidence.
- [ ] AC-09: A dependency-free checker distinguishes immutable managed
  projections from source duplication and supports staged `audit`/`enforce` CI.

## Ryzyka i Uwagi

- Existing noncanonical worktrees are observed but not migrated or removed.
- The package standardizes future placement; lifecycle and cleanup authority
  remain separate and lease-aware.

## Autoryzacja sesji

The user explicitly requested investigation, implementation, adoption in
`wellmanifest/new-project` and publication. This authorizes bounded protected
delivery but not destructive cleanup, secret access or branch-history rewrite.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-127/`.
