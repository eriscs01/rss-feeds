"""Pydantic models for feed configuration and settings."""

from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings


class FeedType(StrEnum):
    REQUESTS = "requests"
    SELENIUM = "selenium"


class FeedConfig(BaseModel):
    """Configuration for a single feed generator."""

    script: str
    type: FeedType
    blog_url: str
    enabled: bool = True
    output_name: str | None = None

    @field_validator("script")
    @classmethod
    def script_must_exist(cls, v: str) -> str:
        script_path = Path(__file__).parent / v
        if not script_path.exists():
            msg = f"Script not found: {v}"
            raise ValueError(msg)
        return v


class GlobalSettings(BaseSettings):
    """Project-wide settings, overridable via RSS_ env vars.

    Example: RSS_REPO_SLUG=oborchers/rss-feeds overrides the default.
    """

    model_config = {"env_prefix": "RSS_"}

    repo_slug: str = "Olshansk/rss-feeds"


REGISTRY_PATH = Path(__file__).parent.parent / "feeds.yaml"


def load_feed_registry() -> dict[str, FeedConfig]:
    """Load and validate feeds.yaml.

    Returns:
        Dict mapping feed name to validated FeedConfig.

    Raises:
        FileNotFoundError: If feeds.yaml is missing.
        ValidationError: If any feed config is invalid.
    """
    registry_path = REGISTRY_PATH
    if not registry_path.exists():
        msg = f"Feed registry not found: {registry_path}"
        raise FileNotFoundError(msg)

    with open(registry_path) as f:
        data = yaml.safe_load(f)

    feeds = {}
    for name, config in data.get("feeds", {}).items():
        feeds[name] = FeedConfig(**config)
    return feeds


def disable_feeds(names: list[str], registry_path: Path | None = None) -> list[str]:
    """Set `enabled: false` on registry entries, preserving comments and layout.

    How:
    1. Locate each feed's two-space-indented key and its four-space-indented block.
    2. Rewrite an existing `enabled` line, or append one to the end of the block.
    3. Leave unknown and already-disabled feeds untouched.

    Returns:
        Names whose entries were changed.
    """
    registry_path = registry_path or REGISTRY_PATH
    lines = registry_path.read_text().splitlines()
    changed = []
    for name in names:
        try:
            start = lines.index(f"  {name}:")
        except ValueError:
            continue
        end = start + 1
        while end < len(lines) and lines[end].startswith("    "):
            end += 1
        block = range(start + 1, end)
        existing = next((i for i in block if lines[i].split(":")[0].strip() == "enabled"), None)
        if existing is None:
            lines.insert(end, "    enabled: false")
        elif lines[existing].split("#")[0].split(":", 1)[1].strip() == "false":
            continue
        else:
            lines[existing] = "    enabled: false"
        changed.append(name)
    if changed:
        registry_path.write_text("\n".join(lines) + "\n")
    return changed
