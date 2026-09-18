"""Prepared fictional bootstrap checks; NOT RUN.

Execution/import belongs to the user's later testing phase.  The fixture uses
only invented School-OS IDs and performs no provider or filesystem operation.
"""

import copy
import json
import unittest

from helpers.bootstrap_contract import check_bootstrap


INSTANCE_ID = "inst_11111111-1111-4111-8111-111111111111"
SOURCE_ACCOUNT_ID = "source_account_30000000-0000-4000-8000-000000000001"


def _encoded(page):
    return json.dumps(page, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _envelope(family, page_id, **values):
    return {
        "instance_id": INSTANCE_ID,
        "family": family,
        "page_id": page_id,
        "schema_version": "1",
        "content_revision": 1,
        **values,
    }


def _empty_locator(number, canonical_family):
    return _envelope(
        "record_locator",
        f"page_a0000000-0000-4000-8000-{number:012d}",
        locator_key={"canonical_family": canonical_family},
        entries=[],
        continuation={"state": "exhausted"},
    )


def _valid_fixture():
    entity_page_id = "page_90000000-0000-4000-8000-000000000001"
    source_page_id = "page_90000000-0000-4000-8000-000000000002"
    locator_families = [
        "source_account",
        "entity",
        "topic",
        "membership",
        "email",
        "attachment_group",
        "ingestion_coverage",
        "discovery_window",
        "knowledge",
    ]
    locators = {
        family: _empty_locator(number, family)
        for number, family in enumerate(locator_families, start=1)
    }
    locators["entity"]["entries"] = [
        {
            "record_id": "entity_10000000-0000-4000-8000-000000000001",
            "page_id": entity_page_id,
        }
    ]
    locators["source_account"]["entries"] = [
        {"record_id": SOURCE_ACCOUNT_ID, "page_id": source_page_id}
    ]
    active_tasks = _empty_locator(20, "task")
    completed_tasks = _empty_locator(21, "task")
    entity_index = _envelope(
        "entity_index",
        "page_a0000000-0000-4000-8000-000000000030",
        directory_key="entity_index_root",
        entries=[],
        continuation={"state": "exhausted"},
    )
    topic_index = _envelope(
        "topic_index",
        "page_a0000000-0000-4000-8000-000000000031",
        directory_key="topic_index_root",
        entries=[],
        continuation={"state": "exhausted"},
    )
    incoming = _envelope(
        "incoming_relationship_index",
        "page_a0000000-0000-4000-8000-000000000032",
        directory_key="incoming_relationship_index_root",
        entries=[],
        continuation={"state": "exhausted"},
    )
    coverage = _envelope(
        "index_coverage",
        "page_a0000000-0000-4000-8000-000000000033",
        entries=[],
        continuation={"state": "exhausted"},
    )
    configuration = _envelope(
        "configuration",
        "page_90000000-0000-4000-8000-000000000003",
        records=[
            {
                "instance_id": INSTANCE_ID,
                "household_entity_ref": {
                    "family": "entity",
                    "id": "entity_10000000-0000-4000-8000-000000000001",
                },
                "household_timezone": "America/Los_Angeles",
                "source_accounts": [
                    {"family": "source_account", "id": SOURCE_ACCOUNT_ID}
                ],
                "entity_topic_roots": {
                    "entity_directory_page_id": locators["entity"]["page_id"],
                    "membership_directory_page_id": locators["membership"]["page_id"],
                    "topic_directory_page_id": locators["topic"]["page_id"],
                    "entity_index_directory_page_id": entity_index["page_id"],
                    "topic_index_directory_page_id": topic_index["page_id"],
                    "incoming_relationship_index_directory_page_id": incoming["page_id"],
                    "index_coverage_directory_page_id": coverage["page_id"],
                },
            }
        ],
    )
    entity = _envelope(
        "entity",
        entity_page_id,
        records=[
            {
                "entity_id": "entity_10000000-0000-4000-8000-000000000001",
                "entity_kind": "household",
                "display_name": "Fictional household",
                "aliases": [],
                "origin": "parent_configuration",
                "recorded_at": "2026-09-17T12:00:00Z",
            }
        ],
    )
    source_account = _envelope(
        "source_account",
        source_page_id,
        records=[
            {
                "source_account_id": SOURCE_ACCOUNT_ID,
                "label": "Fictional school mailbox",
                "logical_mailbox_identity": "Fictional parent-selected mailbox",
                "configured_scope": "Fictional school correspondence",
                "import_boundary": {
                    "state": "known",
                    "value": "2026-08-01",
                    "precision": "day",
                    "meaning": "configured_import_start",
                },
                "adapter_ref": "system/tool-adapters/fictional-mail-tool",
            }
        ],
    )
    catalogues = []
    for number, family in enumerate(
        ("email", "attachment_group", "ingestion_coverage", "knowledge"),
        start=40,
    ):
        catalogues.append(
            _envelope(
                "page_catalogue",
                f"page_a0000000-0000-4000-8000-{number:012d}",
                route={
                    "canonical_family": family,
                    "source_account_id": SOURCE_ACCOUNT_ID,
                    "source_month": "pending",
                },
                entries=[],
                continuation={"state": "exhausted"},
            )
        )

    pages = [
        configuration,
        entity,
        source_account,
        *locators.values(),
        active_tasks,
        completed_tasks,
        entity_index,
        topic_index,
        incoming,
        coverage,
        *catalogues,
    ]
    routes = [
        {
            "role": "instance-configuration",
            "root_page_id": configuration["page_id"],
            "expected": {"family": "configuration"},
        },
        *[
            {
                "role": f"{family}-directory",
                "root_page_id": page["page_id"],
                "expected": {
                    "family": "record_locator",
                    "locator_key": {"canonical_family": family},
                },
            }
            for family, page in locators.items()
        ],
        {
            "role": "active-tasks",
            "root_page_id": active_tasks["page_id"],
            "expected": {
                "family": "record_locator",
                "locator_key": {"canonical_family": "task"},
            },
        },
        {
            "role": "completed-task-history",
            "root_page_id": completed_tasks["page_id"],
            "expected": {
                "family": "record_locator",
                "locator_key": {"canonical_family": "task"},
            },
        },
        {
            "role": "entity-index-root",
            "root_page_id": entity_index["page_id"],
            "expected": {"family": "entity_index", "directory_key": "entity_index_root"},
        },
        {
            "role": "topic-index-root",
            "root_page_id": topic_index["page_id"],
            "expected": {"family": "topic_index", "directory_key": "topic_index_root"},
        },
        {
            "role": "incoming-relationship-root",
            "root_page_id": incoming["page_id"],
            "expected": {
                "family": "incoming_relationship_index",
                "directory_key": "incoming_relationship_index_root",
            },
        },
        {
            "role": "index-coverage-root",
            "root_page_id": coverage["page_id"],
            "expected": {"family": "index_coverage"},
        },
        *[
            {
                "role": f"pending-{page['route']['canonical_family']}",
                "root_page_id": page["page_id"],
                "expected": {"family": "page_catalogue", "route": page["route"]},
            }
            for page in catalogues
        ],
    ]
    return {"routes": routes}, pages


class BootstrapContractChecks(unittest.TestCase):
    def _check(self, manifest, pages):
        return check_bootstrap("1", INSTANCE_ID, manifest, [_encoded(page) for page in pages])

    def test_valid_fictional_empty_instance(self):
        manifest, pages = _valid_fixture()
        self.assertEqual(self._check(manifest, pages), {"status": "valid", "diagnostics": []})

    def test_generic_catalogue_family_is_invalid(self):
        manifest, pages = _valid_fixture()
        catalogue = next(page for page in pages if page["family"] == "page_catalogue")
        catalogue["route"]["canonical_family"] = "catalogue_root"
        self.assertEqual(self._check(manifest, pages)["status"], "invalid")

    def test_missing_saved_root_is_insufficient_evidence(self):
        manifest, pages = _valid_fixture()
        missing = manifest["routes"][-1]["root_page_id"]
        pages = [page for page in pages if page["page_id"] != missing]
        self.assertEqual(self._check(manifest, pages)["status"], "insufficient_evidence")

    def test_continuation_cycle_is_invalid(self):
        manifest, pages = _valid_fixture()
        locator = next(page for page in pages if page.get("locator_key") == {"canonical_family": "topic"})
        locator["continuation"] = {"state": "continues", "next_page_id": locator["page_id"]}
        self.assertEqual(self._check(manifest, pages)["status"], "invalid")

    def test_wrong_referenced_family_or_route_is_invalid(self):
        manifest, pages = _valid_fixture()
        configuration = next(page for page in pages if page["family"] == "configuration")
        topic_locator = next(page for page in pages if page.get("locator_key") == {"canonical_family": "topic"})
        configuration["records"][0]["entity_topic_roots"]["entity_directory_page_id"] = topic_locator["page_id"]
        self.assertEqual(self._check(manifest, pages)["status"], "invalid")

    def test_missing_or_non_string_configuration_root_is_invalid(self):
        for replacement in (None, 7):
            with self.subTest(replacement=replacement):
                manifest, pages = _valid_fixture()
                configuration = next(
                    page for page in pages if page["family"] == "configuration"
                )
                roots = configuration["records"][0]["entity_topic_roots"]
                if replacement is None:
                    roots.pop("topic_directory_page_id")
                else:
                    roots["topic_directory_page_id"] = replacement
                self.assertEqual(self._check(manifest, pages)["status"], "invalid")

    def test_non_string_locator_catalogue_and_index_targets_are_invalid(self):
        mutations = (
            lambda pages: next(
                page
                for page in pages
                if page.get("locator_key") == {"canonical_family": "entity"}
            )["entries"][0].update(page_id=7),
            lambda pages: next(
                page for page in pages if page["family"] == "page_catalogue"
            )["entries"].append(
                {
                    "canonical_page_id": 7,
                    "canonical_family": "email",
                    "content_revision": 1,
                    "drive_access_aid": "fictional-drive-aid",
                }
            ),
            lambda pages: next(
                page
                for page in pages
                if page.get("directory_key") == "entity_index_root"
            )["entries"].append(
                {
                    "lookup_id": "entity_10000000-0000-4000-8000-000000000001",
                    "buckets": [{"time_bucket": "2026-09", "page_ids": [7]}],
                }
            ),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                manifest, pages = _valid_fixture()
                mutate(pages)
                self.assertEqual(self._check(manifest, pages)["status"], "invalid")

    def test_discovery_window_continuation_target_is_followed(self):
        manifest, pages = _valid_fixture()
        discovery_locator = next(
            page
            for page in pages
            if page.get("locator_key") == {"canonical_family": "discovery_window"}
        )
        email_locator = next(
            page
            for page in pages
            if page.get("locator_key") == {"canonical_family": "email"}
        )
        discovery_page = _envelope(
            "discovery_window",
            "page_90000000-0000-4000-8000-000000000090",
            records=[
                {
                    "window_id": "window_51000000-0000-4000-8000-000000000001",
                    "observed_email_refs": {
                        "source_index_page_ids": [email_locator["page_id"]],
                        "continuation": {
                            "state": "continues",
                            "next_page_id": "page_a0000000-0000-4000-8000-000000000099",
                        },
                    },
                }
            ],
        )
        discovery_locator["entries"].append(
            {
                "record_id": discovery_page["records"][0]["window_id"],
                "page_id": discovery_page["page_id"],
            }
        )
        pages.append(discovery_page)
        result = self._check(manifest, pages)
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertIn(
            "missing_referenced_readback",
            {item["code"] for item in result["diagnostics"]},
        )

    def test_discovery_window_continuation_requires_a_string_page_id(self):
        manifest, pages = _valid_fixture()
        discovery_locator = next(
            page
            for page in pages
            if page.get("locator_key") == {"canonical_family": "discovery_window"}
        )
        discovery_page = _envelope(
            "discovery_window",
            "page_90000000-0000-4000-8000-000000000091",
            records=[
                {
                    "window_id": "window_51000000-0000-4000-8000-000000000002",
                    "observed_email_refs": {
                        "source_index_page_ids": [],
                        "continuation": {"state": "continues", "next_page_id": 7},
                    },
                }
            ],
        )
        discovery_locator["entries"].append(
            {
                "record_id": discovery_page["records"][0]["window_id"],
                "page_id": discovery_page["page_id"],
            }
        )
        pages.append(discovery_page)
        self.assertEqual(self._check(manifest, pages)["status"], "invalid")

    def test_oversized_page_is_invalid(self):
        manifest, pages = _valid_fixture()
        encoded = [_encoded(page) for page in pages]
        encoded[0] += b" " * 65_536
        self.assertEqual(check_bootstrap("1", INSTANCE_ID, manifest, encoded)["status"], "invalid")

    def test_entry_bound_is_invalid(self):
        manifest, pages = _valid_fixture()
        coverage = next(page for page in pages if page["family"] == "index_coverage")
        coverage["entries"] = [
            {
                "canonical_page_id": pages[1]["page_id"],
                "canonical_family": "entity",
                "content_revision": 1,
                "covered_indexes": [],
            }
            for _ in range(101)
        ]
        self.assertEqual(self._check(manifest, pages)["status"], "invalid")

    def test_conflicting_duplicate_page_id_is_invalid(self):
        manifest, pages = _valid_fixture()
        duplicate = copy.deepcopy(pages[0])
        duplicate["content_revision"] = 2
        self.assertEqual(self._check(manifest, [*pages, duplicate])["status"], "invalid")
