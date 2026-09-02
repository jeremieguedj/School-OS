# Scheduler adapters

A scheduler adapter must define:

- stable schedule identity;
- configured local timezone and daylight-saving behavior;
- schedule creation/update/inspection/disable verification;
- whether background runs retain required connector authorization;
- invocation input and Drive bootstrap access;
- timeout, retry, missed-run, and overlap behavior; and
- how to prove that a prior schedule is disabled before cutover.

A runtime without a certified scheduler adapter may support manual runs only.
