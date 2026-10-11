"""Synthetic telemetry only: no local session history is needed by tests."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "measure_tokens", Path(__file__).resolve().parents[1] / "scripts/measure_tokens.py")
metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(metrics)


def event(kind, payload, second=0):
    return {"type": kind, "timestamp": f"2026-01-01T00:00:{second:02d}Z", "payload": payload}


def counts(inputs=100, cached=60, outputs=10):
    return {"input_tokens": inputs, "cached_input_tokens": cached, "output_tokens": outputs}


def task(task_id="main", thread="p", turn="t1", parent=None):
    return {"id": task_id, "thread_id": thread, "turn_ids": [turn],
            "parent_task_id": parent, "children_complete": True}


def start(thread="p", turn="t1", parent=None):
    return [event("session_meta", {"id": thread, "parent_thread_id": parent}),
            event("event_msg", {"type": "task_started", "turn_id": turn}),
            event("turn_context", {"turn_id": turn, "model": "test-model", "effort": "high"})]


def finish(turn="t1", second=9):
    return event("event_msg", {"type": "task_complete", "turn_id": turn}, second)


def completion(response="r1", values=None, cumulative=None, thread="p", turn="t1", second=1):
    values = counts() if values is None else values
    return event("token_usage_record", {"response_id": response, "thread_id": thread,
                 "turn_id": turn, "usage": values,
                 "thread_token_usage": values if cumulative is None else cumulative}, second)


def legacy(total, last=None, second=1):
    return event("event_msg", {"type": "token_count", "info": {
        "total_token_usage": total, "last_token_usage": total if last is None else last}}, second)


class MeasurementTests(unittest.TestCase):
    def run_metrics(self, records, tasks=None, extra=None, truncated=False):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for index, rows in enumerate([records] + (extra or [])):
                path = Path(directory) / f"rollout-{index}.jsonl"
                path.write_text("".join(json.dumps(row) + "\n" for row in rows)
                                + ('{"secret_body":"' if truncated else ""), encoding="utf-8")
                paths.append(path)
            return metrics.measure({"tasks": [task()] if tasks is None else tasks}, paths)

    def test_per_call_cache_repeated_records_and_legacy_notifications(self):
        record = completion()
        rows = start() + [record, record, legacy(counts()), legacy(counts()),
                         completion("r2", counts(50, 20, 5), counts(150, 80, 15), second=2),
                         legacy(counts(150, 80, 15), counts(50, 20, 5), second=3), finish()]
        result = self.run_metrics(rows)
        self.assertTrue(result["complete"])
        self.assertEqual(result["tokens"], {**counts(150, 80, 15), "uncached_input_tokens": 70})
        row = result["tasks"][0]
        self.assertEqual(row["model_calls"], 2)
        self.assertEqual(row["duplicate_usage_events"], 1)
        self.assertEqual(row["wall_seconds"], 9)

    def test_duplicate_explicit_files_do_not_repeat_completions(self):
        rows = start() + [completion(), finish()]
        result = self.run_metrics(rows, extra=[rows])
        self.assertEqual(result["tokens"]["input_tokens"], 100)
        self.assertTrue(result["complete"])

    def test_per_call_reset_and_compaction_keep_actual_usage(self):
        rows = start() + [completion(), event("compacted", {}),
                         completion("r2", counts(30, 0, 2), second=2), finish()]
        result = self.run_metrics(rows)
        self.assertTrue(result["complete"])
        self.assertEqual(result["tokens"]["input_tokens"], 130)
        self.assertEqual(result["tasks"][0]["counter_resets"], 1)
        self.assertEqual(result["tasks"][0]["compactions"], 1)

    def test_missing_call_detected_by_cumulative_reconciliation(self):
        rows = start() + [completion(), completion("r3", counts(20, 0, 2), counts(150, 60, 15)), finish()]
        result = self.run_metrics(rows)
        self.assertFalse(result["complete"])
        self.assertIn("cumulative_reconciliation_gap", result["tasks"][0]["warnings"])

    def test_conflicting_duplicate_is_not_summed(self):
        result = self.run_metrics(start() + [completion(), completion(values=counts(200, 60, 10)), finish()])
        self.assertEqual(result["tasks"][0]["observed_tokens"]["input_tokens"], 100)
        self.assertIsNone(result["tokens"]["input_tokens"])
        self.assertIn("conflicting_duplicate_usage", result["tasks"][0]["warnings"])

    def test_missing_first_or_final_completion_detected(self):
        record = completion()
        record["payload"]["turn_token_usage"] = counts(200, 120, 20)
        result = self.run_metrics(start() + [record, finish()])
        self.assertIn("initial_turn_usage_gap", result["tasks"][0]["warnings"])
        self.assertIsNone(result["tokens"]["input_tokens"])
        result = self.run_metrics(start() + [completion(), legacy(counts(200, 120, 20)), finish()])
        self.assertIn("final_cumulative_usage_gap", result["tasks"][0]["warnings"])

    def test_usage_without_reliable_identity_is_unknown(self):
        record = completion()
        record["payload"].pop("response_id")
        result = self.run_metrics(start() + [completion(), record, finish()])
        self.assertIsNone(result["tokens"]["input_tokens"])
        self.assertIn("missing_response_identity", result["tasks"][0]["warnings"])

    def test_missing_cache_is_unknown_not_zero(self):
        values = {"input_tokens": 100, "output_tokens": 10}
        result = self.run_metrics(start() + [completion(values=values), finish()])
        self.assertEqual(result["tokens"]["input_tokens"], 100)
        self.assertIsNone(result["tokens"]["cached_input_tokens"])
        self.assertIsNone(result["tokens"]["uncached_input_tokens"])
        self.assertFalse(result["complete"])

    def test_invalid_numbers_and_impossible_cache(self):
        for values in [counts(100, 101, 10), counts(-1, 0, 10), counts(True, 0, 10)]:
            with self.subTest(values=values):
                result = self.run_metrics(start() + [completion(values=values), finish()])
                self.assertFalse(result["complete"])
                self.assertIsNone(result["tokens"]["uncached_input_tokens"])

    def test_legacy_cumulative_snapshots_not_summed_or_claimed_as_calls(self):
        result = self.run_metrics(start() + [legacy(counts()), legacy(counts()),
                                  legacy(counts(170, 80, 20), counts(70, 20, 10), second=2), finish()])
        self.assertEqual(result["tokens"]["input_tokens"], 170)
        self.assertEqual(result["tasks"][0]["usage_events"], 2)
        self.assertIsNone(result["tasks"][0]["model_calls"])
        self.assertFalse(result["complete"])

    def test_legacy_unknown_initial_baseline_and_reset(self):
        for rows in [[legacy(counts(500, 60, 10), counts(100, 60, 10))],
                     [legacy(counts()), legacy(counts(20, 0, 1))]]:
            with self.subTest(rows=rows):
                result = self.run_metrics(start() + rows + [finish()])
                self.assertIsNone(result["tokens"]["input_tokens"])
                self.assertIn("legacy_unknown_baseline_or_reset", result["tasks"][0]["warnings"])

    def test_legacy_window_uses_prior_snapshot_as_baseline(self):
        spec = {"id": "window", "thread_id": "p", "start": "2026-01-01T00:00:02Z",
                "end": "2026-01-01T00:00:08Z", "children_complete": True}
        result = self.run_metrics(start() + [legacy(counts(), second=1),
            legacy(counts(150, 80, 15), counts(50, 20, 5), second=3)], tasks=[spec])
        self.assertEqual(result["tokens"]["input_tokens"], 50)

    def test_mixed_legacy_and_modern_turns_cannot_silently_drop_usage(self):
        spec = task()
        spec["turn_ids"] = ["t1", "t2"]
        rows = start() + [legacy(counts()), finish(),
            event("event_msg", {"type": "task_started", "turn_id": "t2"}, 10),
            completion("r2", counts(), counts(200, 120, 20), turn="t2", second=11),
            finish("t2", 19)]
        result = self.run_metrics(rows, [spec])
        self.assertFalse(result["complete"])
        self.assertIsNone(result["tokens"]["input_tokens"])
        self.assertIn("mixed_turn_usage_sources", result["tasks"][0]["warnings"])

    def test_same_turn_hybrid_cannot_hide_unknown_legacy_baseline(self):
        rows = start() + [legacy(counts(500, 300, 50), counts()),
            completion("r2", counts(50, 30, 5), counts(550, 330, 55)),
            legacy(counts(550, 330, 55), counts(50, 30, 5)), finish()]
        result = self.run_metrics(rows)
        self.assertFalse(result["complete"])
        self.assertIsNone(result["tokens"]["input_tokens"])
        self.assertIn("legacy_unknown_baseline_or_reset", result["tasks"][0]["warnings"])

    def test_finished_turn_without_usage_is_not_assumed_zero(self):
        spec = task()
        spec["turn_ids"] = ["t1", "t2"]
        rows = start() + [completion(), finish(),
            event("event_msg", {"type": "task_started", "turn_id": "t2"}, 10), finish("t2", 19)]
        result = self.run_metrics(rows, [spec])
        self.assertFalse(result["complete"])
        self.assertIsNone(result["tokens"]["input_tokens"])
        self.assertIn("missing_turn_usage", result["tasks"][0]["warnings"])

    def test_proven_modern_turn_baseline_allows_inherited_legacy_snapshot(self):
        record = completion("r1", counts(50, 30, 5), counts(550, 330, 55), second=2)
        record["payload"]["turn_token_usage"] = counts(50, 30, 5)
        rows = start() + [legacy(counts(500, 300, 50), counts()), record,
            legacy(counts(550, 330, 55), counts(50, 30, 5), second=3), finish()]
        result = self.run_metrics(rows)
        self.assertTrue(result["complete"])
        self.assertEqual(result["tokens"]["input_tokens"], 50)

    def test_proven_initial_baseline_does_not_hide_missing_final_completion(self):
        record = completion("r1", counts(), counts(500, 300, 50))
        record["payload"]["turn_token_usage"] = counts()
        rows = start() + [record, legacy(counts(500, 300, 50), counts()),
            legacy(counts(550, 330, 55), counts(50, 30, 5), second=2), finish()]
        result = self.run_metrics(rows)
        self.assertFalse(result["complete"])
        self.assertIsNone(result["tokens"]["input_tokens"])
        self.assertIn("final_snapshot_usage_gap", result["tasks"][0]["warnings"])

    def test_overlapping_older_file_cannot_replace_newer_usage_checkpoint(self):
        record = completion("r1", counts(), counts(500, 300, 50))
        record["payload"]["turn_token_usage"] = counts()
        old = start() + [record, legacy(counts(500, 300, 50), counts(), second=2), finish()]
        new = start() + [record, legacy(counts(500, 300, 50), counts(), second=2),
                        legacy(counts(550, 330, 55), counts(50, 30, 5), second=3), finish()]
        for first, second in [(new, old), (old, new)]:
            with self.subTest(order=first is new):
                result = self.run_metrics(first, extra=[second])
                self.assertFalse(result["complete"])
                self.assertIsNone(result["tokens"]["input_tokens"])
                self.assertIn("final_snapshot_usage_gap", result["tasks"][0]["warnings"])

    def test_conflicting_simultaneous_counter_snapshots_remain_unknown(self):
        result = self.run_metrics(start() + [completion(), legacy(counts()),
            legacy(counts(150, 80, 15), counts(50, 20, 5)), finish()])
        self.assertIn("ambiguous_counter_snapshots", result["tasks"][0]["warnings"])
        self.assertIsNone(result["tokens"]["input_tokens"])

    def test_two_tasks_reused_child_and_nested_child_attributed_once(self):
        parents = start() + [completion(), finish()]
        parents += [event("event_msg", {"type": "task_started", "turn_id": "t2"}, 10),
                    completion("r2", counts(50, 0, 5), counts(150, 60, 15), turn="t2", second=11),
                    finish("t2", second=19)]
        children = start("c", "c1", "p") + [completion(thread="c", turn="c1"), finish("c1")]
        children += [event("event_msg", {"type": "task_started", "turn_id": "c2"}, 10),
                     completion("r2", counts(30, 0, 3), counts(130, 60, 13), "c", "c2", 11), finish("c2", 19)]
        nested = start("n", "n1", "c") + [completion(thread="n", turn="n1"), finish("n1")]
        specs = [task(), task("next", turn="t2"), task("child", "c", "c1", "main"),
                 task("followup", "c", "c2", "next"), task("nested", "n", "n1", "child")]
        result = self.run_metrics(parents, specs, [children, nested])
        self.assertTrue(result["complete"])
        self.assertEqual(result["tokens"]["input_tokens"], 380)
        self.assertEqual(result["agent_task_count"], 3)
        self.assertEqual(result["agent_thread_count"], 2)
        self.assertEqual(result["reused_child_task_count"], 1)
        self.assertAlmostEqual(result["agent_input_share"], 230 / 380)
        # Selecting only the first review excludes the reused child's followup.
        first = self.run_metrics(parents, [specs[0], specs[2], specs[4]], [children, nested])
        self.assertEqual(first["tokens"]["input_tokens"], 300)

    def test_missing_and_interrupted_children_are_incomplete(self):
        specs = [task(), task("child", "c", "c1", "main")]
        result = self.run_metrics(start() + [completion(), finish()], specs)
        self.assertFalse(result["complete"])
        self.assertIsNone(result["tokens"]["input_tokens"])
        self.assertIn("missing_thread", result["tasks"][1]["warnings"])
        child = start("c", "c1", "p") + [completion(thread="c", turn="c1"),
                    event("event_msg", {"type": "turn_aborted", "turn_id": "c1"})]
        result = self.run_metrics(start() + [completion(), finish()], specs, [child])
        self.assertIn("interrupted_task", result["tasks"][1]["warnings"])

    def test_truncation_and_missing_usage_do_not_leak_bodies(self):
        result = self.run_metrics(start() + [finish()], truncated=True)
        self.assertFalse(result["complete"])
        self.assertIsNone(result["tokens"]["input_tokens"])
        self.assertNotIn("secret_body", json.dumps(result))
        self.assertIn("malformed_or_truncated_record", result["tasks"][0]["warnings"])

    def test_tool_output_bytes_and_dedup_do_not_export_bodies(self):
        call = event("response_item", {"type": "custom_tool_call", "call_id": "call1", "input": "secret"})
        output = event("response_item", {"type": "custom_tool_call_output", "call_id": "call1", "output": "é"})
        result = self.run_metrics(start() + [completion(), call, call, output, output, finish()])
        row = result["tasks"][0]
        self.assertEqual(row["tool_calls"], 1)
        self.assertEqual(row["tool_output_bytes"], 2)
        self.assertNotIn("secret", json.dumps(result))
        result = self.run_metrics(start() + [completion(), call, finish()])
        self.assertIsNone(result["tasks"][0]["tool_output_bytes"])

    def test_overlapping_windows_and_cyclic_parents_are_rejected(self):
        with self.assertRaises(ValueError):
            self.run_metrics(start() + [completion()], [task(), task("overlap")])
        with self.assertRaises(ValueError):
            self.run_metrics([], [task(parent="main")])

    def test_unconfirmed_descendant_inventory_and_unknown_model(self):
        spec = task()
        spec.pop("children_complete")
        result = self.run_metrics(start()[:2] + [completion(), finish()], [spec])
        self.assertFalse(result["complete"])
        self.assertIsNone(result["tasks"][0]["models"])
        self.assertIn("descendant_inventory_unconfirmed", result["tasks"][0]["warnings"])


if __name__ == "__main__":
    unittest.main()
