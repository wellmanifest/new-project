# Policy DSL profile for `CONTRIBUTING.md`

`CONTRIBUTING.md` is a consuming profile of the experimental
`wellmanifest.policy/v1` language. It does not own a private shell language and
does not make its declarations executable.

## Identity and revisions

Three independent version layers are deliberately kept separate:

| Layer | Current identity | Meaning |
| --- | --- | --- |
| language | `wellmanifest.policy/v1` | incompatible syntax and semantics |
| runtime alias | `policy-sh@1` | historical name accepted by `wellm` |
| document profile | `CONTRIBUTING VERSION 13` | revision of this policy document |

Changing prose or a repository procedure may advance the document revision
without changing the language major. A breaking grammar or Policy IR change
requires a new language major. A runtime release has its own package version.

## Deterministic Markdown carrier

Normative declarations are selected only from fenced blocks labelled `dsl`.
The first concrete `DOCUMENT CONTRIBUTING` block supplies the header; later
policy blocks are concatenated in source order. Placeholder syntax examples,
independent embedded documents and all `bash`, `text` and prose blocks are not
part of the Policy DSL input. A selected block is parsed completely and an
unknown statement fails closed.

The repository's `dsl-manifest.json` binds the carrier, this guide and the
selector regression to exact SHA-256 digests. `tests/rule-enforcement.test.sh`
also rejects any concrete `RULE`, `STATE` or `TRANSITION` declaration placed
outside a `dsl` fence.

## Runtime and portable implementations

The language owner is `wellmanifest/policy-dsl`. Its normative EBNF, closed
Policy IR JSON Schema, fixtures and conformance tests define interoperability.
The reference checker parses and normalizes inert text but deliberately has no
executor. `wellm` provides a typed Python runtime and accepts both the
canonical identifier and `policy-sh@1`; alternative TypeScript, Rust or other
implementations must produce structurally equivalent Policy IR and pass the
same fixtures.

Exporting Policy IR as JSON is the language-neutral boundary. Parser libraries
such as Lark, TatSu, textX, pest, nearley, Ohm or ANTLR are implementation
choices, not separate dialects. Generated source code is optional; conformance
is measured against grammar, schema and fixtures rather than a particular
parser library.

## Env DSL composition

The historical `ENV_FILE`, `VARIABLE` and `SECRET` declarations in
`CONTRIBUTING.md` are a Policy DSL compatibility surface. They are neither an
extension nor an implementation of Env DSL 1. `wellmanifest.env` owns its
ABNF, deterministic layering and evaluator. A typed adapter may supply its
inert result as the explicit context used to evaluate Policy IR:

```text
Env DSL -- validate/evaluate --> typed context
                                      |
Policy DSL -- parse/schema --> Policy IR -- evaluate --> proposed operation
                                                        |
                                                        v
                                                  POA boundary
```

Secret values remain outside both documents and are resolved by a separately
governed provider.

## LLM, GBNF, MCP and POA

An LLM may generate a proposal through the constrained GBNF published by
`policy-dsl`. GBNF limits the token surface, but acceptance still requires the
canonical parser and closed Policy IR Schema. The candidate action vocabulary
is intentionally bounded and cannot contain shell execution, credentials,
approval evidence or authority envelopes.

MCP may expose the exact grammar and schema, a validation operation, a
parse/normalize operation and stable diagnostics. It is only a transport: an
MCP tool call does not widen the model's `propose-only` authority. The safe
flow is:

```text
LLM + GBNF -> Policy text -> parser -> closed Policy IR -> policy checks
                                                        -> POA request/plan
                                                        -> protected approval
                                                        -> execution envelope
                                                        -> receipt
```

POA owns the authorization boundary. Parsing a valid document, producing an
IR or receiving it over MCP never authorizes an effect. Only a protected POA
controller may bind an approved plan to an execution envelope.

## Publication status

The language remains experimental, but its v1 contract is now available from
the exact reviewed revision
`daaf7b7b96312a2469de1b4799f2f81c7396de4e`, reachable from protected
`wellmanifest/policy-dsl` main. The consuming manifest locks the normative
specification, EBNF, constrained GBNF, closed Policy IR schema and reference
checker to that revision and their SHA-256 digests. The installable checker is
independently pinned by `governance/policy-dsl.lock.json`; neither lock follows
a mutable branch.
