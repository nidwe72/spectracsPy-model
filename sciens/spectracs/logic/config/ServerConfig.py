import os
from typing import Dict, Optional


class ServerConfig:
    """Loads server-side secrets/config from a `.env` in an EXTERNAL, un-versioned folder
    (`spectracsPy-server-config/.env`) — outside all repos, never committed. SPEC_paypal_payment.md
    §4.4 / D4.

    Folder resolution: the `SPECTRACS_SERVER_CONFIG_DIR` env var if set, else walk up from this file
    to the sibling `spectracsPy-server-config` folder next to the repo roots.

    Zero new dependencies: a tiny KEY=VALUE parser (no python-dotenv), stdlib only. Values may carry a
    whitespace-preceded ` #` inline comment and optional surrounding quotes, both stripped.
    """

    _cache: Optional[Dict[str, str]] = None

    @classmethod
    def get(cls, key: str, default=None):
        value = cls._load().get(key)
        if value is None or value == "":
            return default
        return value

    @classmethod
    def getInt(cls, key: str, default: int) -> int:
        try:
            return int(cls._load().get(key))
        except (TypeError, ValueError):
            return default

    @classmethod
    def reload(cls):
        cls._cache = None

    @classmethod
    def configDir(cls) -> Optional[str]:
        override = os.environ.get("SPECTRACS_SERVER_CONFIG_DIR")
        if override:
            return override
        here = os.path.dirname(os.path.abspath(__file__))
        for _ in range(12):
            candidate = os.path.join(here, "spectracsPy-server-config")
            if os.path.isdir(candidate):
                return candidate
            parent = os.path.dirname(here)
            if parent == here:
                break
            here = parent
        return None

    @classmethod
    def _envPath(cls) -> Optional[str]:
        directory = cls.configDir()
        if directory is None:
            return None
        return os.path.join(directory, ".env")

    @classmethod
    def _load(cls) -> Dict[str, str]:
        if cls._cache is not None:
            return cls._cache
        result: Dict[str, str] = {}
        path = cls._envPath()
        if path is not None and os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as handle:
                for raw in handle:
                    line = raw.strip()
                    if line == "" or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    # Strip an inline comment: a '#' that starts the (stripped) value — i.e. the value
                    # was blank and only a trailing comment remains — or one preceded by whitespace.
                    if value.startswith("#"):
                        value = ""
                    else:
                        hashIndex = value.find(" #")
                        if hashIndex != -1:
                            value = value[:hashIndex].strip()
                    if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
                        value = value[1:-1]         # strip matching surrounding quotes
                    result[key] = value
        cls._cache = result
        return result
