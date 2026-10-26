"""Negative package checks use temporary copies, never the working bundle."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validator", SOURCE / "scripts/validate_repository.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "bundle"
        shutil.copytree(SOURCE, self.root, ignore=shutil.ignore_patterns(
            ".git", "__pycache__", "*.pyc", ".venv", ".private-markers"))
        for name, value in {"ROOT": self.root,
                            "README_PATH": self.root / "README.md",
                            "MARKETPLACE_PATH": self.root / ".agents/plugins/marketplace.json"}.items():
            p = patch.object(validator, name, value)
            p.start()
            self.addCleanup(p.stop)
        p = patch.dict(os.environ, {"PR_REVIEW_PRIVATE_MARKERS": "[]"})
        p.start()
        self.addCleanup(p.stop)
        self.skill = self.root / "plugins/github-pr-review-fix/skills/github-pr-review-fix"

    def check_bundle(self):
        validator.validate_marketplace()
        validator.validate_install_documentation()
        versions = {validator.validate_plugin(n) for n in validator.EXPECTED_PLUGINS}
        if len(versions) != 1:
            raise ValueError("versions differ")
        validator.validate_review_assets()
        validator.validate_release_metadata(next(iter(versions)))

    def test_valid(self):
        self.check_bundle()

    def test_versions(self):
        path = self.skill.parents[1] / ".codex-plugin/plugin.json"
        manifest = json.loads(path.read_text())
        manifest["version"] = "9.9.9"
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "versions differ"):
            self.check_bundle()

    def test_shared_reference_drift(self):
        with (self.skill / "references/security.md").open("a") as f:
            f.write("\nChanged independently.\n")
        with self.assertRaisesRegex(ValueError, "Shared asset mismatch"):
            self.check_bundle()

    def test_shared_script_drift(self):
        with (self.skill / "scripts/review_snapshot.py").open("a") as f:
            f.write("\n# drift\n")
        with self.assertRaisesRegex(ValueError, "Shared asset mismatch"):
            self.check_bundle()

    def test_missing_reference(self):
        (self.skill / "references/security.md").unlink()
        with self.assertRaisesRegex(ValueError, "Missing required reference"):
            self.check_bundle()

    def test_orphan_reference(self):
        (self.skill / "references/unreachable.md").write_text("Never routed.")
        with self.assertRaisesRegex(ValueError, "Unreachable"):
            self.check_bundle()

    def test_nested_orphan_reference(self):
        nested = self.skill / "references/nested"
        nested.mkdir()
        (nested / "unreachable.md").write_text("Never routed.")
        with self.assertRaisesRegex(ValueError, "Unreachable"):
            self.check_bundle()

    def test_missing_link_target(self):
        with (self.skill / "SKILL.md").open("a") as f:
            f.write("\n`references/absent.md`\n")
        with self.assertRaisesRegex(ValueError, "Missing or escaping"):
            self.check_bundle()

    def test_forbidden_authorization_exclusion(self):
        with (self.skill / "SKILL.md").open("a") as f:
            f.write("\nIgnore pure permission/authorization findings.\n")
        with self.assertRaisesRegex(ValueError, "Unsafe authorization"):
            self.check_bundle()

    def test_instruction_size(self):
        with (self.skill / "SKILL.md").open("a") as f:
            f.write("x" * 12001)
        with self.assertRaisesRegex(ValueError, "size limit"):
            self.check_bundle()

    def test_missing_fixture(self):
        (self.root / "tests/security-review-cases.md").unlink()
        with self.assertRaisesRegex(ValueError, "Missing or empty review fixture"):
            self.check_bundle()

    def test_empty_fixture(self):
        (self.root / "tests/security-review-cases.md").write_text(" \n")
        with self.assertRaisesRegex(ValueError, "Missing or empty review fixture"):
            self.check_bundle()

    def test_implicit_delivery(self):
        path = self.root / "plugins/pr-review-and-commit/skills/pr-review-and-commit/agents/openai.yaml"
        path.write_text(path.read_text().replace("false", "true"))
        with self.assertRaisesRegex(ValueError, "Invocation policy"):
            self.check_bundle()

    def test_prompt_mismatch(self):
        path = self.skill / "agents/openai.yaml"
        text = path.read_text().replace('  default_prompt:', '  unused_prompt:')
        path.write_text(text)
        with self.assertRaisesRegex(ValueError, "Default prompt"):
            self.check_bundle()

    def test_readme_pin(self):
        p = self.root / "README.md"
        version = validator.validate_plugin("github-pr-review-fix")
        p.write_text(p.read_text().replace(f"`v{version}`", "`v0.0.0`"))
        with self.assertRaisesRegex(ValueError, "release pin"):
            validator.validate_release_metadata(version)

    def test_changelog_version(self):
        p = self.root / "CHANGELOG.md"
        version = validator.validate_plugin("github-pr-review-fix")
        p.write_text(p.read_text().replace(f"## {version} -", "## 0.0.0 -", 1))
        with self.assertRaisesRegex(ValueError, "changelog version"):
            validator.validate_release_metadata(version)

    def test_optional_private_markers_are_case_insensitive(self):
        (self.root / "example.md").write_text("ORG-PRIVATE-EXAMPLE")
        with patch.dict(os.environ, {"PR_REVIEW_PRIVATE_MARKERS": '["org-private-example"]'}):
            with self.assertRaisesRegex(ValueError, "value withheld"):
                validator.validate_public_files()

    def test_generic_private_path(self):
        (self.root / "example.md").write_text('/' + 'Users/example/private')
        with self.assertRaisesRegex(ValueError, "value withheld"):
            validator.validate_public_files()

    def test_archive_scan_includes_hidden_manifests(self):
        path = self.root / ".agents/private-example.md"
        path.write_text('/' + 'home/example/private')
        with self.assertRaisesRegex(ValueError, "value withheld"):
            validator.validate_public_files()

    def test_no_private_markers_needed(self):
        validator.validate_public_files()


if __name__ == "__main__":
    unittest.main()
