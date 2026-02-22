# SPDX-License-Identifier: MIT
# Copyright (c) 2026 joy7758 contributors
from __future__ import annotations

import math

import pytest

from sdk.canonical.jcs import dumps


def test_jcs_dumps_is_deterministic() -> None:
    assert dumps({"b": 1, "a": 2}) == b'{"a":2,"b":1}'


def test_jcs_dumps_rejects_nan() -> None:
    with pytest.raises(ValueError):
        dumps({"x": math.nan})


def test_jcs_dumps_rejects_inf() -> None:
    with pytest.raises(ValueError):
        dumps({"x": math.inf})

