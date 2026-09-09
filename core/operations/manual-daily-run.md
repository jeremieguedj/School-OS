# Manual daily-brief request

## Goal

Let an authenticated owner run the same complete `daily-run` operation directly
on a qualified manual surface. This is not a second recipe or a scheduler
dispatch. It uses the shared sequential runner and the same durable operation,
catalog, task, rendering, delivery-key, checkpoint, and recovery rules as a
scheduled invocation.

## Admission

1. Resolve the stable bootstrap, instance manifest, private daily values,
   operation state, profile-selection object and exact manual profile, delivery ledger, and this installed
   recipe. The logical file map is for recovery/maintenance; do not sweep it.
2. Require an explicit owner request, `attended_single_writer` serialization
   evidence, and a qualified **manual** profile for storage, mail, and selected
   task capabilities. A scheduler is not required or read for this entrypoint.
3. Admit an active operation only through its checkpoint recovery path. Do not
   start a competing operation or treat `idle` alone as serialization evidence.
4. Invoke `school_os.daily.run_daily(entrypoint="manual")`; every required
   phase must consume verified predecessor output and the operation may report
   only `COMPLETE`, `NEEDS_CONTINUATION`, `BLOCKED`, or `CANCELLED`.

## Delivery

The ordinary manual run uses the common delivery key, intended content hash, and durable
ledger. It verifies delivery through the selected adapter before confirmation;
an unknown outcome is reconciled or blocked, never blindly resent. An explicit
authorized correction has a distinct policy-controlled variant. A manual TEST
run may select only the one finite manual TEST variant in private delivery
configuration; its replay is suppressed under that same key.
