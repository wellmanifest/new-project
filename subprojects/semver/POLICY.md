# POLICY.md — Embedded & Heterogeneous Fleet SemVer Standard

`wellmanifest/semver` establishes the normative, platform-neutral standard for semantic versioning (SemVer 2.0.0), immutable binary identity binding, and safe multi-stage CI/CD delivery pipelines in heterogeneous distributed systems combining edge hosts (e.g. Raspberry Pi 5 Linux) and microcontrollers (e.g. ESP32-S3 / M5Stack CoreS3).

---

## 1. Foundational Principle

> **Firmware is Not a Web Service; A SemVer Tag Must Cryptographically Bind Physical Identity.**
>
> In heterogeneous embedded fleets, a single monolithic version string cannot describe physical hardware interfaces, MCU flash partition layouts, communication protocol schemas, and Linux host runtimes simultaneously.
>
> Every embedded firmware release MUST bind an immutable cryptographic identity (raw binary SHA-256, compiler-embedded ELF SHA-256, git commit revision, and hardware target matrix). Pushing to Git main must never trigger unmediated hardware flashing; delivery requires explicit capability authorization, pre-flight safe-state validation, dual-bank A/B streaming with bus pacing, and bootloader anti-brick rollback protection.

---

## 2. Normative Invariants

### INV-SEMVER-001: Strict Tier Separation
- System Platform Version (`system_version`), Edge Linux Host Runtime Version (`host_version`), Microcontroller Firmware Version (`mcu_firmware_version`), and Interface Contract Versions (`schema_version`) MUST increment independently according to their respective scopes.
- Firmware versions MUST NOT implicitly mirror edge host release tags.

### INV-SEMVER-002: Immutable Binary Identity Binding
Every microcontroller firmware release descriptor MUST specify:
1. `sha256`: cryptographic digest of the raw flashable binary image.
2. `elf_sha256`: 64-character hexadecimal digest from the embedded app descriptor (`esp_app_desc_t`).
3. `git_commit`: full 40-character commit SHA of the source tree.
4. `target_partition`: active/target partition slot (`ota_0` or `ota_1`).

### INV-SEMVER-003: Interface Contract SemVer
Communication protocols (OQL dialect schemas, UART frame formats, REST/WebSocket APIs) MUST maintain independent versioning with backward-compatibility guarantees across consecutive minor releases.

### INV-SEMVER-004: Hardware Compatibility Lock
Candidate firmware images MUST declare strict hardware compatibility constraints: target board, SoC variant, PCB revision, required pinouts, and minimum peripheral matrix. Flashing attempts on mismatched hardware targets MUST fail closed.

### INV-SEMVER-005: Dual-Build CI Stage Isolation
CI/CD pipelines MUST isolate host container/binary builds from cross-compilation toolchains (`xtensa-esp32s3-elf`), producing separately attested, reproducible artifacts.

### INV-SEMVER-006: Precondition Safe Idle Outputs Audit
Hardware targets and deployment proxies MUST fail closed (`HTTP 409 Conflict`) if actuators, motors, pumps, or high-voltage circuits are energized when an update is requested.

### INV-SEMVER-007: Dual-Bank A/B Delivery with Pacing
Over-the-Air (OTA) updates MUST stream exclusively into the inactive partition slot with bus transmission pacing to prevent controller starvation, conditional on running image matching (`If-Match: <elf_sha256>`).

### INV-SEMVER-008: Bootloader Anti-Brick Rollback
Newly booted firmware operates in a transient `pending_verify` state. It MUST run peripheral health checks (power rails, I2C bus scan, network connectivity) before confirming execution via `esp_ota_mark_app_valid_cancel_rollback()`. Panics or watchdogs trigger automatic fallback to the previous partition.

### INV-SEMVER-009: Separation of Git Merge from Hardware Flashing
Per `wellmanifest/merge`, branch merges and pushes to `main` update code governance only. Physical flashing is an effectful runtime operation requiring an authenticated capability token and fleet audit receipt.

### INV-SEMVER-010: Offline Conformance Verification
Standard compliance tooling (`conformance.py`) MUST execute completely offline without network access, hardware dependencies, or side effects.

---

## 3. Schemas and Routing

- Embedded Release Manifest Schema: [`schemas/embedded-release.schema.json`](schemas/embedded-release.schema.json)
- Hardware Target Matrix Schema: [`schemas/hardware-matrix.schema.json`](schemas/hardware-matrix.schema.json)
- Pipeline Run Attestation Schema: [`schemas/pipeline-run.schema.json`](schemas/pipeline-run.schema.json)
- Conformance Checker: [`operations/conformance.py`](operations/conformance.py)
