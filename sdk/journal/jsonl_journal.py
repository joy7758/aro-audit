import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sdk.canonical.jcs import dumps as jcs_dumps


@dataclass
class JournalConfig:
    path: str
    fsync_on_flush: bool = True


class JSONLJournal:
    def __init__(self, config: JournalConfig):
        self.config = config
        Path(config.path).parent.mkdir(parents=True, exist_ok=True)
        # Line buffering reduces the chance of partial writes without explicit flush().
        self._fh = open(config.path, "a+", encoding="utf-8", buffering=1)
        self._lock = threading.Lock()

    def append_statement(self, obj: dict[str, Any]) -> str:
        # Canonical formatting keeps line-level hashes stable across modules.
        line = jcs_dumps(obj).decode("utf-8")
        with self._lock:
            self._fh.write(line + "\n")
        return line

    def read_lines(self) -> list[str]:
        with self._lock:
            self._fh.flush()
            with open(self.config.path, "r", encoding="utf-8") as fh:
                return [line.rstrip("\n") for line in fh if line.strip()]

    def flush(self):
        """
        公共稳定接口：保证写入落盘
        """
        with self._lock:
            self._fh.flush()
            if self.config.fsync_on_flush:
                os.fsync(self._fh.fileno())

    def close(self):
        try:
            with self._lock:
                self._fh.close()
        except Exception:
            pass
