---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "physical-interface-contracts",
  "kind": "information",
  "version": 1,
  "title": "Physical interface contracts",
  "status": "proposed",
  "owner": "wellmanifest/new-project",
  "created": "2026-09-30",
  "updated": "2026-09-30",
  "review_after": "2026-10-30",
  "source_revision": "fa7972da8f6a28a0afe2914aacf46bee4a846943",
  "affected_repositories": ["wellmanifest/new-project", "maskservice/stacknet", "maskservice/c2004"],
  "evidence": [
    "maskservice/c2004 9075af5 (Tic249 limit switches SCL/SDA to TX/RX with polarity flip)",
    "maskservice/stacknet eba4b09 (cores3-i2c-tic profile without the dri0050 module)",
    "maskservice/stacknet 9afcb79 (PLF-2712 restores the pump module)"
  ]
}
---

# Physical interface contracts

<!-- docs:section purpose -->
## Purpose

Some repository values mean something physical: which pin carries a limit
switch, whether it is active low or high, whether a pull-up is on, which
hardware modules a deployable firmware profile starts. A unit test that
compares such a file with a new expected value only confirms what the author
intended. It cannot show that the device still behaves correctly. The rules
`P-PHYS-001` to `P-PHYS-003` make each change of physical meaning explicit and
tie it to an observation on real hardware.

<!-- docs:section scope -->
## Scope

The gate applies only to repositories that declare
`.governance/physical-contracts.json`. Other adopters are unaffected. It covers
ticket intents with schema v2 or v3.

<!-- docs:section content -->
## Contract

### Adopter declaration

```json
{
  "schema": "new-project.physical-contracts/v1",
  "contracts": [
    {
      "id": "tic249-limit-switches",
      "paths": ["contracts/hardware/tic249-*.json"],
      "properties": ["pin-assignment", "active-level", "pull"],
      "hazard": "motion",
      "acceptance": "Each switch reads inactive at rest and active while actuated on the rig."
    }
  ]
}
```

`properties` lists what the files can change: `pin-assignment`,
`active-level`, `pull`, `capability-set`, `unit-scale`, `limit-range` and
`timing`. `hazard` is `motion`, `pressure`, `electrical`, `thermal` or
`none`. The schema is `governance/physical-contracts.schema.json`.

### Ticket intent

When a changed path matches a contract, the intent carries one
`physicalChanges` entry per changed property:

```json
"physicalChanges": [
  {"contract": "tic249-limit-switches", "property": "pin-assignment",
   "signal": "limit forward/reverse", "before": "SCL/SDA", "after": "TX/RX",
   "acceptance": ["forward reads inactive at rest and active while pressed",
                  "reverse reads inactive at rest and active while pressed"]},
  {"contract": "tic249-limit-switches", "property": "active-level",
   "signal": "limit forward/reverse", "before": "active-low", "after": "active-low",
   "acceptance": ["..."]}
]
```

`before` and `after` must differ; the second entry above is rejected, which
is the point. An edit that keeps physical meaning uses
`{"contract": "...", "property": "none", "rationale": "..."}`.

### Diagnostics

- `GOV-PHYS-001`: a changed path matches a contract and the intent has no
  entry for it.
- `GOV-PHYS-002`: the declaration is invalid; the gate fails closed.

<!-- docs:section evidence -->
## Evidence

Two regressions on 2026-09-29 motivated this contract. Both passed their
repository tests.

- Moving the Tic T249 limit switches from SCL/SDA to TX/RX also changed them
  from active-low to active-high. With switches that pull the pin to ground,
  both limits then read active at rest and the artificial lung refused to
  start. The contract test asserted the new, wrong polarity.
- A new I2C Tic firmware profile was composed without the `dri0050` module
  that the deployed profile had. The pump driver never started, and every
  pump command failed as "not ready".

A declared `physicalChanges` list would have put `active-level` and
`capability-set` next to the intended change in review, with a rest/actuated
check that fails on the rig.

<!-- docs:section limitations -->
## Limitations

The gate cannot tell which property a diff changes. It enforces that the
author names the changes and plans their hardware acceptance. The observation
itself (`P-PHYS-002`) is produced by the adopter's hardware runtime and is
enforced manually. Capability parity between profiles (`P-PHYS-003`) needs
an adopter-side test.

<!-- docs:section next_actions -->
## Next actions

- Adopt the declaration in `maskservice/stacknet` (firmware profiles) and
  `maskservice/c2004` (Tic249 NVM contract).
- Add a digest-bound hardware acceptance receipt so `P-PHYS-002` can become
  deterministic.
