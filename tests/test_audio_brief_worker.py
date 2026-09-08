"""Focused, dependency-free checks for the local ElevenLabs worker."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest


WORKER = Path(__file__).parents[1] / "automation" / "audio-brief" / "elevenlabs_audio_brief.py"
SPEC = spec_from_file_location("audio_brief_worker", WORKER)
assert SPEC and SPEC.loader
worker = module_from_spec(SPEC)
SPEC.loader.exec_module(worker)


def record(**overrides):
    value = {
        "section": "news",
        "delta_kind": "new",
        "voice_role": "voice_b",
        "subject_label": "Student A",
        "spoken_text": "A source-linked update.",
        "source_tid": "thread-1",
        "fact_or_row_id": "fact-1",
    }
    value.update(overrides)
    return value


class AudioBriefWorkerTests(unittest.TestCase):
    def test_dialogue_uses_recipe_voice_and_tag_mapping(self):
        inputs, omitted = worker.build_inputs({"run_date": "2026-09-02", "records": [record()]})

        self.assertEqual(omitted, 0)
        self.assertEqual(inputs[0]["voice_id"], worker.VOICES["narrator"])
        self.assertEqual(inputs[1], {
            "voice_id": worker.VOICES["voice_b"],
            "text": "[warmly] News: A source-linked update.",
        })
        self.assertEqual(inputs[-1]["voice_id"], worker.VOICES["narrator"])

    def test_opening_spells_sha_and_summarizes_subjects_by_section(self):
        manifest = {
            "run_date": "2026-09-02",
            "records": [
                record(section="guideline", subject_label="Student B"),
                record(section="action", subject_label="Student C", fact_or_row_id="fact-2"),
            ],
        }
        inputs, _ = worker.build_inputs(manifest)

        self.assertEqual(
            inputs[0]["text"],
            "[warmly] S-H-A Daily Brief for Wednesday September 2nd. Today we're going to cover action items for Student C and guidelines for Student B.",
        )

    def test_output_filename_is_human_readable_without_commas(self):
        self.assertEqual(worker.display_date(worker.dt.date(2026, 9, 2)), "Wednesday September 2nd")

    def test_writer_uses_the_human_readable_filename(self):
        with self.subTest("does not need a network request"):
            import tempfile

            with tempfile.TemporaryDirectory() as directory:
                output, _ = worker.write_fresh_mp3(Path(directory), "2026-09-02", b"ID3test")
                self.assertEqual(output.name, "SHA Daily Brief Wednesday September 2nd.mp3")

    def test_whatsapp_compatibility_mode_is_explicit(self):
        import sys
        from unittest.mock import patch

        with patch.object(sys, "argv", ["worker", "--manifest", "m.json", "--output-dir", "out", "--whatsapp-compatible"]):
            self.assertTrue(worker.parse_args().whatsapp_compatible)

    def test_verified_fallback_voice_pair_is_the_default_recipe(self):
        self.assertEqual(worker.VOICES["voice_a"], "CwhRBWXzGAHq8TQ4Fs17")
        self.assertEqual(worker.VOICES["voice_b"], "EXAVITQu4vr4xnSDxMaL")

    def test_first_record_over_character_cap_fails_closed(self):
        manifest = {"run_date": "2026-09-02", "records": [record(spoken_text="x" * 3000)]}

        with self.assertRaisesRegex(worker.BriefError, "first complete record exceeds the 2,000-character limit"):
            worker.build_inputs(manifest)

    def test_action_due_status_must_be_recipe_defined(self):
        manifest = {
            "run_date": "2026-09-02",
            "records": [record(section="action", due_status="someday")],
        }

        with self.assertRaisesRegex(worker.BriefError, "unsupported action due_status"):
            worker.build_inputs(manifest)

    def test_current_run_new_and_changed_news_guidelines_and_actions_feed_audio(self):
        manifest = {
            "run_date": "2026-09-02",
            "records": [
                record(section="news", delta_kind="new", spoken_text="New school update."),
                record(section="guideline", delta_kind="changed", fact_or_row_id="fact-2", spoken_text="Updated guideline."),
                record(section="action", delta_kind="changed", fact_or_row_id="fact-3", spoken_text="Action status changed."),
            ],
        }

        inputs, omitted = worker.build_inputs(manifest)

        self.assertEqual(omitted, 0)
        self.assertEqual(
            [turn["text"] for turn in inputs[1:-1]],
            [
                "[warmly] News: New school update.",
                "[clear, calm] School guideline: Updated guideline.",
                "[clear, matter-of-fact] Action update: Action status changed.",
            ],
        )

    def test_regenerated_rolling_window_and_unchanged_open_actions_are_not_audio_delta(self):
        for delta_kind in ("rolling_window", "unchanged"):
            with self.subTest(delta_kind=delta_kind):
                with self.assertRaisesRegex(worker.BriefError, "current-run new or changed delta"):
                    worker.build_inputs({"run_date": "2026-09-02", "records": [record(delta_kind=delta_kind)]})


if __name__ == "__main__":
    unittest.main()
