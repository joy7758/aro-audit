# IP and License Strategy

## Current Open-Source Baseline

- Repository license: MIT (`LICENSE`)
- Copyright: maintained in `COPYRIGHT`
- Notices and third-party trademark statements: `NOTICE`
- Project mark usage constraints: `TRADEMARK_POLICY.md`

This baseline keeps adoption friction low and supports ecosystem integrations.

## Commercialization Boundary

To keep legal clarity while enabling commercialization:

1. Keep protocol/facts layer open:
   - AAR/ALC schema definitions
   - journal writer and verifier
   - manifest export format

2. Commercialize trust/compliance services:
   - managed proof/receipt services
   - enterprise policy packs and reports
   - enterprise key lifecycle integrations (KMS/HSM, rotation, revocation)

3. Avoid ambiguous mixed licensing in one module:
   - open and paid modules should be separated by package/repository boundary.

## Contribution IP Rules

Contributors must submit only content they have legal rights to provide.
See `CONTRIBUTING.md` for mandatory IP statements.

## Release Gate (Legal)

Run before release:

```bash
tools/check_legal.sh
```

A release should not proceed if legal baseline checks fail.
