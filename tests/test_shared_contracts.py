from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from school_os.contracts import canonical_json_bytes, dump_mapping_yaml, load_mapping_yaml, sha256_bytes, validate  # noqa: E402


class SharedContractTests(unittest.TestCase):
    def test_owned_yaml_round_trips_empty_collections_without_type_change(self) -> None:
        value = {
            "empty_list": [], "empty_mapping": {},
            "nested": [{"children": [], "metadata": {}}],
        }
        encoded = dump_mapping_yaml(value)
        self.assertEqual(value, load_mapping_yaml(encoded.decode("utf-8")))

    def test_canonical_json_is_stable_utf8_with_trailing_newline(self) -> None:
        value = {"z": "café", "a": [2, 1]}
        encoded = canonical_json_bytes(value)
        self.assertEqual(b'{"a":[2,1],"z":"caf\xc3\xa9"}\n', encoded)
        self.assertEqual("3ed4b0ad210e98c8eb62f2df42f735d24e01454c3cf6acb4a0ddc8d54ab0b0d5", sha256_bytes(encoded))

    def test_shared_yaml_loader_and_schema_validator_match_instance_contract(self) -> None:
        schema = json.loads((ROOT / "schemas" / "release.schema.json").read_text(encoding="utf-8"))
        manifest = load_mapping_yaml((ROOT / "release.yaml").read_text(encoding="utf-8"))
        self.assertEqual([], validate(manifest, schema))
