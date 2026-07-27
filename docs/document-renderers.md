# Contract And Legal Document Renderers

This document defines the responsibilities and legal boundaries of the
Intent/Contract document renderers implemented in
`@office-dsl/document-renderer`. The renderers turn an approved or in-progress
`intent-contract.dsl.v1` snapshot into a human-readable Markdown draft with a
traceability map back to the DSL.

## Legal Disclaimers

Every rendered document is a **draft**. The renderers embed the shared
`DRAFT_DISCLAIMER` at the top of each output. The disclaimer states that:

- The document was generated automatically from an Intent/Contract DSL snapshot.
- It is **non-binding** and must be reviewed by the parties and by qualified
  legal counsel before it is used.
- The renderer **must not add, infer, or invent any term** that is not present
  in the DSL.
- Fields that are missing, ambiguous, conflicting, or unapproved are shown as
  **explicit gaps** and are never filled with assumed legal language.

## Must Not Invent Terms

The renderers are deterministic and source-bound:

- A field value is only rendered when its `value` is non-null and its `status`
  is `CONFIRMED`, `INCOMPLETE`, or `ASSUMED`.
- `ASSUMED` values that have not been approved are rendered with an
  `(ASSUMED - needs approval)` marker and listed under `assumptions`.
- Any other status (`MISSING`, `AMBIGUOUS`, `CONFLICTING`, `REJECTED`,
  `NOT_APPLICABLE`) and any absent field is rendered as an explicit
  `[GAP: ...]` marker and listed in the `Open Items And Gaps` section.
- Empty node lists are rendered as `[GAP: none stated in DSL]`; the renderer
  never fabricates a placeholder clause.

Because the renderers only read fields that exist in the Intent/Contract model,
inputs such as employment guidelines render **without unsupported fields**: any
detail that the DSL does not carry becomes a gap rather than invented text.

## Renderers

- **Task delegation** (`renderTaskDelegation`) renders the delegator, assignee,
  deliverables, deadlines, dependencies, exclusions, and acceptance criteria
  from the DSL only.
- **Service agreement** (`renderServiceAgreement`) renders parties, scope
  (subjects, deliverables, obligations), payment (with resolved payer/payee),
  acceptance criteria, exclusions, and governing law from approved DSL.
- **Employment agreement / guideline** (`renderEmploymentAgreement`) renders
  employer, employee, position and duties, remuneration, term, conditions,
  guidelines/acceptance, and exclusions as a draft, using only model fields.
- **Dispatch** (`renderDocument`) selects the renderer from
  `document.type.value`; unknown or generic contract types fall back to the
  service agreement renderer.

## Document-To-DSL Traceability Map

Every rendered document carries a `traceability` array and appends a
`Traceability Map` table to the Markdown. Each entry maps a rendered
paragraph/item to:

- `section` - the document section heading it belongs to,
- `label` - the rendered item label,
- `dslPaths` - the DSL field paths (`FormalField.field`) that produced it,
- `sourceIds` - the source reference ids (`SourceReference.id`) behind the value.

This guarantees that each paragraph references DSL paths or source references,
so reviewers can audit exactly where every rendered statement came from.
