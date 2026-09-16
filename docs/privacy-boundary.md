# Privacy boundary

This repository is reusable source code and documentation. It must contain only synthetic examples.

Never commit:

- names, contact information, schools, domains, recipients, account identifiers, or Drive/provider IDs;
- email bodies, attachments, screenshots, source snippets, or task comments from a real household;
- API keys, OAuth tokens, cookies, credentials, or connector exports;
- private configuration, state files, task bindings, delivery logs, or generated briefs;
- logs or test artifacts derived from a private instance.

Private information belongs only in the user's installed Drive instance and connected services. Synthetic fixtures must be invented independently, not redacted copies of real communications.

Before publication, follow the repository continuity in `START-HERE.md` and run the independent `scripts/privacy_scan.py` on all accepted tracked and new files. Keep raw development receipts in an admitted gitignored private directory with restrictive permissions; publish only synthetic examples and privacy-safe findings.
