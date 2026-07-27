# Examples Run Verification

Date: 2026-07-27

This report records a full examples run after the package-boundary refactor and checks whether generated artifacts match the agreed project rules.

## Commands Run

- `.\project.bat examples`
- `.\project.bat examples-chat`
- `.\project.bat examples-recruitment`

Note: the first sandboxed `examples` run failed with the known Windows Codex sandbox `spawn EPERM` limitation. The same command was rerun outside the sandbox and passed. `examples-chat` and `examples-recruitment` passed in the normal run.

## Runner Results

| Runner                 | Result | Details              |
| ---------------------- | ------ | -------------------- |
| `examples`             | PASS   | 6/6 scenarios passed |
| `examples-chat`        | PASS   | 4/4 scenarios passed |
| `examples-recruitment` | PASS   | 4/4 scenarios passed |

Office examples:

- `01-read-only-report`: PASS
- `02-clarification`: PASS
- `03-email-drafts`: PASS
- `04-confirmed-send`: PASS
- `05-policy-denial`: PASS
- `06-log-analysis`: PASS

Chat examples:

- `01-short-agreement`: PASS, outcome `AGREED`
- `02-long-negotiation-agreement`: PASS, outcome `AGREED`
- `03-short-conversation-cancelled`: PASS, outcome `CANCELLED`
- `04-long-negotiation-cancelled`: PASS, outcome `CANCELLED`

Recruitment examples:

- `01-multi-candidate`: PASS, accepted `1`, rejected `1`
- `02-single-candidate-agreement`: PASS, accepted `1`, rejected `0`
- `03-negotiated-two-candidates`: PASS, accepted `2`, rejected `0`
- `04-ocr-candidate-cancelled`: PASS, accepted `0`, rejected `1`

## Artifact Checks

Generated artifacts are written beside the scenario that produced them:

- office outputs go to `examples/<scenario>/generated/`
- chat outputs go to `examples-chat/<scenario>/generated/`
- recruitment outputs go to `examples-recruitment/01-multi-candidate/generated/`
- recruitment per-candidate final/proposal/status files go to the candidate-local `out/`

No generated JSON artifacts were found under any `generated/` folder. JSON remains only as checked-in expected fixtures under `out/`, for example `expected.summary.json` and `expected.dsl.json`.

No new example-runner artifacts were written under `.office-dsl/`.

## Chat Finalization Rules

The agreed finalization rule is respected:

```text
final-contract.dsl.hcl
contract.pdf
approvals.dsl.hcl
```

exist only for agreed chat scenarios:

- `examples-chat/01-short-agreement/generated/final/`
- `examples-chat/02-long-negotiation-agreement/generated/final/`

Cancelled chat scenarios do not contain final contract/PDF/approval artifacts. Their `generated/final/` folders contain only `cancelled-summary.md`:

- `examples-chat/03-short-conversation-cancelled/generated/final/cancelled-summary.md`
- `examples-chat/04-long-negotiation-cancelled/generated/final/cancelled-summary.md`

Summary outputs confirm:

- `01-short-agreement`: `outcome = "AGREED"`, `final_created = true`
- `02-long-negotiation-agreement`: `outcome = "AGREED"`, `final_created = true`
- `03-short-conversation-cancelled`: `outcome = "CANCELLED"`, `final_created = false`
- `04-long-negotiation-cancelled`: `outcome = "CANCELLED"`, `final_created = false`

## Recruitment Finalization Rules

The first recruitment summary reports:

- `candidate_count = 2`
- `accepted = ["001-anna-nowak"]`
- `rejected = ["002-bartek-lis"]`

Candidate finalization matches the plan:

Each candidate folder also owns its document-process fixtures, so person-level input, output, chat, status, generated summaries, and md/pdf conversion checks are no longer mixed at the recruitment root.

- `001-anna-nowak` has `out/contract.dsl.txt` because the candidate outcome is `ACCEPTED`.
- `002-bartek-lis` does not have `out/contract.dsl.txt` because the candidate outcome is `REJECTED`.

Document process checks also match the agreed fixture layout:

- `001-anna-nowak/document-processes/md2pdf`: `id = "001-anna-nowak-md2pdf"`, `process = "md2pdf"`, `input = "in/cv.md"`, `output = "out/cv.pdf"`, `ok = true`
- `002-bartek-lis/document-processes/pdf2md`: `id = "002-bartek-lis-pdf2md"`, `process = "pdf2md"`, `input = "in/cv.pdf"`, `output = "out/cv.md"`, `ok = true`

## Conclusion

The current examples produce the planned outputs. `examples-recruitment` now covers four runnable scenarios: mixed accepted/rejected candidates, single-candidate direct agreement, two-candidate negotiated agreement including PDF text extraction, and OCR-fallback cancellation. The generated files are local to each example family, generated DSL files use project DSL/HCL text instead of JSON, final chat contract/PDF/approval artifacts are created only for `AGREED` scenarios, cancelled chat scenarios do not create final contract/PDF artifacts, and recruitment creates a final candidate contract only for the accepted candidate.
