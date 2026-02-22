# SPDX-License-Identifier: MIT
# Copyright (c) 2026 joy7758 contributors
from __future__ import annotations

import json
import math
from typing import Any

try:  # pragma: no cover - optional acceleration path
    import rfc8785 as _rfc8785
except Exception:  # pragma: no cover - fallback path
    _rfc8785 = None


def _validate_numbers(obj: Any) -> None:
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise ValueError("NaN/Infinity are not valid JSON numbers")
        return
    if isinstance(obj, dict):
        for value in obj.values():
            _validate_numbers(value)
        return
    if isinstance(obj, (list, tuple)):
        for value in obj:
            _validate_numbers(value)


def dumps(obj: Any) -> bytes:
    """
    Return deterministic UTF-8 canonical JSON bytes.

    Preferred backend is RFC8785 when available; otherwise we fallback to
    strict deterministic JSON serialization with sorted keys and no NaN/Inf.
    """
    _validate_numbers(obj)
    if _rfc8785 is not None:
        return _rfc8785.dumps(obj)
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")

