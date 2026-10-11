"""Black-box tests; Git mutations occur only inside disposable fixture repos."""

from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ("github-pr-review-fix", "pr-review-and-commit")
SCRIPTS = [ROOT / "plugins" / name / "skills" / name / "scripts" / "review_snapshot.py"
           for name in PLUGINS]


@unittest.skipUnless(shutil.which("git"), "Git is required")
class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "--quiet")
        self.git("config", "user.email", "snapshot@example.invalid")
        self.git("config", "user.name", "Snapshot Fixture")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.hooksPath", str(self.root / "no-hooks"))
        self.git("config", "core.fileMode", "true")
        (self.repo / "seed").write_text("seed\n")
        self.base = self.commit()
        self.output = self.root / "snapshot"

    def git(self, *args, input=None, check=True):
        env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        return subprocess.run(["git", "-C", str(self.repo), *args], input=input,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              check=check, env=env).stdout

    def commit(self, stage=True):
        if stage:
            self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "fixture")
        return self.git("rev-parse", "HEAD").decode().strip()

    def command(self, *args, check=True, script=None):
        result = subprocess.run([sys.executable, str(script or SCRIPTS[0]), *map(str, args)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check:
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        return result

    def capture(self, head=None, base=None, output=None, check=True):
        return self.command("capture", "--repo", self.repo, "--base", base or self.base,
                            "--head", head or self.base, "--output", output or self.output,
                            check=check)

    def index(self):
        return [json.loads(line) for line in (self.output / "index.jsonl").read_bytes().splitlines()]

    def test_bundles_are_identical_and_both_entrypoints_run(self):
        self.assertEqual(SCRIPTS[0].read_bytes(), SCRIPTS[1].read_bytes())
        result = self.command("capture", "--repo", self.repo, "--base", self.base,
                              "--head", self.base, "--output", self.output, script=SCRIPTS[1])
        self.assertEqual(json.loads(result.stdout)["files"], 0)

    def test_add_delete_rename_and_hostile_paths(self):
        old = self.repo / 'old\t"name\n.txt'
        old.write_text("unchanged rename contents\n" * 10)
        (self.repo / "deleted").write_text("gone\n")
        base = self.commit()
        new_name = '-new\t"$(touch exploit)\n.txt'
        old.rename(self.repo / new_name)
        (self.repo / "deleted").unlink()
        added = "unicode-\u00e9-\U0001f600.txt"
        (self.repo / added).write_text("added\n")
        bad_utf8 = os.fsdecode(b"invalid-\xff.txt")
        self.git("add", "--all")
        blob = self.git("hash-object", "-w", "--stdin", input=b"invalid UTF-8 path\n").decode().strip()
        self.git("update-index", "--add", "--cacheinfo", "100644", blob, bad_utf8)
        head = self.commit(stage=False)
        self.capture(head, base)
        entries = self.index()
        self.assertEqual(len(entries), 4)
        rename = next(item for item in entries if item["status"].startswith("R"))
        self.assertEqual((rename["old_path"], rename["new_path"]), (old.name, new_name))
        self.assertEqual(rename["hunks"], [])
        self.assertEqual(next(item for item in entries if item["status"] == "D")["new_path"], None)
        self.assertEqual({item["new_path"] for item in entries if item["status"] == "A"},
                         {added, bad_utf8})
        self.assertFalse((self.repo / "exploit").exists())

    def test_binary_mode_symlink_submodule_and_lfs(self):
        (self.repo / "binary").write_bytes(b"\0old")
        (self.repo / "executable").write_text("#!/bin/sh\n")
        (self.repo / "link").symlink_to("seed")
        self.git("add", "--all")
        self.git("update-index", "--add", "--cacheinfo", "160000", self.base, "module")
        base = self.commit(stage=False)
        (self.repo / "binary").write_bytes(b"\0new")
        (self.repo / "executable").chmod(0o755)
        (self.repo / "link").unlink()
        (self.repo / "link").symlink_to("executable")
        (self.repo / "large").write_text("version https://git-lfs.github.com/spec/v1\n"
                                        + "oid sha256:" + "a" * 64 + "\nsize 9000\n")
        self.git("add", "--all")
        self.git("update-index", "--add", "--cacheinfo", "160000", base, "module")
        head = self.commit(stage=False)
        self.capture(head, base)
        entries = {item["new_path"]: item for item in self.index()}
        for name, kind in (("binary", "binary"), ("executable", "mode-only"),
                           ("link", "symlink"), ("module", "submodule"), ("large", "lfs-pointer")):
            self.assertIn(kind, entries[name]["classes"])
        self.assertEqual(entries["executable"]["hunks"], [])
        self.assertEqual(entries["executable"]["old_mode"], "100644")
        self.assertEqual(entries["executable"]["new_mode"], "100755")

    def test_type_change_keeps_both_patch_sections(self):
        (self.repo / "seed").unlink()
        (self.repo / "seed").symlink_to("target")
        head = self.commit()
        self.capture(head)
        entry = self.index()[0]
        self.assertEqual(entry["status"], "T")
        self.assertIn("symlink", entry["classes"])
        patch = (self.output / "patch.diff").read_bytes()
        self.assertEqual(patch.count(b"diff --git "), 2)
        self.assertEqual(len(entry["hunks"]), 2)
        self.assertEqual(entry["patch_end"], len(patch))
        self.assertIn(b"-seed", patch[entry["hunks"][0]["start"]:entry["hunks"][0]["end"]])
        self.assertIn(b"+target", patch[entry["hunks"][1]["start"]:entry["hunks"][1]["end"]])
        self.assertNotIn(b"diff --git", patch[entry["hunks"][0]["start"]:entry["hunks"][0]["end"]])

    def test_hunk_ranges_point_to_exact_frozen_patch(self):
        (self.repo / "lines").write_text("".join(f"line {i}\n" for i in range(40)))
        base = self.commit()
        lines = (self.repo / "lines").read_text().splitlines(keepends=True)
        lines[2], lines[35] = "changed early\n", "changed late\n"
        (self.repo / "lines").write_text("".join(lines))
        head = self.commit()
        self.capture(head, base)
        entry = self.index()[0]
        patch = (self.output / "patch.diff").read_bytes()
        self.assertEqual(len(entry["hunks"]), 2)
        self.assertEqual(entry["patch_end"], len(patch))
        for hunk in entry["hunks"]:
            text = patch[hunk["start"]:hunk["end"]]
            self.assertTrue(text.startswith(b"@@ "))
            self.assertIn(b"+changed ", text)
            self.assertEqual(hunk["old_count"], hunk["new_count"])
        (self.repo / "lines").write_text("dirty unrelated working tree\n")
        self.assertEqual(patch, (self.output / "patch.diff").read_bytes())

    def test_empty_diff_and_eof_page(self):
        self.capture()
        self.assertEqual(self.index(), [])
        result = self.command("page", "--snapshot", self.output, "--artifact", "patch.diff")
        page = json.loads(result.stdout)
        self.assertTrue(page["eof"])
        self.assertEqual(page["next_offset"], 0)
        self.assertEqual(page["data"], "")

    def test_long_lines_bounded_pages_reconstruct_exact_bytes(self):
        (self.repo / "long").write_bytes((b'"\\\t' + "\u00e9".encode()) * 700 + b"\n")
        head = self.commit()
        self.capture(head)
        for artifact in ("patch.diff", "index.jsonl"):
            offset = 0
            reconstructed = bytearray()
            mid_line_seen = False
            while True:
                result = self.command("page", "--snapshot", self.output, "--artifact", artifact,
                                      "--offset", offset, "--max-bytes", 512)
                self.assertLessEqual(len(result.stdout), 512)
                page = json.loads(result.stdout)
                reconstructed.extend(page["data"].encode("utf-8", "surrogateescape"))
                mid_line_seen |= page["ends_mid_line"]
                if page["eof"]:
                    break
                self.assertGreater(page["next_offset"], offset)
                offset = page["next_offset"]
            self.assertEqual(bytes(reconstructed), (self.output / artifact).read_bytes())
            self.assertTrue(mid_line_seen)

    def test_very_long_line_does_not_create_fake_hunks(self):
        (self.repo / "long").write_bytes(b"x" * 65535 + b"diff --git fake\n" + b"z" * 150000)
        head = self.commit()
        self.capture(head)
        self.assertEqual(len(self.index()), 1)
        self.assertEqual(len(self.index()[0]["hunks"]), 1)
        self.assertEqual(self.index()[0]["hunks"][0]["end"], (self.output / "patch.diff").stat().st_size)

    def test_shallow_repository_uses_available_objects_without_history(self):
        (self.repo / "seed").write_text("next\n")
        base = self.commit()
        (self.repo / "seed").write_text("last\n")
        head = self.commit()
        clone = self.root / "shallow"
        self.git("clone", "--quiet", "--depth=2", self.repo.as_uri(), str(clone))
        self.repo = clone
        self.assertEqual(self.git("rev-parse", "--is-shallow-repository"), b"true\n")
        self.capture(head, base)
        self.assertEqual(len(self.index()), 1)
        missing = self.root / "missing-history"
        result = self.capture(head, self.base, missing, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((missing / "manifest.json").exists())

    def test_abbreviated_or_noncommit_objects_are_rejected(self):
        for base in (self.base[:10], "HEAD", self.git("rev-parse", "HEAD^{tree}").decode().strip(), "f" * 40):
            result = self.capture(base=base, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(self.output.exists())

    def test_output_inside_repo_or_git_directory_is_rejected(self):
        for output in (self.repo / "snapshot", self.repo / ".git" / "snapshot"):
            result = self.capture(output=output, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())

    def test_existing_outputs_and_symlink_alias_into_repository_are_rejected(self):
        self.output.mkdir()
        sentinel = self.output / "patch.diff"
        sentinel.write_text("keep")
        self.assertNotEqual(self.capture(check=False).returncode, 0)
        self.assertEqual(sentinel.read_text(), "keep")
        alias = self.root / "alias"
        alias.symlink_to(self.repo, target_is_directory=True)
        self.assertNotEqual(self.capture(output=alias / "snapshot", check=False).returncode, 0)
        leaf = self.root / "leaf"
        leaf.symlink_to(self.output, target_is_directory=True)
        self.assertNotEqual(self.capture(output=leaf, check=False).returncode, 0)

    def test_external_diff_and_textconv_are_not_executed(self):
        marker = self.root / "executed"
        driver = self.root / "driver"
        driver.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 1\n")
        driver.chmod(0o755)
        (self.repo / ".gitattributes").write_text("seed diff=hostile\n")
        (self.repo / "seed").write_text("changed\n")
        head = self.commit()
        self.git("config", "diff.external", str(driver))
        self.git("config", "diff.hostile.command", str(driver))
        self.git("config", "diff.hostile.textconv", str(driver))
        self.capture(head)
        self.assertFalse(marker.exists())
        self.assertIn(b"+changed", (self.output / "patch.diff").read_bytes())

    def test_missing_blob_acquisition_never_has_complete_manifest(self):
        (self.repo / "seed").write_text("changed\n")
        head = self.commit()
        blob = self.git("rev-parse", head + ":seed").decode().strip()
        (self.repo / ".git" / "objects" / blob[:2] / blob[2:]).unlink()
        result = self.capture(head, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.output / "manifest.json").exists())

    def test_missing_promisor_blob_does_not_execute_transport(self):
        (self.repo / "seed").write_text("changed\n")
        head = self.commit()
        blob = self.git("rev-parse", head + ":seed").decode().strip()
        (self.repo / ".git" / "objects" / blob[:2] / blob[2:]).unlink()
        marker = self.root / "transport-executed"
        transport = self.root / "transport"
        transport.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 1\n")
        transport.chmod(0o755)
        self.git("config", "core.repositoryformatversion", "1")
        self.git("config", "extensions.partialClone", "origin")
        self.git("config", "remote.origin.url", "ext::" + str(transport))
        self.git("config", "remote.origin.promisor", "true")
        self.git("config", "protocol.ext.allow", "always")
        self.assertNotEqual(self.capture(head, check=False).returncode, 0)
        self.assertFalse(marker.exists())
        self.assertFalse((self.output / "manifest.json").exists())

    def test_sha256_commit_ids_when_supported(self):
        repo = self.root / "sha256"
        repo.mkdir()
        result = subprocess.run(["git", "init", "--quiet", "--object-format=sha256", str(repo)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode:
            self.skipTest("Git does not support SHA-256 repositories")
        self.repo = repo
        self.git("config", "user.name", "Snapshot Fixture")
        self.git("config", "user.email", "snapshot@example.invalid")
        self.git("config", "core.hooksPath", str(self.root / "no-hooks"))
        (repo / "seed").write_text("before\n")
        base = self.commit()
        (repo / "seed").write_text("after\n")
        head = self.commit()
        self.capture(head, base)
        self.assertEqual(len(base), 64)
        self.assertEqual(len(self.index()[0]["new_blob"]), 64)

    def test_tampered_artifacts_and_incomplete_snapshots_are_rejected(self):
        self.capture()
        (self.output / "patch.diff").write_text("tampered")
        result = self.command("page", "--snapshot", self.output, "--artifact", "patch.diff", check=False)
        self.assertNotEqual(result.returncode, 0)
        (self.output / "manifest.json").unlink()
        self.assertNotEqual(self.command("page", "--snapshot", self.output, check=False).returncode, 0)

    def test_invalid_page_caps_offsets_and_symlinks_are_rejected(self):
        self.capture()
        for option, value in (("--max-bytes", "511"), ("--max-bytes", "65537"),
                              ("--offset", "-1"), ("--offset", "1")):
            self.assertNotEqual(self.command("page", "--snapshot", self.output,
                                            option, value, check=False).returncode, 0)
        (self.output / "index.jsonl").unlink()
        (self.output / "index.jsonl").symlink_to(self.output / "patch.diff")
        self.assertNotEqual(self.command("page", "--snapshot", self.output, check=False).returncode, 0)

    def test_repository_working_tree_and_index_are_untouched(self):
        (self.repo / "seed").write_text("committed\n")
        head = self.commit()
        (self.repo / "seed").write_text("staged\n")
        self.git("add", "seed")
        (self.repo / "seed").write_text("unstaged\n")
        before = self.git("status", "--porcelain=v1", "-z")
        index_before = (self.repo / ".git" / "index").read_bytes()
        self.capture(head)
        self.assertEqual(before, self.git("status", "--porcelain=v1", "-z"))
        self.assertEqual(index_before, (self.repo / ".git" / "index").read_bytes())
        self.assertEqual(self.git("rev-parse", "HEAD").decode().strip(), head)


if __name__ == "__main__":
    unittest.main()
