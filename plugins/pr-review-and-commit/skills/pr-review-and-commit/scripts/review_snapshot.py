#!/usr/bin/env python3
"""Freeze a two-commit diff without checking out or executing repository code.

capture --repo ROOT --base FULL_OID --head FULL_OID --output NEW_EXTERNAL_DIR
page --snapshot DIR --artifact index.jsonl --offset 0 --max-bytes 12000

The caller establishes repository identity and comparison semantics (for example,
passes an already verified merge-base). This tool validates local commit objects,
not remote PR identity. Capture writes patch.diff, index.jsonl and manifest.json.
Index and hunk byte ranges are half-open offsets in patch.diff. Page offsets are
bytes, never line numbers; use next_offset until eof, including for long lines.
Acquisition completeness is not inspection, semantic coverage, or a clean review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
ARTIFACTS = ("index.jsonl", "patch.diff")


def encode(value):
    # ASCII JSON safely represents control characters and undecodable Git paths.
    return json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode("ascii")


def git(repo, *args, output=None, input=None):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1",
               GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0", LC_ALL="C")
    command = ["git", "--no-pager", "-C", str(repo), "-c", "protocol.allow=never"]
    # Explicit protocol settings take precedence over protocol.allow. Disable all
    # configured transports too, including custom remote helpers in old Git.
    configs = subprocess.run(command + ["config", "--null", "--name-only",
                              "--get-regexp", r"^protocol\..*\.allow$"],
                             env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if configs.returncode not in (0, 1):
        raise ValueError("Cannot inspect Git transport configuration")
    for key in configs.stdout.split(b"\0"):
        if key:
            command.extend(["-c", os.fsdecode(key) + "=never"])
    command.extend(["-c", "core.quotePath=true", *args])
    result = subprocess.run(command, env=env, input=input, stdout=output or subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if result.returncode:
        # Do not print repository-controlled stderr (it can be enormous or contain
        # secrets). A failed command never creates the completion manifest.
        raise ValueError("Git acquisition failed: " + args[0])
    return result.stdout


def inventory(raw):
    fields = raw.split(b"\0")
    if fields.pop() != b"":
        raise ValueError("Unterminated Git inventory")
    entries = []
    position = 0
    while position < len(fields):
        header = fields[position].decode("ascii").split()
        if len(header) != 5 or not re.fullmatch(r":[0-7]{6}", header[0]):
            raise ValueError("Invalid Git inventory header")
        old_mode, new_mode, old_blob, new_blob, status = header
        path_count = 2 if status[0] in "RC" else 1
        paths = fields[position + 1:position + 1 + path_count]
        if len(paths) != path_count or any(not path for path in paths):
            raise ValueError("Missing Git inventory path")
        old_path = os.fsdecode(paths[0]) if status[0] != "A" else None
        new_path = os.fsdecode(paths[-1]) if status[0] != "D" else None
        entries.append({"id": f"f{len(entries) + 1:06d}", "status": status,
                        "old_path": old_path, "new_path": new_path,
                        "old_mode": old_mode[1:], "new_mode": new_mode,
                        "old_blob": old_blob, "new_blob": new_blob, "hunks": []})
        position += 1 + path_count
    return entries


def lfs_blobs(repo, entries):
    blobs = sorted({entry[side + "_blob"] for entry in entries for side in ("old", "new")
                    if entry[side + "_mode"] not in ("000000", "160000")})
    if not blobs:
        return set()
    sizes = git(repo, "cat-file", "--batch-check", input=("\n".join(blobs) + "\n").encode())
    small = []
    rows = sizes.splitlines()
    if len(rows) != len(blobs):
        raise ValueError("Incomplete blob inventory")
    for oid, row in zip(blobs, rows):
        parts = row.decode("ascii").split()
        if len(parts) != 3 or parts[:2] != [oid, "blob"]:
            raise ValueError("Missing local blob")
        if int(parts[2]) <= 1024:
            small.append(oid)
    if not small:
        return set()
    content = git(repo, "cat-file", "--batch", input=("\n".join(small) + "\n").encode())
    found = set()
    position = 0
    for oid in small:
        end = content.index(b"\n", position)
        header = content[position:end].decode("ascii").split()
        if len(header) != 3 or header[:2] != [oid, "blob"]:
            raise ValueError("Invalid blob response")
        length = int(header[2])
        body = content[end + 1:end + 1 + length]
        if len(body) != length or content[end + 1 + length:end + 2 + length] != b"\n":
            raise ValueError("Incomplete blob response")
        if body.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
            found.add(oid)
        position = end + length + 2
    return found


def index_patch(path, entries, lfs):
    current = None
    current_header = None
    section_count = 0
    count = 0
    line_start = True
    with path.open("rb") as stream:
        while True:
            offset = stream.tell()
            chunk = stream.readline(65536)
            if not chunk:
                break
            if line_start and chunk.startswith(b"diff --git "):
                if current is not None:
                    current["patch_end"] = offset
                    if current["hunks"] and "end" not in current["hunks"][-1]:
                        current["hunks"][-1]["end"] = offset
                # Git emits separate deletion/addition sections for a type
                # change, although --raw reports one T record for that path.
                if current is not None and current["status"] == "T" and chunk == current_header and section_count == 1:
                    section_count += 1
                else:
                    if count >= len(entries):
                        raise ValueError("Patch has more files than inventory")
                    current = entries[count]
                    current["patch_start"] = offset
                    current["binary"] = False
                    current_header = chunk
                    section_count = 1
                    count += 1
            elif current is None:
                raise ValueError("Patch lacks a file header")
            elif line_start:
                match = HUNK.match(chunk)
                if match:
                    if current["hunks"] and "end" not in current["hunks"][-1]:
                        current["hunks"][-1]["end"] = offset
                    old_start, old_count, new_start, new_count = match.groups()
                    current["hunks"].append({"id": f"{current['id']}-h{len(current['hunks']) + 1:06d}",
                        "start": offset, "old_start": int(old_start),
                        "old_count": int(old_count) if old_count is not None else 1,
                        "new_start": int(new_start),
                        "new_count": int(new_count) if new_count is not None else 1})
                elif chunk.startswith(b"Binary files ") or chunk.startswith(b"GIT binary patch"):
                    current["binary"] = True
            line_start = chunk.endswith(b"\n")
        if current is not None:
            current["patch_end"] = stream.tell()
            if current["hunks"] and "end" not in current["hunks"][-1]:
                current["hunks"][-1]["end"] = stream.tell()
    if count != len(entries):
        raise ValueError("Patch and inventory file counts differ")
    for entry in entries:
        classes = set()
        for side in ("old", "new"):
            mode = entry[side + "_mode"]
            if mode == "160000":
                classes.add("submodule")
            elif mode == "120000":
                classes.add("symlink")
            elif mode != "000000":
                classes.add("binary" if entry["binary"] else
                            "text" if entry["hunks"] else "regular-unclassified")
            if entry[side + "_blob"] in lfs:
                classes.add("lfs-pointer")
        entry["classes"] = sorted(classes)
        if entry["old_blob"] == entry["new_blob"] and entry["old_mode"] != entry["new_mode"]:
            entry["classes"].append("mode-only")


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            result.update(chunk)
    return {"bytes": path.stat().st_size, "sha256": result.hexdigest()}


def capture(args):
    repo = Path(args.repo).resolve(strict=True)
    root = Path(os.fsdecode(git(repo, "rev-parse", "--show-toplevel").removesuffix(b"\n"))).resolve()
    if root != repo:
        raise ValueError("--repo must identify the repository root")
    for oid in (args.base, args.head):
        if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", oid):
            raise ValueError("Expected full lowercase commit object IDs")
        if git(repo, "cat-file", "-t", oid) != b"commit\n":
            raise ValueError("Expected a local commit object")
    requested = Path(args.output).absolute()
    output = requested.parent.resolve(strict=True) / requested.name
    git_dirs = [repo]
    for flag in ("--absolute-git-dir", "--git-common-dir"):
        directory = Path(os.fsdecode(git(repo, "rev-parse", flag).removesuffix(b"\n")))
        git_dirs.append((repo / directory).resolve())
    if any(output == directory or directory in output.parents for directory in git_dirs):
        raise ValueError("Output must be outside the repository and its Git directories")
    output.mkdir(mode=0o700)  # Exclusive: never overwrite a prior run or follow a leaf symlink.
    diff = ["diff", "--no-ext-diff", "--no-textconv", "--no-color", "--no-relative",
            "--no-renames", "--find-renames=50%", "--ignore-submodules=none", "--submodule=short",
            "--src-prefix=a/", "--dst-prefix=b/", "--diff-algorithm=myers", "--no-indent-heuristic",
            "--output-indicator-new=+", "--output-indicator-old=-",
            "--output-indicator-context= ", args.base, args.head, "--"]
    entries = inventory(git(repo, *diff[:1], "--raw", "--no-abbrev", "-z", *diff[1:]))
    with (output / "patch.diff").open("xb") as stream:
        git(repo, *diff[:1], "--patch", "--unified=3", "--full-index", *diff[1:], output=stream)
    index_patch(output / "patch.diff", entries, lfs_blobs(repo, entries))
    with (output / "index.jsonl").open("xb") as stream:
        for entry in entries:
            stream.write(encode(entry) + b"\n")
    manifest = {"schema": 1, "repo": str(repo), "base": args.base, "head": args.head,
                "acquisition_complete": True, "files": len(entries),
                "artifacts": {name: digest(output / name) for name in ARTIFACTS}}
    with (output / "manifest.json").open("xb") as stream:
        stream.write(encode(manifest) + b"\n")
    print(json.dumps({"acquisition_complete": True, "files": len(entries),
                      "hunks": sum(len(entry["hunks"]) for entry in entries),
                      "note": "Acquisition only; no semantic coverage is established."}))


def page(args):
    snapshot = Path(args.snapshot).resolve(strict=True)
    manifest_path = snapshot / "manifest.json"
    artifact = snapshot / args.artifact
    if any(path.is_symlink() or not path.is_file() for path in (manifest_path, artifact)):
        raise ValueError("Snapshot files must be regular files, not symlinks")
    manifest = json.loads(manifest_path.read_text(encoding="ascii"))
    if manifest.get("schema") != 1 or manifest.get("acquisition_complete") is not True:
        raise ValueError("Snapshot acquisition is incomplete")
    expected = manifest["artifacts"][args.artifact]
    if digest(artifact) != expected:
        raise ValueError("Snapshot artifact changed; capture a new snapshot")
    total = expected["bytes"]
    if not 0 <= args.offset <= total:
        raise ValueError("Offset is outside the artifact")
    with artifact.open("rb") as stream:
        stream.seek(max(0, args.offset - 1))
        starts_mid_line = args.offset > 0 and stream.read(1) != b"\n"
        stream.seek(args.offset)
        data = stream.read(args.max_bytes)
    # JSON escaping can expand bytes (especially invalid UTF-8). Bound the entire
    # response, with a continuation even when a single line exceeds the cap.
    low, high = 0, len(data)
    while low <= high:
        size = (low + high) // 2
        end = args.offset + size
        response = {"artifact": args.artifact, "offset": args.offset, "next_offset": end,
                    "total_bytes": total, "eof": end == total,
                    "starts_mid_line": starts_mid_line,
                    "ends_mid_line": end < total and (size == 0 or data[size - 1] != 10),
                    "data": data[:size].decode("utf-8", "surrogateescape")}
        rendered = encode(response) + b"\n"
        if len(rendered) <= args.max_bytes:
            selected = rendered
            low = size + 1
        else:
            high = size - 1
    if high <= 0 and args.offset < total:
        raise ValueError("Page cap is too small to advance")
    sys.stdout.buffer.write(selected)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    acquire = commands.add_parser("capture", help="Acquire an immutable local comparison")
    for name in ("repo", "base", "head", "output"):
        acquire.add_argument("--" + name, required=True)
    pages = commands.add_parser("page", help="Read a bounded artifact page, continuing by byte offset")
    pages.add_argument("--snapshot", required=True)
    pages.add_argument("--artifact", choices=ARTIFACTS, default="index.jsonl")
    pages.add_argument("--offset", type=int, default=0)
    pages.add_argument("--max-bytes", type=int, default=12000)
    args = parser.parse_args()
    if args.command == "page" and not 512 <= args.max_bytes <= 65536:
        parser.error("--max-bytes must be between 512 and 65536")
    try:
        capture(args) if args.command == "capture" else page(args)
    except (OSError, ValueError, KeyError, IndexError, UnicodeError) as error:
        print("Snapshot failed: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
