"""Unexecuted, development-only examples of the approved metadata recipe.

These in-memory classes are fictional model representations, not production
schemas, adapter contracts, or a Drive persistence implementation. The supported
Date fixture domain is declared exact RFC-style seconds with an explicit numeric
timezone. Rejecting other views here does not select a production threshold.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime
import re
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class DateObservation:
    original: str
    meaning: str
    precision: str


@dataclass(frozen=True)
class Recipients:
    addresses: Tuple[str, ...]
    complete: bool = True


@dataclass(frozen=True)
class AttachmentInventory:
    names: Tuple[str, ...]
    original_names: bool
    scope: Optional[str]
    complete: bool


@dataclass(frozen=True)
class Observation:
    mailbox_id: str
    mailbox_verified: bool
    subject: Optional[str]
    sender: Optional[str]
    original_date: Optional[DateObservation]
    received_date: Optional[DateObservation] = None
    to: Optional[Recipients] = None
    cc: Optional[Recipients] = None
    attachments: Optional[AttachmentInventory] = None
    # Access hints have no path into normalize() or any comparison below.
    access_hints: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Comparison:
    mailbox_id: Optional[str]
    subject: Optional[str]
    sender: Optional[str]
    sent: Optional[datetime]
    received: Optional[datetime]
    to: Optional[Tuple[str, ...]]
    cc: Optional[Tuple[str, ...]]
    attachment_names: Optional[Tuple[str, ...]]
    attachment_scope: Optional[str]

    @property
    def core(self):
        return self.mailbox_id, self.subject, self.sender, self.sent

    @property
    def supported_core(self):
        return all(value is not None for value in self.core)


def normalize_subject(original: Optional[str]) -> Optional[str]:
    """Decode/unfold supported headers; keep case, interior text and prefixes."""
    if original is None:
        return None
    unfolded = re.sub(r"\r?\n(?=[ \t])", "", original)
    if "\n" in unfolded or "\r" in unfolded:
        return None
    try:
        return str(make_header(decode_header(unfolded))).strip()
    except (LookupError, UnicodeError):
        return None


_ADDRESS = re.compile(
    r"(?P<local>[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+)@"
    r"(?P<domain>[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)"
)


def normalize_address(original: str) -> Optional[str]:
    """Support fictional bare, bracketed and flattened display-address forms.

    This deliberately is not a universal RFC address parser. Unsupported forms
    stay unknown rather than manufacturing an address or rewriting local parts.
    """
    value = original.strip()
    if "<" in value or ">" in value:
        bracketed = re.fullmatch(r"([^<>@]*)<([^<>]+)>", value)
        if bracketed is None:
            return None
        value = bracketed.group(2).strip()
    elif " " in value or "\t" in value:
        pieces = value.rsplit(None, 1)
        if len(pieces) != 2 or "@" in pieces[0]:
            return None
        value = pieces[1]
    matched = _ADDRESS.fullmatch(value)
    if matched is None:
        return None
    return matched.group("local") + "@" + matched.group("domain").lower()


def normalize_recipients(value: Optional[Recipients]):
    if value is None or not value.complete:
        return None
    normalized = [normalize_address(address) for address in value.addresses]
    if any(address is None for address in normalized):
        return None
    # This fixture domain treats recipients as an address set within each role.
    return tuple(sorted(set(normalized)))


def fixture_instant(value: Optional[DateObservation], meaning: str):
    """Interpret only this model's declared exact zoned Date fixture domain."""
    if value is None or value.meaning != meaning or value.precision != "second":
        return None
    if re.search(r"\d{2}:\d{2}:\d{2} [+-]\d{4}$", value.original.strip()) is None:
        return None
    # RFC -0000 means the local timezone is unknown, not a known zero offset.
    if value.original.strip().endswith("-0000"):
        return None
    try:
        parsed = parsedate_to_datetime(value.original)
    except (TypeError, ValueError, OverflowError):
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def normalize(observation: Observation) -> Comparison:
    inventory = observation.attachments
    comparable_inventory = (
        inventory is not None
        and inventory.original_names
        and inventory.complete
        and inventory.scope is not None
        and all(name != "" for name in inventory.names)
    )
    return Comparison(
        mailbox_id=(observation.mailbox_id
                    if observation.mailbox_verified and observation.mailbox_id.strip()
                    else None),
        subject=normalize_subject(observation.subject),
        sender=(normalize_address(observation.sender)
                if observation.sender is not None else None),
        sent=fixture_instant(observation.original_date, "original_date"),
        received=fixture_instant(observation.received_date, "received"),
        to=normalize_recipients(observation.to),
        cc=normalize_recipients(observation.cc),
        attachment_names=tuple(sorted(inventory.names)) if comparable_inventory else None,
        attachment_scope=inventory.scope if comparable_inventory else None,
    )


def optional_conflict(left: Comparison, right: Comparison) -> bool:
    for name in ("received", "to", "cc"):
        first, second = getattr(left, name), getattr(right, name)
        if first is not None and second is not None and first != second:
            return True
    return (
        left.attachment_names is not None
        and right.attachment_names is not None
        and left.attachment_scope == right.attachment_scope
        and left.attachment_names != right.attachment_names
    )


@dataclass
class LogicalEmail:
    record_id: str
    observations: List[Observation]
    comparisons: List[Comparison]


@dataclass(frozen=True)
class Decision:
    status: str
    reason: str
    record_id: Optional[str] = None
    candidate_ids: Tuple[str, ...] = ()


@dataclass
class Catalog:
    records: Dict[str, LogicalEmail] = field(default_factory=dict)

    def admit(self, observation: Observation, new_owned_id: Optional[str] = None,
              lookup_complete: bool = True) -> Decision:
        """Model a completed relevant lookup; no provider/source calls occur."""
        comparison = normalize(observation)
        if not comparison.supported_core:
            return Decision("pending", "outside-supported-metadata-fixture-domain")
        if not lookup_complete:
            return Decision("pending", "relevant-index-lookup-incomplete")
        candidates = []
        for record in self.records.values():
            if record.comparisons[0].core != comparison.core:
                continue
            if not any(optional_conflict(saved, comparison)
                       for saved in record.comparisons):
                candidates.append(record.record_id)
        if len(candidates) > 1:
            return Decision("pending", "several-compatible-existing-records",
                            candidate_ids=tuple(sorted(candidates)))
        if candidates:
            record_id = candidates[0]
            record = self.records[record_id]
            record.observations.append(observation)
            record.comparisons.append(comparison)
            return Decision("reuse", "supported-metadata-agreement", record_id)
        if not new_owned_id or new_owned_id in self.records:
            raise ValueError("A new model record requires an unused School-OS-owned ID")
        self.records[new_owned_id] = LogicalEmail(
            new_owned_id, [observation], [comparison]
        )
        return Decision("new", "supported-metadata-and-complete-lookup", new_owned_id)


@dataclass
class ReadCandidate:
    work_reference: str
    original_filename: Optional[str]
    state: str = "unread"


@dataclass
class AttachmentReadPass:
    """A fictional work pass, not stable individual attachment identities."""
    work_id: str
    parent_email_id: str
    inventory_scope: Optional[str]
    inventory_complete: bool
    candidates: List[ReadCandidate]

    def __post_init__(self):
        references = [candidate.work_reference for candidate in self.candidates]
        if len(set(references)) != len(references):
            raise ValueError("Candidate references must be distinct within this work pass")

    def groups(self):
        result = {}
        for candidate in self.candidates:
            key = (self.parent_email_id, candidate.original_filename)
            result.setdefault(key, []).append(candidate.work_reference)
        return result

    def record_read(self, work_reference: str):
        for candidate in self.candidates:
            if candidate.work_reference == work_reference:
                candidate.state = "read"
                return
        raise KeyError(work_reference)

    @property
    def all_exposed_candidates_read(self):
        return all(candidate.state == "read" for candidate in self.candidates)

    @property
    def declared_inventory_read(self):
        # These flags model reading only. They do not prove persistence, exact
        # attachment identity, complete semantic extraction, or body coverage.
        return (self.inventory_complete and self.inventory_scope is not None
                and self.all_exposed_candidates_read)


@dataclass(frozen=True)
class WindowScope:
    mailbox_id: str
    configured_scope: str
    start: str
    end: str
    date_meaning: str
    timezone: str
    precision: str
    track: str


@dataclass
class WindowProgress:
    """Abstract serializable progress; not a canonical schema or Drive adapter."""
    scope: WindowScope
    enumeration: str = "unfinished"
    observed_email_ids: List[str] = field(default_factory=list)

    def observe_page(self, email_ids: Tuple[str, ...], *,
                     continuation_available: bool, exhaustion_established: bool):
        if continuation_available and exhaustion_established:
            raise ValueError("Continuation contradicts claimed listing exhaustion")
        for record_id in email_ids:
            if record_id not in self.observed_email_ids:
                self.observed_email_ids.append(record_id)
        # No page-size threshold is a completeness signal. Processing coverage
        # is deliberately absent: enumeration cannot complete content reading.
        self.enumeration = "exhausted" if exhaustion_established else "unfinished"

    def snapshot(self):
        # There is intentionally no required token, source handle, local path,
        # source content, conversation reference or external scheduler state.
        return asdict(self)

    @classmethod
    def from_snapshot(cls, snapshot):
        return cls(WindowScope(**snapshot["scope"]), snapshot["enumeration"],
                   list(snapshot["observed_email_ids"]))

    def resume_instruction(self):
        return "no-unfinished-window" if self.enumeration == "exhausted" else "repeat-window"
