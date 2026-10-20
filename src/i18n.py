"""Translated messages, same approach as herdr-talk.

Strings live in locales/<language>.json as "key": "text". {name} is filled from the values passed to t().

Language is chosen in this order, first match wins:
  1. HERDR_SIMPLE_GIT_LANG environment variable
  2. "lang" in HERDR_PLUGIN_CONFIG_DIR/config.json
  3. OS language (Windows: GetUserDefaultUILanguage, Linux/macOS: LC_ALL / LC_MESSAGES / LANG)
  4. en

A key missing in the chosen language falls back to en, then to the key name itself.
"""

import ctypes
import json
import locale
import os
import sys
from pathlib import Path

SUPPORTED = ("en", "ko", "ru", "fr", "es", "de", "ja")
DEFAULT = "en"
LOCALES_DIR = Path(__file__).resolve().parent / "locales"


class _KeepMissing(dict):
    """Keep {name} as-is when no value is passed for it, so a translation mistake does not crash."""

    def __missing__(self, key):
        return "{" + key + "}"


def normalize(value):
    """'ko_KR.UTF-8', 'ko-KR', 'KO' -> 'ko'. Returns None when the language is not supported."""
    if not value:
        return None
    code = str(value).strip().replace("-", "_").split(".")[0].split("_")[0].lower()
    return code if code in SUPPORTED else None


def _from_plugin_config():
    config_dir = os.environ.get("HERDR_PLUGIN_CONFIG_DIR")
    if not config_dir:
        return None
    try:
        data = json.loads((Path(config_dir) / "config.json").read_text(encoding="utf-8-sig"))
        return normalize(data.get("lang"))
    except (OSError, ValueError, AttributeError):
        return None


def _from_os():
    if sys.platform == "win32":
        try:
            language_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            return normalize(locale.windows_locale.get(language_id))
        except (AttributeError, OSError):
            return None
    for name in ("LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(name)
        if value:
            # The first variable that is set decides. An unsupported value falls back to en.
            return normalize(value)
    return None


def _load(language):
    try:
        return json.loads((LOCALES_DIR / f"{language}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


language = normalize(os.environ.get("HERDR_SIMPLE_GIT_LANG")) or _from_plugin_config() or _from_os() or DEFAULT
_fallback = _load(DEFAULT)
_messages = _fallback if language == DEFAULT else _load(language)


def t(key, **values):
    text = _messages.get(key) or _fallback.get(key) or key
    return text.format_map(_KeepMissing(values)) if values else text
