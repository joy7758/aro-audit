import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class JournalConfig:
    path: str


class JSONLJournal:
    def __init__(self, config: JournalConfig):
        self.config = config
        Path(config.path).parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(config.path, "a+", encoding="utf-8")

    def append_statement(self, obj: dict):
        line = json.dumps(obj, ensure_ascii=False)
        self._fh.write(line + "\n")

    def flush(self):
        """
        公共稳定接口：保证写入落盘
        """
        self._fh.flush()
        os.fsync(self._fh.fileno())

    def close(self):
        try:
            self._fh.close()
        except Exception:
            pass
