# Fictional trial-evaluation examples

These public artifacts prepare the approved T14–T19 evaluator checks. They use
only fictional IDs and content. They are not private trial receipts, execution
results, or proof that any route passed.

- `reference-traversal.json` exercises a nested
  `entries[].buckets[].page_ids[]` reference and an explicit continuation. Its
  expected set is fixed independently of evaluator output.
- `artifact-provenance.json` shows why a same-name local file without an
  observed task-bound export receipt is limited to the visible response.
- `image-expectation.json` distinguishes a grounded visual expectation from an
  unavailable-pixels limitation. The named hashes are fictional placeholders;
  real values belong only in private evidence.
- `TRIAL-REPORT-TEMPLATE.md` is the privacy-safe report structure for each
  route and the final cross-route comparison.

The prepared developer checks in
[`helpers/prepared_checks/check_trial_evaluation.py`](../../helpers/prepared_checks/check_trial_evaluation.py)
use synthetic in-memory receipts and records. They passed locally on 2026-09-17
under the separately authorized implementation/testing phase. They make no live
connector or provider claim.
