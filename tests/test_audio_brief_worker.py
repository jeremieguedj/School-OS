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


if __name__ == "__main__":
    unittest.main()
