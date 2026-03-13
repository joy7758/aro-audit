# Evidence Object FDO Profile

## Purpose

This profile maps the ARO Audit Evidence Object to a FAIR Digital Object style
description so it can be discussed as a portable object type in FDO-oriented
systems.

## Object Type

- Object name: Evidence Object
- Proposed profile scope: post-run AI governance evidence
- Canonical repository: `https://github.com/joy7758/aro-audit`

## FDO Mapping

| Evidence Object Field | FDO Concept | Notes |
| --- | --- | --- |
| `agent_id` | metadata | runtime or agent identifier |
| `persona_id` | metadata | identity-facing role metadata |
| `interaction_trace` | provenance | ordered interaction history |
| `policy_decisions` | provenance | governance decision trail |
| `execution_hash` | integrity reference | content integrity anchor |
| `timestamp` | metadata | evidence creation timestamp |
| `tool_calls` | provenance | execution-relevant action log |
| `result_summary` | metadata | bounded outcome summary |

## Minimal Profile Shape

- `PID`
  - globally resolvable identifier for the evidence object
- `metadata`
  - object type
  - agent identity
  - persona identity
  - timestamp
  - result summary
- `provenance`
  - interaction trace
  - policy decisions
  - tool calls
- `integrity reference`
  - execution hash

## Handle Examples

- `21.T11966/aro-evidence-object-demo-0001`
- `hdl:21.T11966/aro-evidence-object-demo-0001`
- `https://hdl.handle.net/21.T11966/aro-evidence-object-demo-0001`

## Usage Notes

This profile does not replace the JSON schema. It provides an FDO-facing
interpretation layer so the Evidence Object can be described as a portable
object class.

The canonical validation surface remains:

- `schema/evidence.schema.json`
- `validator.py`
