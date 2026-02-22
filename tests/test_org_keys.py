# SPDX-License-Identifier: MIT
# Copyright (c) 2026 joy7758 contributors
from __future__ import annotations

import os
import stat
from pathlib import Path

from sdk.keys.org_keys import load_or_create_keypair, pubkey_fingerprint


def test_load_or_create_keypair_roundtrip(tmp_path: Path) -> None:
    key_path = tmp_path / "org_subkey_ed25519.pem"

    pair1 = load_or_create_keypair(str(key_path))
    assert key_path.exists()

    pair2 = load_or_create_keypair(str(key_path))
    assert pubkey_fingerprint(pair1.pub) == pubkey_fingerprint(pair2.pub)


def test_private_key_file_permission_is_restricted(tmp_path: Path) -> None:
    key_path = tmp_path / "org_subkey_ed25519.pem"
    load_or_create_keypair(str(key_path))

    if os.name == "posix":
        mode = stat.S_IMODE(key_path.stat().st_mode)
        assert mode == 0o600

