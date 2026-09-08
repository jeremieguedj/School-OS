# Private-instance templates

These files are starting points for an installed Drive instance. They are intentionally synthetic and contain no working IDs, recipients, provider containers, domains, or credentials.

During onboarding, the agent creates private copies, replaces placeholders only with observed values or direct user-provided configuration, validates them, and records the resulting file references in the private instance manifest. `config/daily-run-personal-values.md` is the private companion to the generic daily operation; adapter selection and provider state remain in their separate integration/adapter records.

For alpha.13, `scripts/scaffold_instance.py` first writes a local candidate from
confirmed answers, a verified package/archive pair, and observed object-reference
evidence. It contains no secret values. A storage-capable installer must create
the listed files, read each exact object and byte sequence back, and only then
accept the installation manifest as `verified`. A supplied reference alone is
never proof that a provider object exists.
