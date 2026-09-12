"""Development-only MIME observations for the existing prepared-input matcher.

This deliberately exposes the matcher's flat body/attachment boundary rather
than silently replacing it with a new identity algorithm. Bytes are read from
independently generated fictional .eml files. Only digests and coverage are
returned. No remote resource is fetched and no semantic extraction is claimed.
"""
from __future__ import annotations

import base64
import hashlib
import json
from datetime import timezone
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, unquote_to_bytes


def digest(value):
    if not isinstance(value, bytes):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def mailboxes(message, field):
    if field not in message:
        return None if field == "From" else []
    result = []
    for _, address in getaddresses([str(x) for x in message.get_all(field, [])]):
        local, separator, domain = address.rpartition("@")
        result.append(local + separator + domain.lower() if separator else address)
    return result


def source_headers(message):
    date = None
    if message.get("Date"):
        try:
            parsed = parsedate_to_datetime(str(message["Date"]))
            if parsed.tzinfo is not None:
                date = parsed.astimezone(timezone.utc).isoformat()
        except (ValueError, TypeError, OverflowError):
            pass
    sender = mailboxes(message, "From")
    return {"sender": sender[0] if sender and len(sender) == 1 else None,
            "sent_at": date,
            "subject": str(message["Subject"]) if "Subject" in message else None,
            "to": mailboxes(message, "To"), "cc": mailboxes(message, "Cc")}


class References(HTMLParser):
    """Inventory common references; not a browser, CSS parser or renderer."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references = []
        self.unsupported = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"img", "source", "image", "object", "iframe", "link"}:
            for key in ("src", "href", "xlink:href", "data"):
                if attrs.get(key):
                    self.references.append((tag, key, attrs[key]))
        if "srcset" in attrs:
            self.unsupported.append("srcset-needs-a-resource-parser")
        if "style" in attrs or tag in {"style", "svg"}:
            self.unsupported.append("css-or-svg-needs-a-resource-parser")


def inspect_message(message):
    bodies, attachments, html, defects, topology = [], [], [], [], []
    cid_targets = {}

    def walk(part, path):
        mime = part.get_content_type()
        defects.extend(type(d).__name__ for d in part.defects)
        topology.append({"path": path, "mime": mime,
                         "disposition": part.get_content_disposition(),
                         "related_root": part.get_param("start")})
        # message/rfc822 is itself an attachment, not another outer reply.
        if mime == "message/rfc822":
            children = part.get_payload()
            if not isinstance(children, list):
                defects.append("unread-nested-message")
                nested_digest = None
            else:
                nested = []
                for child in children:
                    parsed = inspect_message(child)
                    nested.append({"headers": source_headers(child),
                                   "body_digest": parsed["body_digest"],
                                   "attachments": parsed["attachments"]})
                    defects.extend(parsed["defects"])
                nested_digest = digest(nested)
            attachments.append({"name": part.get_filename() or "", "mime": mime,
                                "digest": nested_digest})
            return
        if part.is_multipart():
            for index, child in enumerate(part.iter_parts()):
                walk(child, path + [index])
            return
        raw = part.get_payload(decode=True)
        defects.extend(type(d).__name__ for d in part.defects)
        if raw is None:
            defects.append("missing-decoded-payload")
            raw = b""
        attachment = (part.get_content_disposition() == "attachment"
                      or part.get_filename() is not None
                      or part.get_content_maintype() != "text")
        if attachment:
            entry = {"name": part.get_filename() or "", "mime": mime,
                     "digest": digest(raw)}
            attachments.append(entry)
            if part.get("Content-ID"):
                cid = str(part["Content-ID"]).strip().strip("<>")
                cid_targets.setdefault(cid, []).append({"path": path,
                                                       "digest": entry["digest"]})
        else:
            try:
                decoded = raw.decode(part.get_content_charset() or "ascii", errors="strict")
            except (UnicodeError, LookupError):
                defects.append("undecodable-text")
                decoded = ""
            decoded = decoded.replace("\r\n", "\n")
            bodies.append({"mime": mime, "text": decoded})
            if mime == "text/html":
                html.append((path, decoded))

    walk(message, [])
    resources, limitations = [], []
    for path, markup in html:
        parser = References()
        parser.feed(markup)
        limitations.extend(parser.unsupported)
        for tag, attribute, value in parser.references:
            entry = {"html_path": path, "tag": tag, "attribute": attribute}
            if value.lower().startswith("cid:"):
                targets = cid_targets.get(unquote(value[4:]), [])
                entry.update(kind="cid", targets=targets,
                             status="read" if len(targets) == 1 else
                             "missing" if not targets else "ambiguous-scope")
                # A global lookup is only diagnostic. Scoped alternative/related
                # CID resolution must be qualified before declaring extraction.
            elif value.lower().startswith("data:"):
                try:
                    header, encoded = value.split(",", 1)
                    content = (base64.b64decode(encoded, validate=True)
                               if header.lower().endswith(";base64")
                               else unquote_to_bytes(encoded))
                    entry.update(kind="data", digest=digest(content), status="read")
                except (ValueError, TypeError):
                    entry.update(kind="data", status="invalid")
            elif value.lower().startswith(("http:", "https:")):
                entry.update(kind="remote", status="unread", locator_digest=digest(value))
            else:
                entry.update(kind="other", status="unsupported")
            resources.append(entry)
    return {"body_digest": digest(bodies), "attachments": attachments,
            "defects": sorted(set(defects)), "resources": resources,
            "resource_limitations": sorted(set(limitations)), "topology": topology,
            "body_parts": len(bodies), "html_parts": len(html)}


def observe(fixture, corpus):
    message = BytesParser(policy=policy.default).parsebytes(
        (Path(corpus) / fixture["file"]).read_bytes())
    parsed = inspect_message(message)
    receipt = fixture["received_at"]
    witness = {"account": fixture["account"], "account_verified": True,
               **source_headers(message), "received_at": receipt["value"],
               "alias": None, "rfc_message_id": None, "in_reply_to": None,
               "thread": None, "profile": "mime-decoded-flat-v1",
               "body_complete": not parsed["defects"],
               "attachment_inventory_complete": not parsed["defects"],
               "attachments": parsed["attachments"], "body_digest": parsed["body_digest"]}
    controls = fixture.get("projection_fields", {})
    if fixture["projection"] != "raw":
        # Even when the underlying synthetic bytes exist for grading, a limited
        # connector projection must never be marked a complete read.
        witness["body_complete"] = fixture["projection"] == "body_only"
        witness["attachment_inventory_complete"] = False
    if controls.get("envelope_complete") is False:
        for header, field in (("From", "sender"), ("To", "to"), ("Cc", "cc"),
                              ("Date", "sent_at"), ("Subject", "subject")):
            if header not in message:
                witness[field] = None
    if "attachments_complete" in controls:
        witness["attachment_inventory_complete"] = controls["attachments_complete"]
    # Explicit connector projection controls; never infer from truth labels.
    for field in ("sender", "sent_at", "received_at", "subject", "to", "cc",
                  "body_complete", "attachment_inventory_complete", "profile"):
        if field in controls:
            witness[field] = controls[field]
    if controls.get("reverse_attachment_listing"):
        witness["attachments"] = list(reversed(witness["attachments"]))
    if controls.get("attachment_bytes_unavailable"):
        witness["attachments"] = [{**item, "digest": None} for item in witness["attachments"]]
    return witness, {"observation_id": fixture["observation_id"],
                     "received_precision": receipt["precision"],
                     "received_availability": receipt["availability"],
                     "projection": fixture["projection"],
                     **{key: parsed[key] for key in
                        ("defects", "resources", "resource_limitations", "topology",
                         "body_parts", "html_parts")},
                     "attachment_count": len(witness["attachments"])}
