# Gmail — school messages and authorized email delivery

Use this mapping with [ingestion](../operations/ingestion.md),
[source identity](../contracts/identity.md) and
[brief recipes](../operations/brief-recipes.md). The current connector supplies
Gmail access and API/transport details; this document supplies shared meanings.

## Message and metadata meanings

One School-OS email represents an individual logical email, including each
individual reply. A Gmail thread or search summary is not that record. Gmail
message/thread handles locate current objects but do not decide School-OS
identity. A changed handle does not prove a different logical email.

Obtain the logical mailbox, original subject, sender, each message's original
Date, role-preserving To/Cc and comparable original attachment-name inventory.
Retain originals alongside normalized values. Automatic association requires the
approved known-timezone, second-or-finer original Date and other recipe conditions.
A display timestamp, snippet or thread date cannot substitute. Use richer
individual-message metadata if needed; inadequate evidence remains unresolved.

Gmail's internal timestamp usually reflects acceptance for SMTP mail, but imported
mail may use the original Date instead. Preserve its documented meaning separately;
it is not School-OS original-Date identity evidence. Gmail also exposes snippets
and full-message content as different things. A snippet cannot establish a complete
body read. [Message meanings](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages).

## Discovery and continuation

Use the approved configured arrival-time windows through run start, unfinished
windows and known not-ingested backlog. Explain the current route's actual time
meaning and boundary precision before calling its window complete. Gmail's
date-only search boundaries use its documented timezone, and UI/API searches
can differ. The connector must preserve the intended interval rather than
quietly treating a date string as household-local midnight.
[Search semantics](https://developers.google.com/workspace/gmail/api/guides/filtering).

Follow every available continuation, including after a short result. An estimated
result count is not exhaustion evidence or a logical-email count. Gmail's list
response can contain only message/thread handles, requiring individual reads.
[Listing semantics](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list).

Save School-OS discovery-window progress on Drive. A lost token permits replay
of an unfinished window; no permanent Gmail cursor is required. Do not rescan
the whole historical range daily: that fallback was rejected. Disclose the
approved older-delayed-visibility limitation and any actual incomplete route.
Mailbox read/unread flags do not decide ingestion. Do not change labels or read
state merely to create a School-OS cursor. Sent, spam, trash and other scopes
remain exactly as authorized; this mapping grants no broader search permission.

## Read content and attachments

Retrieve bodies and relevant attachment candidates temporarily through the
authorized connector. Original filename plus parent email supplies the approved
attachment context; preserve same-parent same-name candidates and uncertainty.
Never use bodies, MIME structure, embedded images, bytes or hashes for identity
or thread association. Reading their substantive content for extraction is a
separate requirement. HTML text that omits meaningful imagery or an attachment
preview that truncates pages is not full processing.

Follow the binary ingestion and approved reuse rule in the ingestion operation.
An unread required attachment prevents full ingestion. A metadata-associated
email may reuse its prior full result only when the approved rule supports it;
a new reply or newly exposed required material cannot inherit that result.
Missing download/OCR/document-reading capability stays explicit. After verified
canonical persistence, discard accessible temporary raw copies.

## Send and inspect the outcome

Sending is separate from source discovery. Resolve the authorized recipient and
sender account, then apply the chosen brief recipe and any configured audio.
The connector handles formatting and transport. Inspect its actual sent-message
or equivalent authorized evidence: sender, recipients, intended content and
attachment presence where applicable. A saved draft is not a sent message, and
sent evidence is not proof the recipient read it.

When outcome is unknown, use only authorized evidence to distinguish a confirmed
send from an unresolved result before retrying. An empty/lagging sent search does
not prove failure. Do not widen mailbox access or resend blindly. Include the
generating agent and actual sending service/account in the output attribution.
No live connector or sending path is qualified by this mapping.
