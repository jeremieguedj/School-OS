"""Prepared unittest cases using fictional source metadata.

Last run locally on 2026-09-18 as part of the 73-test prepared-check suite.
These checks make no provider or production qualification claim.
"""

import unittest

from helpers.source_metadata import (
    normalize_address_parts,
    normalize_subject,
    utf8_size,
)


class SourceMetadataChecks(unittest.TestCase):
    def test_literal_subject_preserves_interior_spacing_case_and_prefix(self):
        self.assertEqual(
            normalize_subject(" \tRe: Cedar  update\r\n\troom 2 \t", representation="raw_header"),
            "Re: Cedar  update\troom 2",
        )

    def test_encoded_words_and_literal_spacing_have_different_rules(self):
        self.assertEqual(
            normalize_subject("Re:  =?utf-8?Q?Caf=C3=A9?=  room", representation="raw_header"),
            "Re:  Café  room",
        )
        self.assertEqual(
            normalize_subject("=?utf-8?Q?Cedar_?=\r\n \t=?us-ascii?B?dXBkYXRl?=", representation="raw_header"),
            "Cedar update",
        )

    def test_strict_charset_decoding(self):
        self.assertEqual(normalize_subject("=?iso-8859-1?Q?Caf=E9?=", representation="raw_header"), "Café")
        self.assertEqual(normalize_subject("=?windows-1252?Q?Fee_=80?=", representation="raw_header"), "Fee €")
        for value in (
            "=?utf-8?Q?=FF?=",
            "=?unknown-charset?Q?Cedar?=",
            "=?utf-8?B?%%%?=",
            "=?utf-8?Q?bad=GG?=",
            "=?utf-8?Q?unfinished",
            "word=?utf-8?Q?Cedar?=",
            "=?utf-8?Q?Cedar?=tail",
            "=?utf-8?Q?" + "a" * 64 + "?=",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_subject(value, representation="raw_header")

    def test_subject_controls_do_not_become_fold_or_replacement(self):
        for value in ("Cedar\n update", "Cedar\r\nupdate", "Cedar\x00",
                      "=?utf-8?Q?Cedar=0Aupdate?=", "\ud800"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_subject(value, representation="raw_header")

    def test_missing_subject_is_not_empty_observed_subject(self):
        self.assertEqual(normalize_subject(" \t", representation="raw_header"), "")
        with self.assertRaises(TypeError):
            normalize_subject(None, representation="raw_header")

    def test_raw_and_decoded_counterparts_do_not_double_decode(self):
        raw = "=?utf-8?Q?=3D=3Futf-8=3FQ=3FCedar=5Fupdate=3F=3D?="
        decoded = "=?utf-8?Q?Cedar_update?="
        self.assertEqual(normalize_subject(raw, representation="raw_header"), decoded)
        self.assertEqual(normalize_subject(decoded, representation="decoded"), decoded)
        self.assertEqual(
            normalize_subject(" \tRe:  " + decoded + " \t", representation="decoded"),
            "Re:  " + decoded,
        )
        with self.assertRaises(ValueError):
            normalize_subject("Cedar\r\n update", representation="decoded")

    def test_subject_representation_is_required_and_never_guessed(self):
        with self.assertRaises(TypeError):
            normalize_subject("Cedar update")
        for representation in ("", "unknown", "RAW_HEADER"):
            with self.subTest(representation=representation), self.assertRaises(ValueError):
                normalize_subject("Cedar update", representation=representation)
        with self.assertRaises(TypeError):
            normalize_subject("Cedar update", representation=None)

    def test_extracted_address_preserves_local_spelling_and_plus_tag(self):
        self.assertEqual(
            normalize_address_parts(" \tCedar.Teacher+Trips ", " EXAMPLE.ORG\t"),
            ("Cedar.Teacher+Trips", "example.org"),
        )
        self.assertNotEqual(
            normalize_address_parts("Cedar.Teacher+Trips", "example.org"),
            normalize_address_parts("cedar.teacher+Trips", "example.org"),
        )

    def test_unextracted_or_unsupported_address_parts_are_not_guessed(self):
        for local, domain in (
            ("Ms Brook <teacher>", "example.org"),
            ("teacher@example.org", "example.org"),
            ('"teacher name"', "example.org"),
            ("teacher..name", "example.org"),
            ("teacher", "example..org"),
            ("teacher", "-example.org"),
            ("teacher", "[127.0.0.1]"),
            ("teacher", "éxample.org"),
            ("teacher\n", "example.org"),
            ("", "example.org"),
        ):
            with self.subTest(local=local, domain=domain), self.assertRaises(ValueError):
                normalize_address_parts(local, domain)
        with self.assertRaises(TypeError):
            normalize_address_parts(None, "example.org")

    def test_utf8_size_counts_supplied_text_without_normalization(self):
        self.assertEqual(utf8_size(""), 0)
        self.assertEqual(utf8_size("é🙂"), 6)
        self.assertEqual(utf8_size("e\u0301"), 3)
        self.assertEqual(utf8_size(" A\r\n"), 4)
        with self.assertRaises(ValueError):
            utf8_size("\ud800")
        with self.assertRaises(TypeError):
            utf8_size(b"already bytes")
