from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.references import (  # noqa: E402
    ObjectReference,
    ReferenceError,
    StoredObject,
    discover_unique,
    load_operation_registry,
    resolve_reference,
)


class FakeStorage:
    def __init__(self, objects: list[StoredObject]) -> None:
        self.objects = objects

    def read(self, object_id: str) -> StoredObject | None:
        return next((object_ for object_ in self.objects if object_.object_id == object_id), None)

    def list_scoped(self, parent_id: str) -> list[StoredObject]:
        return [object_ for object_ in self.objects if object_.parent_id == parent_id]


def object_(object_id: str, *, kind: str = "file", parent: str = "instance-root", mime: str = "text/markdown") -> StoredObject:
    return StoredObject(
        object_id=object_id,
        kind=kind,
        parent_id=parent,
        ancestor_ids=(parent, "instance-root"),
        mime_type=mime,
        version="v1",
        name="daily-run.md",
        data=b"fixture",
    )


class ReferenceResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = ObjectReference(
            object_id="recipe-expected",
            kind="file",
            permitted_ancestor_id="instance-root",
            mime_type="text/markdown",
            version="v1",
        )

    def test_exact_identity_beats_same_named_lookalikes(self) -> None:
        expected = object_("recipe-expected")
        lookalike = object_("recipe-lookalike")
        storage = FakeStorage([lookalike, expected])
        self.assertEqual(expected, resolve_reference(storage, self.reference, expected_kind="file"))

    def test_kind_parent_mime_and_version_mismatches_block(self) -> None:
        cases = [
            object_("recipe-expected", kind="folder"),
            StoredObject(
                **{
                    **object_("recipe-expected", parent="another-instance").__dict__,
                    "ancestor_ids": ("another-instance",),
                }
            ),
            object_("recipe-expected", mime="application/json"),
            StoredObject(**{**object_("recipe-expected").__dict__, "version": "v2"}),
        ]
        for candidate in cases:
            with self.subTest(candidate=candidate):
                with self.assertRaises(ReferenceError):
                    resolve_reference(FakeStorage([candidate]), self.reference)

    def test_missing_or_ambiguous_scoped_discovery_blocks(self) -> None:
        with self.assertRaisesRegex(ReferenceError, "no matching"):
            discover_unique(FakeStorage([]), parent_id="instance-root", name="daily-run.md", kind="file")
        with self.assertRaisesRegex(ReferenceError, "ambiguous"):
            discover_unique(
                FakeStorage([object_("one"), object_("two")]),
                parent_id="instance-root",
                name="daily-run.md",
                kind="file",
            )

    def test_registry_is_schema_valid_and_every_recipe_is_installed(self) -> None:
        self.assertEqual(
            {"daily-run": "core/operations/daily-run.md"},
            load_operation_registry(
                ROOT / "core" / "operations" / "registry.json",
                ROOT / "schemas" / "operation-registry.schema.json",
                ROOT,
            ),
        )

    def test_registry_rejects_a_missing_or_unsafe_recipe(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name) / "School-OS-0.1.0-alpha.13"
        (root / "core" / "operations").mkdir(parents=True)
        shutil.copy(ROOT / "schemas" / "operation-registry.schema.json", root / "operation-registry.schema.json")
        registry = json.loads((ROOT / "core" / "operations" / "registry.json").read_text(encoding="utf-8"))
        (root / "registry.json").write_text(json.dumps(registry), encoding="utf-8")
        with self.assertRaisesRegex(ReferenceError, "not an installed regular file"):
            load_operation_registry(root / "registry.json", root / "operation-registry.schema.json", root)
        registry["operations"]["daily-run"] = "../outside.md"
        (root / "registry.json").write_text(json.dumps(registry), encoding="utf-8")
        with self.assertRaisesRegex(ReferenceError, "invalid operation registry"):
            load_operation_registry(root / "registry.json", root / "operation-registry.schema.json", root)


if __name__ == "__main__":
    unittest.main()
