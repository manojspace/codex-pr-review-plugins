#!/usr/bin/env python3
"""Validate the marketplace and both plugin bundles."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_PATH = ROOT / ".agents/plugins/marketplace.json"
README_PATH = ROOT / "README.md"
EXPECTED_PLUGINS = ("github-pr-review-fix", "pr-review-and-commit")
EXPECTED_REPOSITORY = "https://github.com/manojspace/codex-pr-review-plugins"
SHARED_REFERENCES = (
    "review-gates.md", "review-actions.md", "security.md", "database-schema.md", "database-runtime.md",
    "providers-and-timing.md", "frontend.md", "structure.md", "artifacts-and-packages.md",
)
FIXTURES = (
    "task-title-cases.md", "timeout-review-cases.md", "error-handling-review-cases.md",
    "failure-recording-review-cases.md", "security-review-cases.md",
    "test-evidence-review-cases.md", "database-review-cases.md",
    "consistency-review-cases.md", "pr-process-review-cases.md", "review-action-cases.md",
    "lifecycle-review-cases.md",
)
SIZE_LIMITS = {"SKILL.md": 12000, "review-gates.md": 18000, "workflow.md": 16000,
               "subagents.md": 6500, "fix-policy.md": 6500}


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


def validate_plugin(name: str) -> str:
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
    )
    for required in required_naming_text:
        if required not in skill_text:
            fail(f"Missing task-naming rule {required!r} in {name}")

    for reference in (*SHARED_REFERENCES, "workflow.md", "subagents.md", "fix-policy.md"):
        if not (skill_path.parent / "references" / reference).is_file():
            fail(f"Missing required reference {reference} in {name}")

    validate_reference_graph(skill_path)
    for path in (skill_path, *(skill_path.parent / "references").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if len(text) > SIZE_LIMITS.get(path.name, 6000):
            fail(f"Instruction size limit exceeded in {path.relative_to(ROOT)}")
        if "Ignore pure permission/authorization" in text:
            fail(f"Unsafe authorization exclusion in {path.relative_to(ROOT)}")
        if path.name == "workflow.md" and "## Task Naming" in text:
            fail(f"Duplicate task naming in {name}")
    metadata = yaml.safe_load((skill_path.parent / "agents/openai.yaml").read_text())
    if not isinstance(metadata, dict):
        fail(f"Invalid agent metadata in {name}")
    if metadata.get("interface", {}).get("default_prompt") != manifest["interface"]["defaultPrompt"][0]:
        fail(f"Default prompt mismatch in {name}")
    if metadata.get("policy", {}).get("allow_implicit_invocation") is not (name == "github-pr-review-fix"):
        fail(f"Invocation policy mismatch in {name}")

    return manifest["version"]


def validate_reference_graph(skill_path: Path) -> None:
    """References may route to other references; every leaf must be reachable."""
    skill_root = skill_path.parent.resolve()
    pending = [skill_path]
    seen = set()
    while pending:
        path = pending.pop().resolve()
        if path in seen:
            continue
        seen.add(path)
        text = path.read_text(encoding="utf-8")
        references = re.findall(r"(?:references/(?:[\w-]+/)*[\w-]+\.md|scripts/[\w-]+\.py)", text)
        references += re.findall(r"\]\((?!https?://)([\w./-]+\.md)(?:#[^)]*)?\)", text)
        for reference in references:
            target = (skill_root / reference if reference.startswith(("references/", "scripts/"))
                      else path.parent / reference).resolve()
            if not target.is_relative_to(skill_root) or not target.is_file():
                fail(f"Missing or escaping reference {reference} in {path.name}")
            if target.suffix == ".md":
                pending.append(target)
    orphaned = [str(p.relative_to(skill_root)) for p in (skill_root / "references").rglob("*.md")
                if p.resolve() not in seen]
    if orphaned:
        fail(f"Unreachable references in {skill_root.name}: {', '.join(sorted(orphaned))}")


def validate_review_assets() -> None:
    for asset in (*("references/" + p for p in SHARED_REFERENCES), "scripts/review_snapshot.py"):
        contents = [(ROOT / "plugins" / name / "skills" / name / asset).read_bytes()
                    for name in EXPECTED_PLUGINS]
        if contents[0] != contents[1]:
            fail(f"Shared asset mismatch: {asset}")
    for fixture in FIXTURES:
        path = ROOT / "tests" / fixture
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            fail(f"Missing or empty review fixture tests/{fixture}")


def validate_release_metadata(version: str) -> None:
    if f"`v{version}`" not in README_PATH.read_text(encoding="utf-8"):
        fail("README must document the current release pin")
    headings = re.findall(r"^## (.+)$", (ROOT / "CHANGELOG.md").read_text(), re.MULTILINE)
    if not headings or not headings[0].startswith(version + " - "):
        fail("First changelog version must match the manifests")


def validate_public_files() -> None:
    """Scan release candidates without embedding anyone's private identifiers."""
    raw = os.environ.get("PR_REVIEW_PRIVATE_MARKERS")
    marker_file = ROOT / ".private-markers"
    markers = json.loads(raw) if raw is not None else (
        marker_file.read_text().splitlines() if marker_file.is_file() else [])
    if not isinstance(markers, list) or any(not isinstance(m, str) or not m.strip() for m in markers):
        fail("Private markers must be a JSON string list or nonempty lines in .private-markers")
    if not markers:
        print("note: no private marker set; generic public-file scan only", file=sys.stderr)
    if (ROOT / ".git").exists():
        result = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--cached", "--others",
                                 "--exclude-standard", "-z"], capture_output=True, check=True)
        paths = [ROOT / os.fsdecode(p) for p in result.stdout.split(b"\0") if p]
    else:
        paths = [p for p in ROOT.rglob("*") if p.is_file() and
                 not any(part in {".git", ".venv", "__pycache__", ".private-markers"}
                         for part in p.relative_to(ROOT).parts)]
    generic = re.compile(r"/(?:Users|home)/[A-Za-z0-9_.-]+/|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
    for path in set(paths):
        if not path.exists():  # deleted candidate file
            continue
        if path.is_symlink():
            fail(f"Unexpected release symlink: {path.relative_to(ROOT)}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if generic.search(text) or any(m.casefold() in text.casefold() for m in markers):
            fail(f"Private content detected in {path.relative_to(ROOT)} (value withheld)")


def main() -> int:
    try:
        validate_marketplace()
        validate_install_documentation()
        versions = {validate_plugin(plugin) for plugin in EXPECTED_PLUGINS}
        if len(versions) != 1:
            fail("Both plugin versions must match")
        validate_review_assets()
        validate_release_metadata(next(iter(versions)))
        validate_public_files()
    except (KeyError, OSError, TypeError, ValueError, yaml.YAMLError, subprocess.CalledProcessError) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        return 1
    print("validated marketplace and 2 plugin bundles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
