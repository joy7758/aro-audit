# Appendix A: AAR-MCP-2.0 Conformance Schema & BPF Profiles (RC1)

**Status:** IMPLEMENTED (RC1)
**Architecture:** MVK (Minimum Viable Kernel) / Model 1 Hard-Gate
**Compliance Target:** Kinetic FAIR Digital Object (K-FDO)

This appendix defines the machine-readable integration contracts and the mandatory kernel-level isolation policies required for a host to claim **RC1-Secure-Host** compliance.

---

## 1. The Capability Contract (JSON Schema)

The `CapabilityToken` is a single-use, intent-bound cryptographic artifact. High-risk tools must present this token via the Broker IPC channel. Direct syscalls are structurally denied.

### 1.1 `CapabilityToken` Schema definition

```json
{
  "$schema": "[http://json-schema.org/draft-07/schema#](http://json-schema.org/draft-07/schema#)",
  "title": "AAR-MCP Capability Token",
  "description": "Cryptographic capability required for MVK side-effect synthesis.",
  "type": "object",
  "properties": {
    "intent_hash": {
      "type": "string",
      "pattern": "^sha256:[a-fA-F0-9]{64}$",
      "description": "Cryptographic commitment of the exact arguments and target resource."
    },
    "spatial_fingerprint": {
      "type": "string",
      "description": "[MIP Integration] Hardware-backed spatial signature. Required for Tier-1 Sovereign hosts; optional but recommended for Tier-2."
    },
    "nonce": {
      "type": "string",
      "description": "Single-use entropy to prevent TOCTOU and IPC replay attacks. Atomically invalidated upon consumption."
    },
    "target_resource": {
      "type": "string",
      "description": "Resolved object identity (e.g., specific absolute file path or database URI), not a generic string."
    }
  },
  "required": ["intent_hash", "nonce", "target_resource"]
}

```

---

## 2. Kernel Enforcement: Seccomp-BPF Confinement Profile

To prevent descriptor smuggling and out-of-band execution, the host MUST apply a strict `seccomp-bpf` filter to the tool's user namespace prior to execution.

### 2.1 Capability Boundary Pseudo-Profile

The following represents the logical BPF routing map enforced by the MVK.

```c
// MVK Capability BPF Policy (Conceptual)
// Default Posture: DENY (Kill Process) for all state-mutating primitives.

SECCOMP_RULE_INIT() {
    // 1. Explicitly Deny Direct I/O & Network Primitives
    bpf_add_rule(SECCOMP_RET_KILL_PROCESS, SYS_openat, ...);
    bpf_add_rule(SECCOMP_RET_KILL_PROCESS, SYS_connect, ...);
    bpf_add_rule(SECCOMP_RET_KILL_PROCESS, SYS_execve, ...);
    bpf_add_rule(SECCOMP_RET_KILL_PROCESS, SYS_ptrace, ...);

    // 2. Allow Read-Only / Safe Primitives (Compute only)
    bpf_add_rule(SECCOMP_RET_ALLOW, SYS_read, ...);
    bpf_add_rule(SECCOMP_RET_ALLOW, SYS_getrandom, ...);
    
    // 3. The ONLY Exit Node: Broker IPC
    // Allow write/sendmsg ONLY if the target fd matches the pre-established IPC socket (passed via O_CLOEXEC)
    bpf_add_rule(SECCOMP_RET_ALLOW, SYS_sendmsg, 
                 CMP_EQ(fd, BROKER_IPC_FD_INHERITED));
}

```

*Note: The underlying Physical Unclonable Function (PUF) alignment logic validating the `spatial_fingerprint` is encapsulated within the baseband SDK and is not exposed in this open-source schema.*

---

## 3. Structural Meltdown Codes (Fail-Closed Lexicon)

When the conformance gate rejects an operation, the MVK terminates the execution and emits an audit bundle containing one of the following terminal states:

| Error Code | Description | Architectural Implication |
| --- | --- | --- |
| `ERR_BOUNDARY_SIGSYS` | Tool attempted a raw, unbrokered syscall. | Process physically terminated by the kernel. Host namespace integrity verified. |
| `ERR_INTENT_DIVERGENCE` | Tool requested a capability for resource B, but the journaled intent was for resource A. | Predicate-Tamper vector blocked. Tool compromised. |
| `ERR_CAPABILITY_CONSUMED` | Token `nonce` CAS (Compare-And-Swap) failed. | IPC replay or high-concurrency TOCTOU attack neutralized. |
| `ERR_MIP_SPATIAL_MISMATCH` | The spatial hardware signature failed closed-source verification. | Physical constitution violation. Non-local/simulated execution detected. |
