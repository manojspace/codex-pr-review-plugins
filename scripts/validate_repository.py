#!/usr/bin/env python3
"""Validate the marketplace and both plugin bundles."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_PATH = ROOT / ".agents/plugins/marketplace.json"
README_PATH = ROOT / "README.md"
EXPECTED_PLUGINS = ("github-pr-review-fix", "pr-review-and-commit")
EXPECTED_REPOSITORY = "https://github.com/manojspace/codex-pr-review-plugins"
PRIVATE_MARKERS = (
    "/Users/" + "manoj",
    "team-" + "vedak",
    "DataAnalytics" + "Services",
    "Local " + "developer",
)


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"Cannot parse {path.relative_to(ROOT)}: {error}")
    if not isinstance(value, dict):
        fail(f"Expected an object in {path.relative_to(ROOT)}")
    return value


def load_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail(f"Missing YAML frontmatter in {path.relative_to(ROOT)}")
    value = yaml.safe_load(match.group(1))
    if not isinstance(value, dict):
        fail(f"Invalid YAML frontmatter in {path.relative_to(ROOT)}")
    return value


def validate_marketplace() -> None:
    marketplace = load_json(MARKETPLACE_PATH)
    if marketplace.get("name") != "pr-review-plugins":
        fail("Marketplace name must be pr-review-plugins")

    entries = marketplace.get("plugins")
    if not isinstance(entries, list):
        fail("Marketplace plugins must be a list")
    names = tuple(entry.get("name") for entry in entries if isinstance(entry, dict))
    if names != EXPECTED_PLUGINS:
        fail(f"Expected marketplace plugins {EXPECTED_PLUGINS}, got {names}")

    for entry in entries:
        name = entry["name"]
        expected_path = f"./plugins/{name}"
        if entry.get("source") != {"source": "local", "path": expected_path}:
            fail(f"Unexpected marketplace source for {name}")
        if entry.get("policy") != {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        }:
            fail(f"Unexpected marketplace policy for {name}")
        if entry.get("category") != "Productivity":
            fail(f"Unexpected marketplace category for {name}")
        if not (ROOT / expected_path).is_dir():
            fail(f"Marketplace source does not exist for {name}")


def validate_install_documentation() -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    required_text = (
        "## Install with the desktop dialog",
        "manojspace/codex-pr-review-plugins",
        "| Git ref | `main` |",
        "| Sparse paths | Leave blank |",
        "PR Review + Fix",
        "PR-Review and Commit",
        "## Install with the CLI",
        "codex plugin marketplace add",
    )
    for required in required_text:
        if required not in readme:
            fail(f"Missing installation documentation {required!r} in README.md")


def validate_plugin(name: str) -> None:
    plugin_root = ROOT / "plugins" / name
    manifest = load_json(plugin_root / ".codex-plugin/plugin.json")
    if manifest.get("name") != name:
        fail(f"Manifest name mismatch for {name}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("version", ""))):
        fail(f"Manifest version is not semantic for {name}")
    if manifest.get("author", {}).get("name") != "Manoj Swami":
        fail(f"Manifest author mismatch for {name}")
    if manifest.get("repository") != EXPECTED_REPOSITORY:
        fail(f"Manifest repository mismatch for {name}")
    if manifest.get("license") != "MIT":
        fail(f"Manifest license mismatch for {name}")
    if manifest.get("skills") != "./skills/":
        fail(f"Manifest skills path mismatch for {name}")
    if manifest.get("interface", {}).get("developerName") != "Manoj Swami":
        fail(f"Manifest developer mismatch for {name}")

    skill_path = plugin_root / "skills" / name / "SKILL.md"
    frontmatter = load_frontmatter(skill_path)
    if frontmatter.get("name") != name:
        fail(f"Skill name mismatch for {name}")

    skill_text = skill_path.read_text(encoding="utf-8")
    required_naming_text = (
        "codex_app__set_thread_title",
        "PR Review - <goal>",
        "<N> PRs Review - <goal>",
        "operational request wording",
    )
    for required in required_naming_text:
        if required not in skill_text:
            fail(f"Missing task-naming rule {required!r} in {name}")

    for reference in re.findall(r"`(references/[^`]+\.md)`", skill_text):
        if not (skill_path.parent / reference).is_file():
            fail(f"Missing referenced file {reference} in {name}")

    for path in plugin_root.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for marker in PRIVATE_MARKERS:
            if marker in text:
                fail(f"Private marker found in {path.relative_to(ROOT)}")


def main() -> int:
    try:
        validate_marketplace()
        validate_install_documentation()
        for plugin in EXPECTED_PLUGINS:
            validate_plugin(plugin)
    except (KeyError, TypeError, ValueError) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        return 1
    print("validated marketplace and 2 plugin bundles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
