# Restart publication and retired CI

The former `workflows/validate.yml` built and tested the retired runtime. It was
explicitly retired with that runtime on `codex/restart-implementation`; it is
preserved in the `orgos-restart-documentation` tag. This is not a bypass of a
current restart check. No replacement functional CI is claimed.

Before publishing, perform diff/privacy/document-link/Git hygiene and inspect any
new hooks/workflows. Functional execution starts only after the agreed restart
implementation publication under the specific authorization in the active plan.
Do not dispatch the legacy main-branch workflow to validate the restart.
