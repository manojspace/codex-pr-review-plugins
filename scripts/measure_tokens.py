#!/usr/bin/env python3
"""Development-only, offline JSONL usage measurement; never emits rollout bodies.

Usage: measure_tokens.py manifest.json --rollout /explicit/rollout.jsonl [...]
Manifest: {"tasks": [{"id": "run-1", "thread_id": "opaque-id",
  "turn_ids": ["opaque-turn"], "parent_task_id": null,
  "children_complete": true}]}. Instead of turn_ids, supply start/end ISO times
(start inclusive, end exclusive). Child followups need separate task windows.
Only supplied files and windows are read. Output paths and raw text are omitted.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys


FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens")
SAFE_ID = re.compile(r"[A-Za-z0-9_.:/-]{1,160}\Z")


def opaque(value):
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
        raise ValueError("Invalid identifier metadata")
    return value


def instant(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Window timestamps need a timezone")
    return result


def usage(value):
    value = value if isinstance(value, dict) else {}
    result = {key: value.get(key) for key in FIELDS}
    for key, number in result.items():
        if type(number) is not int or number < 0:
            result[key] = None
    if (result["input_tokens"] is not None
            and result["cached_input_tokens"] is not None
            and result["cached_input_tokens"] > result["input_tokens"]):
        result["cached_input_tokens"] = None
    return result


def bucket():
    return {"sum": dict.fromkeys(FIELDS, 0), "unknown": set(), "events": 0}


def add(target, values):
    target["events"] += 1
    for key, value in values.items():
        if value is None:
            target["unknown"].add(key)
        else:
            target["sum"][key] += value


def tokens(target):
    result = {key: (None if key in target["unknown"] or not target["events"]
                    else value) for key, value in target["sum"].items()}
    result["uncached_input_tokens"] = (
        result["input_tokens"] - result["cached_input_tokens"]
        if result["input_tokens"] is not None and result["cached_input_tokens"] is not None
        else None)
    return result


def checkpoint(task, key, timestamp, values):
    old = task[key]
    if old is None or old[0] is None and timestamp is not None or (
            old[0] is not None and timestamp is not None and timestamp > old[0]):
        task[key] = (timestamp, values)
    elif old[0] == timestamp and old[1] != values:
        task["warnings"].add("ambiguous_counter_snapshots")
        task["per_call"]["unknown"].update(FIELDS)
        task["cumulative"]["unknown"].update(FIELDS)


def prepare(manifest):
    if not isinstance(manifest, dict) or not isinstance(manifest.get("tasks"), list):
        raise ValueError("Manifest needs a tasks array")
    tasks = []
    for spec in manifest.get("tasks", []):
        task = {"id": opaque(spec["id"]), "thread_id": opaque(spec["thread_id"]),
                "parent_task_id": spec.get("parent_task_id"),
                "turn_ids": set(map(opaque, spec.get("turn_ids", []))),
                "start": instant(spec["start"]) if spec.get("start") else None,
                "end": instant(spec["end"]) if spec.get("end") else None,
                "children_complete": spec.get("children_complete") is True,
                "per_call": bucket(), "cumulative": bucket(), "warnings": set(),
                "calls": {}, "usage_turns": set(), "legacy_turns": set(), "tools": set(), "outputs": set(), "output_bytes": 0,
                "unknown_legacy_turns": set(), "proven_turn_baselines": set(),
                "last_modern_snapshot": None, "last_legacy_snapshot": None,
                "output_unknown": False, "models": set(), "efforts": set(),
                "started": {}, "finished": {}, "observed_turns": set(),
                "seen": False, "parent_thread_id": None, "duplicates": 0,
                "resets": 0, "legacy_resets": 0, "compactions": 0}
        if not task["turn_ids"] and not (task["start"] and task["end"]):
            raise ValueError("Every task needs turn_ids or both start/end")
        if task["start"] and task["end"] and task["start"] >= task["end"]:
            raise ValueError("Window start must precede end")
        tasks.append(task)
    by_id = {task["id"]: task for task in tasks}
    if not tasks or len(by_id) != len(tasks):
        raise ValueError("Tasks must have distinct identifiers")
    for task in tasks:
        ancestors = {task["id"]}
        parent = task["parent_task_id"]
        while parent is not None:
            if parent not in by_id or parent in ancestors:
                raise ValueError("Parent task is missing or cyclic")
            ancestors.add(parent)
            parent = by_id[parent]["parent_task_id"]
    return tasks


def selected(tasks, thread, turn, timestamp):
    matches = [task for task in tasks if task["thread_id"] == thread
               and (not task["turn_ids"] or turn in task["turn_ids"])
               and (task["start"] is None or timestamp is not None and timestamp >= task["start"])
               and (task["end"] is None or timestamp is not None and timestamp < task["end"])]
    if len(matches) > 1:
        raise ValueError("Task windows overlap; attribution would double count")
    return matches


def measure(manifest, paths):
    tasks = prepare(manifest)
    # One history per thread, even when explicit files overlap or are repeated.
    previous = {}
    seen_legacy = set()
    file_warnings = set()
    for path in dict.fromkeys(Path(path).resolve() for path in paths):
        thread = turn = None
        parent_thread = None
        try:
            stream = path.open(encoding="utf-8")
        except OSError:
            file_warnings.add("unreadable_rollout")
            continue
        with stream:
            for line in stream:
                try:
                    event = json.loads(line)
                    if not isinstance(event, dict):
                        raise ValueError()
                except (ValueError, UnicodeError):
                    file_warnings.add("malformed_or_truncated_record")
                    continue
                payload = event.get("payload")
                if not isinstance(payload, dict):
                    continue
                kind = event.get("type")
                subtype = payload.get("type")
                try:
                    timestamp = instant(event["timestamp"])
                except (KeyError, TypeError, ValueError, AttributeError):
                    timestamp = None
                if kind == "session_meta":
                    thread = payload.get("id")
                    parent_thread = payload.get("parent_thread_id")
                    for task in tasks:
                        if task["thread_id"] == thread:
                            task["seen"] = True
                            task["parent_thread_id"] = parent_thread
                    continue
                if kind == "turn_context" or subtype == "task_started":
                    turn = payload.get("turn_id", turn)
                event_thread = payload.get("thread_id", thread)
                event_turn = payload.get("turn_id", turn)
                active = selected(tasks, event_thread, event_turn, timestamp)
                for task in active:
                    task["seen"] = True
                    if isinstance(event_turn, str) and SAFE_ID.fullmatch(event_turn):
                        task["observed_turns"].add(event_turn)
                    if timestamp is None:
                        task["warnings"].add("missing_timestamp")
                    if kind == "turn_context":
                        for source, target in (("model", "models"), ("effort", "efforts")):
                            value = payload.get(source)
                            if isinstance(value, str) and SAFE_ID.fullmatch(value):
                                task[target].add(value)
                    if subtype == "task_started" and timestamp:
                        task["started"][event_turn] = timestamp
                    if subtype in ("task_complete", "task_completed") and timestamp:
                        task["finished"][event_turn] = timestamp
                    if subtype in ("turn_aborted", "task_aborted"):
                        task["warnings"].add("interrupted_task")
                    if kind == "compacted" or subtype == "context_compacted":
                        task["compactions"] += 1
                    if kind == "response_item" and subtype in (
                            "function_call", "custom_tool_call", "function_call_output", "custom_tool_call_output"):
                        call_id = payload.get("call_id") or payload.get("id")
                        if not isinstance(call_id, str):
                            task["warnings"].add("missing_tool_identity")
                            continue
                        if subtype.endswith("_output"):
                            if call_id not in task["outputs"]:
                                task["outputs"].add(call_id)
                                output = payload.get("output")
                                if isinstance(output, str):
                                    task["output_bytes"] += len(output.encode("utf-8"))
                                else:
                                    task["output_unknown"] = True
                        else:
                            task["tools"].add(call_id)
                if kind == "token_usage_record":
                    for task in active:
                        response_id = payload.get("response_id")
                        if not isinstance(response_id, str) or not response_id:
                            task["warnings"].add("missing_response_identity")
                            task["per_call"]["unknown"].update(FIELDS)
                            continue
                        values = usage(payload.get("usage"))
                        if response_id in task["calls"]:
                            task["duplicates"] += 1
                            if task["calls"][response_id] != values:
                                task["warnings"].add("conflicting_duplicate_usage")
                                task["per_call"]["unknown"].update(FIELDS)
                            continue
                        task["calls"][response_id] = values
                        checkpoint(task, "last_modern_snapshot", timestamp, usage(payload.get("thread_token_usage")))
                        add(task["per_call"], values)
                        turn_total = usage(payload.get("turn_token_usage"))
                        if (event_turn in task["started"] and event_turn not in task["usage_turns"]
                                and all(values[k] is not None and turn_total[k] == values[k] for k in FIELDS)):
                            task["proven_turn_baselines"].add(event_turn)
                        if (event_turn in task["started"] and event_turn not in task["usage_turns"]
                                and any(turn_total[k] is not None and values[k] is not None
                                        and turn_total[k] > values[k] for k in FIELDS)):
                            task["warnings"].add("initial_turn_usage_gap")
                            task["per_call"]["unknown"].update(FIELDS)
                        task["usage_turns"].add(event_turn)
                        if any(value is None for value in values.values()):
                            task["warnings"].add("missing_or_invalid_usage_field")
                    # Reconcile per-completion records with thread counters where exposed.
                    cumulative = usage(payload.get("thread_token_usage"))
                    key = (event_thread, "per_call")
                    old = previous.get(key)
                    identity = (event_thread, payload.get("response_id"))
                    if identity not in seen_legacy:
                        seen_legacy.add(identity)
                        if old and all(cumulative[k] is not None and old[k] is not None for k in FIELDS):
                            reset = any(cumulative[k] < old[k] for k in FIELDS)
                            for task in active:
                                if reset:
                                    task["resets"] += 1
                                elif any(cumulative[k] - old[k] != usage(payload.get("usage"))[k] for k in FIELDS):
                                    task["warnings"].add("cumulative_reconciliation_gap")
                                    task["per_call"]["unknown"].update(FIELDS)
                        previous[key] = cumulative
                elif kind == "event_msg" and subtype == "token_count":
                    info = payload.get("info") or {}
                    if not isinstance(info, dict):
                        continue
                    total = usage(info.get("total_token_usage"))
                    for task in active:
                        checkpoint(task, "last_legacy_snapshot", timestamp, total)
                    key = (event_thread, "legacy")
                    old = previous.get(key)
                    # Repeated snapshots are notifications, not additional calls.
                    if old == total:
                        continue
                    reset = old is not None and any(total[k] is not None and old[k] is not None
                                                    and total[k] < old[k] for k in FIELDS)
                    last = usage(info.get("last_token_usage"))
                    initial = old is None and total == last and total["input_tokens"] is not None
                    delta = {k: total[k] - old[k] if old is not None and not reset
                             and total[k] is not None and old[k] is not None else None for k in FIELDS}
                    if initial:
                        delta = total
                    delta = usage(delta)
                    for task in active:
                        task["legacy_turns"].add(event_turn)
                        add(task["cumulative"], delta)
                        if reset:
                            task["legacy_resets"] += 1
                        if reset or old is None and not initial:
                            task["unknown_legacy_turns"].add(event_turn)
                            task["warnings"].add("legacy_unknown_baseline_or_reset")
                    previous[key] = total
    rows = []
    for task in tasks:
        modern = bool(task["per_call"]["events"])
        chosen = task["per_call"] if modern else task["cumulative"]
        warnings = task["warnings"] | file_warnings
        if modern:
            if task["unknown_legacy_turns"] <= task["proven_turn_baselines"]:
                warnings.discard("legacy_unknown_baseline_or_reset")
            else:
                chosen["unknown"].update(FIELDS)
            if task["legacy_turns"] - task["usage_turns"]:
                warnings.add("mixed_turn_usage_sources")
                chosen["unknown"].update(FIELDS)
        if not task["seen"]:
            warnings.add("missing_thread")
        if not chosen["events"]:
            warnings.add("missing_usage")
        if not modern:
            warnings.add("model_call_count_unavailable")
        expected = task["turn_ids"] or task["observed_turns"]
        if expected - (task["usage_turns"] | task["legacy_turns"]):
            warnings.add("missing_turn_usage")
            chosen["unknown"].update(FIELDS)
        finished = bool(expected) and expected <= task["finished"].keys()
        started = bool(expected) and expected <= task["started"].keys()
        latest_modern = task["last_modern_snapshot"]
        latest_legacy = task["last_legacy_snapshot"]
        if (modern and latest_modern and latest_legacy and latest_modern[0] and latest_legacy[0]
                and latest_legacy[0] >= latest_modern[0]
                and any(latest_legacy[1][key] is not None and latest_modern[1][key] is not None
                        and latest_legacy[1][key] > latest_modern[1][key] for key in FIELDS)):
            warnings.add("final_snapshot_usage_gap")
            chosen["unknown"].update(FIELDS)
        if modern and finished and task["cumulative"]["events"] and any(
                key not in task["cumulative"]["unknown"]
                and task["cumulative"]["sum"][key] > chosen["sum"][key] for key in FIELDS):
            warnings.add("final_cumulative_usage_gap")
            chosen["unknown"].update(FIELDS)
        if not finished:
            warnings.add("unfinished_or_missing_task_end")
        if not started:
            warnings.add("missing_task_start")
        if not task["children_complete"]:
            warnings.add("descendant_inventory_unconfirmed")
        if task["parent_task_id"]:
            parent = next(item for item in tasks if item["id"] == task["parent_task_id"])
            if task["parent_thread_id"] != parent["thread_id"]:
                warnings.add("parent_relationship_unverified")
        if task["tools"] - task["outputs"] or task["output_unknown"]:
            warnings.add("missing_or_unmeasurable_tool_output")
        values = tokens(chosen)
        if any(value is None for value in values.values()):
            warnings.add("incomplete_token_totals")
        rows.append({"task_id": task["id"], "thread_id": task["thread_id"],
                     "parent_task_id": task["parent_task_id"],
                     "turn_ids": sorted(expected), "tokens": values,
                     "observed_tokens": chosen["sum"],
                     "usage_source": "per_completion" if modern else "cumulative_deltas",
                     "model_calls": len(task["calls"]) if modern else None,
                     "usage_events": chosen["events"], "duplicate_usage_events": task["duplicates"],
                     "counter_resets": task["resets"] if modern else task["legacy_resets"], "compactions": task["compactions"],
                     "tool_calls": len(task["tools"]),
                     "tool_output_bytes": None if task["output_unknown"] or task["tools"] - task["outputs"] else task["output_bytes"],
                     "models": sorted(task["models"]) or None, "efforts": sorted(task["efforts"]) or None,
                     "start": min(task["started"].values()).isoformat() if started else None,
                     "end": max(task["finished"].values()).isoformat() if finished else None,
                     "wall_seconds": (max(task["finished"].values()) - min(task["started"].values())).total_seconds()
                     if started and finished else None,
                     "complete": not warnings, "warnings": sorted(warnings)})
    totals = {}
    for key in (*FIELDS, "uncached_input_tokens"):
        values = [row["tokens"][key] for row in rows]
        totals[key] = sum(values) if all(value is not None for value in values) else None
    child_input = [row["tokens"]["input_tokens"] for row in rows if row["parent_task_id"]]
    child_threads = {row["thread_id"] for row in rows if row["parent_task_id"]}
    return {"schema_version": 1, "tasks": rows, "tokens": totals,
            "complete": all(row["complete"] for row in rows),
            "agent_task_count": sum(row["parent_task_id"] is not None for row in rows),
            "agent_thread_count": len(child_threads),
            "reused_child_task_count": len(child_input) - len(child_threads),
            "agent_input_share": sum(child_input) / totals["input_tokens"]
            if totals["input_tokens"] and all(value is not None for value in child_input) else None,
            "definitions": {"model_calls": "distinct response_id per task with per-completion usage",
                            "tool_output_bytes": "UTF-8 bytes of response_item output strings; never serialized bodies",
                            "tokens": "each declared task once; cached input is part of input",
                            "wall_seconds": "task start to task completion, not summed call latency",
                            "coverage": "only explicitly declared windows; quality and undeclared descendants are not inferred"}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--rollout", type=Path, action="append", required=True)
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = measure(manifest, args.rollout)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError):
        # Exceptions may contain file contents, paths, or raw JSON; do not print them.
        print(json.dumps({"error": "Invalid manifest or unreadable input metadata"}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
