# Separate interpretation review

A fresh Codex agent read the source fixture without reading the semantic
expectation file, state model or result files. Its full output is preserved in
[`independent-interpretation.json`](independent-interpretation.json), bound to
the byte hash of the input file and its ordered message/part content hashes.
The state model's fixture hash uses canonical JSON serialization; these two
hashes intentionally use different representations of the same input.

This is an independent interpretation exercise with limited blinding. The input
fixture also contains identity probes and some semantic hints. Withholding the
expectation file does not make this an uncontaminated or statistically valid
benchmark. No performance percentage is claimed. The reader assumed every text
surrogate was readable, including the unavailable timetable; that assumption
must never bypass the state model's actual-read requirement.

The reader produced 41 fine-grained source-local facts, six source-local action
mentions representing four distinct requests, and two corrections. Those counts
are not directly comparable to 21 consolidated model facts. The primary agent
reviewed the interpretation against the fictional source and expected records:

| Sources | Review outcome |
|---|---|
| 001 | Dismissal gate/time and late-collection condition preserved; equivalent HTML/plain alternatives recognized; no invented dated task. |
| 002 | Yes **or no** response remains mandatory; February trip date is separate from January response deadline. |
| 003 + 013 | Inline school answer replaces January 23 with January 24, preserves the time and optional/no-response conditions; quoted questions add no task. |
| 004 + 012 | The fee's conditional request persists with corrected January 20 deadline. It does not change the separate response deadline. |
| 005 + 014 | One term consent task; explicit parent completion survives the reminder. The reminder means act now if still outstanding, without replacing the original January 12 due date. |
| 006 | Boots request belongs to the meaningful image, not its body pointer or decorative logo. This tests the supplied text's meaning, not vision. |
| 007 | Both handbook rules recognized. The separate interpretation exposed missing term-wide applicability and page references in the initial expected catalog. Those were added before the final state-model run. |
| 008 | Library opening is preserved without inventing an action. |
| 009 + 011 | Same-name attachments supply different meanings; repeated menu content preserves both source occurrences. Lunch-line guidance remains standing knowledge. |
| 010 | Timetable content is combined with the body's starting week. Availability is assumed here; the state model separately withholds these facts before a successful read. |
| 015 | The second mailbox's assembly stays distinct despite a repeated provider message ID; no response task invented. |

The expected catalog was improved in two places: body-plus-handbook provenance,
term-wide qualifications and page positions for the standing rules; and explicit
immediate-reminder wording alongside the unchanged original deadline. The
independent output was not rewritten to match those changes.

This exposes a requirement beyond stable source IDs: processing must preserve
qualifications supplied by surrounding text and connect claims supported by
multiple parts. A passing state machine with an incomplete expectation fixture
does not establish losslessness. The exercise offers narrow positive evidence
for one agent's comprehension of these short examples; realistic emails,
forwarding/MIME parsing, attachments and target-app execution still need tests.
