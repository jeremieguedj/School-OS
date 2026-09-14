"""Development-only, conservative metadata identity model; not a runtime.

Automatic association requires original subject, sender and an exact zoned
source timestamp in the same account. Optional fields only distinguish when
their scopes are comparable. Content and external identifiers are never read.
The seconds requirement is an explicit test policy, not a universal mail rule.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
from email import policy
from email.header import decode_header, make_header
from email.utils import getaddresses, parsedate_to_datetime
import re


FIELDS = ("account", "account_verified", "subject", "sender", "sent", "received",
          "to", "cc", "filenames", "filename_scope", "filenames_complete")
ORIGINAL_FILENAME_SCOPES = {"original_named_attachments"}


def decode_subject(value):
    if value is None:
        return None
    try:
        return str(make_header(decode_header(re.sub(r"\r?\n[ \t]+", " ", value))))
    except (ValueError, LookupError, UnicodeError):
        return None


def empty_address_value(value):
    """Recognize empty fields/groups without treating malformed text as empty."""
    if not isinstance(value, str):
        return False
    if not value.strip():
        return True
    if ":" not in value or ";" not in value:
        return False
    try:
        header = policy.default.header_factory("To", value)
        return (not header.defects and bool(header.groups) and not header.addresses
                and all(group.display_name is not None and not group.addresses
                        for group in header.groups))
    except (ValueError, TypeError, IndexError):
        return False


def addresses(value):
    """None denotes unknown, [] a known empty role; preserve local-part spelling."""
    if value is None:
        return None
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple)) or any(not isinstance(item, str) for item in value):
        return None
    value = [item for item in value if not empty_address_value(item)]
    result = []
    for _, address in getaddresses(value):
        local, separator, domain = address.rpartition("@")
        if not separator or not local or not domain:
            return None
        if any(c.isspace() for c in local) and not (local.startswith('"') and local.endswith('"')):
            return None
        result.append(local + "@" + domain.lower())
    return sorted(result)


def flattened_sender(value):
    """Observed display-label + final bare address, without interpreting label.

    This is an explicitly observed metadata presentation, not arbitrary RFC
    parsing. Ambiguous/malformed forms remain unknown. A quoted display label
    can itself contain an address; only the final standalone address is read.
    """
    if value is None or not isinstance(value, str) or not value.strip():
        return None
    if "<" in value and ">" in value:
        parsed = addresses(value)
    else:
        candidate = value.rsplit(None, 1)[-1]
        parsed = addresses(candidate)
        if parsed is None or len(parsed) != 1:
            return None
        local, _, domain = candidate.rpartition("@")
        if not local or not domain or any(c in candidate for c in '<>"'):
            return None
        if parsed[0] != local + "@" + domain.lower():
            return None
    return parsed[0] if parsed and len(parsed) == 1 else None


def flattened_recipients(value):
    """Observed search list: each entry is one display label + final address."""
    if value is None:
        return None
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple)):
        return None
    result = []
    for item in value:
        if empty_address_value(item):
            continue
        address = flattened_sender(item)
        if address is None:
            return None
        result.append(address)
    return sorted(result)


def source_date(value, meaning="sent"):
    if value is None:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        precision = "second" if re.search(r"\b\d{1,2}:\d{2}:\d{2}\b", value) else "minute"
        return {"value": parsed.isoformat(), "precision": precision,
                "meaning": meaning, "zone_known": parsed.tzinfo is not None}
    except (ValueError, TypeError, OverflowError):
        return {"value": None, "precision": "unknown", "meaning": meaning, "zone_known": False}


def time_range(value, meaning):
    if not value or value.get("meaning") != meaning or not value.get("zone_known"):
        return None
    duration = {"second": 1, "minute": 60, "day": 86400}.get(value.get("precision"))
    if duration is None or not isinstance(value.get("value"), str):
        return None
    try:
        parsed = datetime.fromisoformat(value["value"].replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return None
        start = parsed.astimezone(timezone.utc).timestamp()
        return (start, start + duration)
    except (ValueError, TypeError, OverflowError):
        return None


def exact(value, meaning):
    found = time_range(value, meaning)
    return found is not None and found[1] - found[0] == 1


def sufficient(item):
    return (item.get("account_verified") is True and bool(item.get("account"))
            and item.get("subject") is not None and bool(item.get("sender"))
            and (exact(item.get("sent"), "sent") or exact(item.get("received"), "received")))


def relation(a, b):
    """exact_metadata, distinct_metadata, or compatible_incomplete."""
    for field in ("account", "subject", "sender", "to", "cc"):
        left, right = a.get(field), b.get(field)
        if field in {"to", "cc"}:
            left = sorted(left) if isinstance(left, list) else left
            right = sorted(right) if isinstance(right, list) else right
        if left is not None and right is not None and left != right:
            return "distinct_metadata"
    if (a.get("filenames_complete") and b.get("filenames_complete")
            and a.get("filename_scope") in ORIGINAL_FILENAME_SCOPES
            and a.get("filename_scope") == b.get("filename_scope")
            and a.get("filenames") is not None and b.get("filenames") is not None
            and sorted(a["filenames"]) != sorted(b["filenames"])):
        return "distinct_metadata"
    exact_route = False
    for meaning in ("sent", "received"):
        left, right = time_range(a.get(meaning), meaning), time_range(b.get(meaning), meaning)
        if left is None or right is None:
            continue
        if max(left[0], right[0]) >= min(left[1], right[1]):
            return "distinct_metadata"
        if left == right and exact(a.get(meaning), meaning) and exact(b.get(meaning), meaning):
            # Receipt is an alternate route only when a source sending time is
            # unavailable; rounded sending evidence must not silently become exact.
            if meaning == "sent" or a.get("sent") is None or b.get("sent") is None:
                exact_route = True
    core_agrees = all(a.get(field) is not None and a.get(field) == b.get(field)
                      for field in ("account", "subject", "sender"))
    return "exact_metadata" if core_agrees and exact_route else "compatible_incomplete"


def resolve(incoming, records, lookup_complete=True):
    if not incoming.get("account_verified") or not incoming.get("account"):
        return {"status": "account_unverified", "record_ids": []}
    if not lookup_complete:
        return {"status": "lookup_incomplete", "record_ids": []}
    compatible = []
    for record in records:
        observed = record["metadata"]
        if observed.get("account") != incoming["account"]:
            continue
        match = relation(incoming, observed)
        if match != "distinct_metadata":
            compatible.append((record["record_id"], match))
    ids = sorted(item[0] for item in compatible)
    if len(compatible) > 1:
        return {"status": "ambiguous_metadata", "record_ids": ids}
    if compatible and compatible[0][1] == "exact_metadata" and sufficient(incoming):
        return {"status": "metadata_association", "record_ids": ids}
    if compatible or not sufficient(incoming):
        return {"status": "needs_metadata", "record_ids": ids}
    return {"status": "new_observation", "record_ids": []}


def record(identifier, metadata):
    # Project only allowed metadata. Neither caller-supplied source IDs nor any
    # content-derived field can enter a saved matching record.
    return {"record_id": identifier,
            "metadata": {key: copy.deepcopy(metadata.get(key)) for key in FIELDS}}


def subject_stem(subject):
    if subject is None:
        return None
    # Grouping-only demonstration; do not alter original identity subject.
    return re.sub(r"^(?:\s*re\s*:\s*)+", "", subject, flags=re.I)


def related(a, b):
    if a.get("account") != b.get("account") or subject_stem(a.get("subject")) is None:
        return False
    if subject_stem(a.get("subject")) != subject_stem(b.get("subject")):
        return False
    def participants(item):
        return set([item["sender"]] if item.get("sender") else []) | set(item.get("to") or []) | set(item.get("cc") or [])
    return bool(participants(a) & participants(b))
