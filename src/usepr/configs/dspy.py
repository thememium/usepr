from __future__ import annotations

from pathlib import Path
from typing import Any

import dspy
import yaml

APPLICATION_NAME = "usepr"

DEFAULT_MODEL = "openrouter/openai/gpt-oss-120b"

DEFAULT_EXTRA_BODY: dict[str, Any] = {
    "provider": {"order": ["groq"], "allow_fallbacks": False}
}

CONFIG_DIR = Path.home() / ".config" / "usepr"
CONFIG_FILE = CONFIG_DIR / "config.yml"


def load_config() -> dict[str, Any]:
    """Load configuration from ~/.config/usepr/config.yml."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE) as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except (yaml.YAMLError, OSError):
        return {}


def get_lm(model: str | None = None) -> dspy.LM:
    """Get a configured DSPy LM instance.

    Priority: explicit model arg > config file > default.
    """
    config = load_config()

    resolved_model = model or config.get("model") or DEFAULT_MODEL

    extra_body = config.get("extra_body", DEFAULT_EXTRA_BODY)
    cache = config.get("cache", False)

    return dspy.LM(
        resolved_model,
        cache=cache,
        extra_body=extra_body,
        extra_headers={
            "HTTP-Referer": f"http://{APPLICATION_NAME}.local",
            "X-Title": APPLICATION_NAME,
        },
    )


def configure_dspy(model: str | None = None) -> None:
    """Configure DSPy with the resolved LM."""
    lm = get_lm(model)
    dspy.configure(lm=lm)
