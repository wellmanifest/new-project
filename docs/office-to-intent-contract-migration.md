# Office DSL To Intent/Contract Migration

This note defines the compatibility path from the current executable `office.dsl.v1` MVP into the standalone canonical `intent-contract.dsl.v1` model.

The adapter is intentionally deterministic and conservative. It preserves the executable intent and audit-relevant structure of an Office DSL task, but it does not infer legal contract terms, bilateral approval, real parties, payment terms, deadlines, or natural-language facts that are not present in the source DSL.

## Implemented Adapter

The implementation lives in `packages/intent-contract-model/src/index.ts` as `officeDslToIntentContractDsl(task)`.

It returns:

- `dsl`: a valid `IntentContractDsl` snapshot,
- `notes`: migration notes with `fromPath`, `toPath`, `decision`, `status`, and `reason` for mapped or assumed fields.

The resulting snapshot can be canonicalized and hashed with `canonicalizeIntentContractDsl` and `hashIntentContractDsl`.

## Mapping Rules

| Office DSL path                | Intent/Contract path                       | Status                           | Notes                                                                                  |
| ------------------------------ | ------------------------------------------ | -------------------------------- | -------------------------------------------------------------------------------------- |
| `task.title`                   | `document.title`                           | `CONFIRMED`                      | Direct task title mapping.                                                             |
| `task.input`                   | `intents[0].description`                   | `CONFIRMED`                      | Original request text is preserved as the main intent.                                 |
| `task.createdBy`               | `parties[0]`, `roles[0]`                   | `ASSUMED`                        | Single-request Office DSL is treated as Human1 intent.                                 |
| `sources[]`                    | `subjects[]`, `sourceReferences[]`         | `CONFIRMED`                      | Mock source names are preserved as system source references.                           |
| `steps[]`                      | `obligations[]`                            | `CONFIRMED` plus `ASSUMED` owner | Office actions become runtime obligations owned by `office-runtime`.                   |
| `steps[].when`                 | `conditions[]`                             | `CONFIRMED`                      | Existing execution conditions become canonical conditions.                             |
| step order                     | `dependencies[]`                           | `ASSUMED`                        | Sequential Office DSL order becomes an assumed dependency chain.                       |
| `expectedResults[]`            | `acceptanceCriteria[]`                     | `CONFIRMED`                      | Existing expected results become completion criteria.                                  |
| `output`                       | `deliverables[0]`                          | `CONFIRMED` plus `ASSUMED` owner | Output format and save target become the current deliverable.                          |
| `policies[decision=DENY]`      | `exclusions[]`                             | `CONFIRMED`                      | Deny policies become explicit exclusions.                                              |
| `policies[]`                   | `risks[]`                                  | `CONFIRMED` plus `ASSUMED` level | Risk text is direct, risk level is inferred from policy decision.                      |
| `steps[].ask`                  | `questions[]`                              | `MISSING`                        | Clarification prompts become unresolved canonical questions.                           |
| `version` and runtime metadata | `assumptions[]`, `render[]`, `execution[]` | `ASSUMED`                        | The adapter records compatibility assumptions instead of inventing contract semantics. |

## Deliberate Omissions

The adapter leaves these canonical collections empty unless source data exists in future Office DSL versions:

- `deadlines`,
- `payments`,
- `conflicts`,
- `approvals`,
- `contract`.

This is deliberate. The current Office DSL does not encode bilateral agreement, payment terms, legal governing law, or approval decisions, so mapping those fields would create unauthorized meaning.

## Validation Expectations

The adapter must keep these guarantees:

- migrated snapshots pass `validateIntentContractDsl`,
- equivalent Office DSL inputs produce equivalent canonical JSON and hash output,
- clarification steps remain completion-blocking canonical questions,
- every assumed value appears in migration notes.

Current coverage lives in `tests/intent-contract-model.test.ts`.
