import os
import threading
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Any

from sdk.canonical.jcs import dumps as jcs_dumps


@dataclass
class JournalConfig:
    path: str
    fsync_on_flush: bool = True


class JSONLJournal:
    def __init__(self, config: JournalConfig):
        self.config = config
        journal_path = Path(config.path)
        journal_path.parent.mkdir(parents=True, exist_ok=True)
        # Line buffering reduces the chance of partial writes without explicit flush().
        self._fh = open(config.path, "a+", encoding="utf-8", buffering=1)
        self._lock = threading.Lock()
        self._line_count = self._count_nonempty_lines(journal_path)

    def __enter__(self) -> "JSONLJournal":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    @staticmethod
    def _count_nonempty_lines(path: Path) -> int:
        with open(path, "r", encoding="utf-8") as fh:
            return sum(1 for line in fh if line.strip())

    def append_statement(self, obj: dict[str, Any]) -> str:
        _, line = self.append_statement_with_lineno(obj)
        return line

    def append_statement_with_lineno(self, obj: dict[str, Any]) -> tuple[int, str]:
        """Append a canonicalized statement and return `(line_number, line)`."""
        # Canonical formatting keeps line-level hashes stable across modules.
        line = jcs_dumps(obj).decode("utf-8")
        with self._lock:
            self._fh.write(line + "\n")
            self._line_count += 1
            return self._line_count, line

    def read_lines(self) -> list[str]:
        with self._lock:
            self._fh.flush()
            with open(self.config.path, "r", encoding="utf-8") as fh:
                return [line.rstrip("\n") for line in fh if line.strip()]

    def flush(self) -> None:
        """Flush journal data and optionally fsync to disk."""
        with self._lock:
            self._fh.flush()
            if self.config.fsync_on_flush:
                os.fsync(self._fh.fileno())

    def close(self) -> None:
        with self._lock:
            if self._fh.closed:
                return
            try:
                self._fh.close()
            except OSError:
                # Best effort close for unusual filesystem/descriptor states.
                return
