from __future__ import annotations

import unittest

from school_os.audio import AudioManifestError, build_audio_manifest, merge_parent_task_delta


class AudioManifestTests(unittest.TestCase):
    def config(self):
        return {
            "voices": {"narrator": "n", "voice_a": "a"},
            "opening_tag": "[open]", "closing_tag": "[close]",
            "groups": {"child-a": {
                "subject_label": "Student A", "voice_role": "voice_a",
                "dialogue_tags": {"news": "[news]", "guideline": "[guide]", "action": "[action]"},
            }},
        }

    def facts(self):
        return [{
            "fact_id": "fact-1", "record_id": "record-1", "entity_scope": "child-a",
            "text": "Exact canonical fact.",
            "flags": {"is_update": True, "is_durable": False, "is_guideline": False, "is_action": False},
        }]

    def tasks(self):
        return {"schema_version": 1, "tasks": [{
            "task_id": "task-1", "entity_scope": "child-a", "action": "Exact action.",
            "source_facts": ["fact-1"],
        }]}

    def test_builds_only_explicit_current_delta_with_exact_canonical_wording(self):
        manifest = build_audio_manifest(
            run_date="2026-09-10", window={"start": "s", "end": "e"},
            delta={
                "schema_version": 1,
                "facts": [{"fact_id": "fact-1", "delta_kind": "new"}],
                "tasks": [{"task_id": "task-1", "delta_kind": "changed"}],
            },
            facts=self.facts(), canonical_tasks=self.tasks(),
            source_threads={"record-1": "thread-1"}, configuration=self.config(),
        )
        self.assertEqual(["Exact canonical fact.", "Exact action."], [item["spoken_text"] for item in manifest["records"]])
        self.assertEqual(["new", "changed"], [item["delta_kind"] for item in manifest["records"]])
        self.assertEqual("thread-1", manifest["records"][1]["source_tid"])

    def test_unknown_identity_or_group_and_implicit_delta_fail_closed(self):
        call = dict(
            run_date="2026-09-10", window={"start": "s", "end": "e"},
            delta={"schema_version": 1, "facts": [{"fact_id": "missing", "delta_kind": "new"}], "tasks": []},
            facts=self.facts(), canonical_tasks=self.tasks(),
            source_threads={"record-1": "thread-1"}, configuration=self.config(),
        )
        with self.assertRaisesRegex(AudioManifestError, "unknown Fact"):
            build_audio_manifest(**call)
        call["delta"] = {"schema_version": 1, "facts": [], "tasks": []}
        call["configuration"] = {**self.config(), "groups": {}}
        with self.assertRaisesRegex(AudioManifestError, "groups"):
            build_audio_manifest(**call)

    def test_parent_task_delta_accumulates_new_and_changed_but_not_source_projection(self):
        source = {"task_id": "source", "origin": "source", "action": "S"}
        parent = {"task_id": "parent", "origin": "parent", "action": "P"}
        initial = {"schema_version": 1, "tasks": [source]}
        after_add = {"schema_version": 1, "tasks": [source, parent]}
        delta = merge_parent_task_delta(
            {"schema_version": 1, "facts": [], "tasks": []}, initial, after_add,
        )
        self.assertEqual([{"task_id": "parent", "delta_kind": "new"}], delta["tasks"])
        changed = {"schema_version": 1, "tasks": [source, {**parent, "action": "Changed"}]}
        again = merge_parent_task_delta(delta, after_add, changed)
        self.assertEqual([{"task_id": "parent", "delta_kind": "new"}], again["tasks"])


if __name__ == "__main__":
    unittest.main()
