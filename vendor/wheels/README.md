This directory contains a temporary wheelhouse for offline build recovery.

Controls:
- Every wheel in this directory must have a matching entry in `SHA256SUMS`.
- Consumers should verify hashes before any install step.
- New wheels should be sourced from official package indexes and reviewed before commit.

Preferred direction:
- Do not add new vendored wheels to git.
- Move future binary distribution to a package registry or release artifact flow.
