#!/usr/bin/env python3
"""Build independent fictional MIME observations and physical-delivery truth.

Python 3.9+, standard library only. This module never imports a parser or matcher.
Truth describes the fictional delivery history, not what a resolver should infer.
"""

import base64
import hashlib
import itertools
import json
from pathlib import Path
import quopri
import struct
import zlib


ROOT = Path(__file__).resolve().parent / "corpus"
DEFAULT_RECEIPT = "2026-08-24T09:12:34-07:00"
SUBJECT = "Café field trip — final details"
BODY = "Hello families,\n\nThe café field trip leaves at 09:30.\nBring a signed permission slip and a water bottle.\nReturn the slip by Thursday.\n\nThank you,\nJuniper School\n"
HTML = "<html><body><p>Hello families,</p><p>The café field trip leaves at 09:30.<br>Bring a signed permission slip and a water bottle.<br>Return the slip by Thursday.</p><p>Thank you,<br>Juniper School</p></body></html>"


def encoded_header(value, charset="utf-8"):
    return "=?{}?b?{}?=".format(charset, base64.b64encode(value.encode(charset)).decode("ascii"))


def envelope(subject=SUBJECT, date="Mon, 24 Aug 2026 09:10:00 -0700",
             sender="Juniper School <office@example.org>", to="Family One <family@example.org>",
             cc="Class Guide <guide@example.org>", exclude=(), encoded=False, extra=()):
    pairs = [("From", sender), ("To", to), ("Cc", cc), ("Subject", subject), ("Date", date)]
    result = []
    for key, value in pairs:
        if key in exclude:
            continue
        if key == "Subject" and encoded:
            value = encoded_header(value)
        result.append((key + ": " + value).encode("utf-8"))
    result.extend(item.encode("utf-8") for item in extra)
    return b"\n".join(result) + b"\nMIME-Version: 1.0\n"


def text_part(text, subtype="plain", charset="utf-8", transfer="8bit"):
    payload = text.encode(charset)
    if transfer == "quoted-printable":
        payload = quopri.encodestring(payload)
    elif transfer == "base64":
        payload = base64.encodebytes(payload)
    header = 'Content-Type: text/{}; charset="{}"\nContent-Transfer-Encoding: {}\n\n'.format(subtype, charset, transfer)
    return header.encode("ascii") + payload


def multipart(parts, subtype="mixed", boundary="fictional-boundary"):
    start = 'Content-Type: multipart/{}; boundary="{}"\n\n'.format(subtype, boundary).encode("ascii")
    marker = b"--" + boundary.encode("ascii")
    return start + b"".join(marker + b"\n" + part.rstrip(b"\n") + b"\n" for part in parts) + marker + b"--\n"


def binary_part(data, media_type, filename=None, cid=None, width=76, disposition="attachment"):
    headers = ["Content-Type: " + media_type, "Content-Transfer-Encoding: base64"]
    if filename is not None:
        headers.append('Content-Disposition: {}; filename="{}"'.format(disposition, filename))
    if cid is not None:
        headers.append("Content-ID: <{}>".format(cid))
    encoded = base64.b64encode(data)
    payload = b"\n".join(encoded[i:i + width] for i in range(0, len(encoded), width))
    return "\n".join(headers).encode("ascii") + b"\n\n" + payload + b"\n"


def pdf(text):
    content = "BT /F1 12 Tf 36 100 Td ({}) Tj ET\n".format(text).encode("ascii")
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
               b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n" + content + b"endstream"]
    output = b"%PDF-1.4\n%fictional\n"
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(output))
        output += str(number).encode("ascii") + b" 0 obj\n" + obj + b"\nendobj\n"
    xref = len(output)
    output += b"xref\n0 6\n0000000000 65535 f \n"
    output += b"".join(("{:010d} 00000 n \n".format(offset)).encode("ascii") for offset in offsets[1:])
    output += b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n" + str(xref).encode("ascii") + b"\n%%EOF\n"
    return output


def png(rgb):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"\x00" + bytes(rgb))) + chunk(b"IEND", b""))


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "raw").mkdir(exist_ok=True)
    observations = []
    payloads = {}

    def add(name, content, occurrence, communication=None, received=DEFAULT_RECEIPT,
            precision="second", projection="raw", case="", rationale="", projection_fields=None,
            indistinguishable_group=None):
        filename = "raw/{}.eml".format(name)
        (ROOT / filename).write_bytes(content)
        observation = {"observation_id": name, "file": filename, "occurrence_id": occurrence,
                       "communication_id": communication or occurrence, "account": "fixture-mailbox",
                       "received_at": {"value": received, "precision": precision if received else "unknown",
                                       "availability": "available" if received else "missing"},
                       "projection": projection, "case": case, "rationale": rationale,
                       "raw_sha256": hashlib.sha256(content).hexdigest()}
        if projection_fields:
            observation["projection_fields"] = projection_fields
        if indistinguishable_group:
            observation["indistinguishable_group"] = indistinguishable_group
        observations.append(observation)
        payloads[name] = content

    raw = envelope() + text_part(BODY)
    add("trip_plain_utf8", raw, "trip", case="baseline_unicode")
    add("trip_qp_utf8", envelope(encoded=True) + text_part(BODY, transfer="quoted-printable"), "trip", case="quoted_printable")
    add("trip_base64_utf8", envelope(encoded=True) + text_part(BODY, transfer="base64"), "trip", case="base64_text")
    # The em dash appears only in the header, whose UTF-8 encoding is independent.
    add("trip_latin1_qp", envelope(encoded=True) + text_part(BODY, charset="iso-8859-1", transfer="quoted-printable"), "trip", case="charset_iso_8859_1")
    add("trip_crlf", raw.replace(b"\n", b"\r\n"), "trip", case="crlf_line_endings")
    folded = envelope(subject="unused", encoded=True).replace(encoded_header("unused").encode(),
        (encoded_header("Café field trip ") + "\n\t" + encoded_header("— final details")).encode())
    add("trip_headers_folded", folded + text_part(BODY, transfer="base64"), "trip", case="folded_encoded_header")
    add("trip_alternative", envelope(encoded=True) + multipart([text_part(BODY), text_part(HTML, "html")], "alternative", "trip-alt"), "trip", case="multipart_alternative")
    add("trip_html_only", envelope(encoded=True) + text_part(HTML, "html"), "trip", case="html_only_equivalent", rationale="The display text matches the plain version; formatting is a presentation choice.")
    add("trip_body_only", text_part(BODY), "trip", received=None, projection="body_only", case="body_only_projection", projection_fields={"body_complete": True, "attachments_complete": False, "envelope_complete": False})
    add("trip_partial_envelope", envelope(exclude=("To", "Cc", "Date")) + text_part(BODY), "trip", case="partial_envelope", projection_fields={"body_complete": True, "envelope_complete": False})
    add("trip_snippet", text_part("Hello families,\n\nThe café field trip leaves"), "trip", received=None, projection="snippet", case="truncated_snippet", projection_fields={"body_complete": False, "attachments_complete": False, "envelope_complete": False})
    add("trip_body_changed", envelope() + text_part(BODY.replace("09:30", "10:15")), "trip-correction", case="same_envelope_changed_body", rationale="A separate correction reused the sender, subject and declared times.")
    reply_env = dict(subject="Re: " + SUBJECT, sender="Class Guide <guide@example.org>", date="Mon, 24 Aug 2026 10:10:00 -0700")
    add("reply_one", envelope(**reply_env) + text_part("The bus now departs from the west gate.\n"), "reply-one", received="2026-08-24T10:10:05-07:00", case="thread_reply")
    add("reply_two", envelope(**reply_env) + text_part("Please use the east gate instead.\n"), "reply-two", received="2026-08-24T10:10:05-07:00", case="same_thread_new_reply_same_envelope")
    quote = "On Monday, Juniper School wrote:\n" + "\n".join("> " + line for line in BODY.splitlines()) + "\n"
    add("reply_with_quote", envelope(**reply_env) + text_part("We will bring the signed slip.\n\n" + quote), "quoted-reply", received="2026-08-24T10:10:05-07:00", case="quoted_reply", rationale="Quoted original content does not make the reply the original delivery.")
    forward_env = dict(subject="Fwd: " + SUBJECT, sender="Family Two <second-family@example.org>", date="Mon, 24 Aug 2026 11:00:00 -0700")
    forward = "For the family calendar.\n\n---------- Forwarded message ----------\nFrom: Juniper School <office@example.org>\nSubject: " + SUBJECT + "\n\n" + BODY
    add("forward_inline", envelope(**forward_env) + text_part(forward), "forward-inline", received="2026-08-24T11:00:05-07:00", case="inline_forward")
    add("quote_only_delivery", envelope(**reply_env) + text_part(quote), "quote-only", received="2026-08-24T10:10:05-07:00", case="quote_only_new_delivery")

    form_one, form_two = pdf("Permission slip: return Thursday."), pdf("Permission slip: return Friday.")
    pdf_env = envelope(subject="Permission form", date="Tue, 25 Aug 2026 08:00:00 -0700")
    cover = text_part("Please review the attached permission form.\n")
    form_a = binary_part(form_one, "application/pdf", "permission.pdf")
    form_b = binary_part(form_two, "application/pdf", "permission.pdf")
    def form_message(parts, boundary="forms-mixed"):
        return pdf_env + multipart([cover] + parts, boundary=boundary)
    add("pdf_one", form_message([form_a]), "pdf-one", case="pdf_attachment")
    add("pdf_one_rewrapped", form_message([binary_part(form_one, "application/pdf", "permission.pdf", width=52)], "different-forms-boundary"), "pdf-one", case="binary_base64_wrapping_boundary")
    add("pdf_payload_changed", form_message([form_b]), "pdf-changed", case="attachment_payload_changed")
    add("pdf_same_name_two_payloads", form_message([form_a, form_b]), "pdf-two-payloads", case="duplicate_filename_distinct_bytes")
    add("pdf_two_reordered", form_message([form_b, form_a]), "pdf-two-payloads", case="attachment_order_presentation", rationale="An explicitly stipulated connector reserialization of this one original delivery reorders its attachment parts while retaining both named payloads. This is not a rule that MIME order is universally immaterial or that reordered raw sources are identical.")
    add("pdf_duplicate_twice", form_message([form_a, form_a]), "pdf-duplicate-twice", case="attachment_multiplicity", rationale="A separate delivery contains two copies, not one attachment.")
    add("pdf_no_attachment", form_message([]), "pdf-no-attachment", case="attachment_removed")
    add("pdf_filename_changed", form_message([binary_part(form_one, "application/pdf", "family-copy.pdf")]), "pdf-renamed-delivery", case="attachment_filename_changed", rationale="This is an independently transmitted message with a renamed attachment.")
    add("pdf_body_only", text_part("Please review the attached permission form.\n"), "pdf-one", received=None, projection="body_only", case="attachment_omitted_projection", projection_fields={"body_complete": True, "attachments_complete": False, "envelope_complete": False})

    red, blue = png((240, 32, 32)), png((32, 32, 240))
    image_env = envelope(subject="Garden day poster", date="Wed, 26 Aug 2026 08:00:00 -0700")
    def cid_message(cid, payload):
        html = '<html><body><p>Garden day is Saturday.</p><img src="cid:{}" alt="Garden day poster"></body></html>'.format(cid)
        return image_env + multipart([text_part(html, "html"), binary_part(payload, "image/png", "poster.png", cid=cid, disposition="inline")], "related", "poster-related")
    add("inline_cid_red", cid_message("poster-one@example.org", red), "poster-red", case="inline_cid_image")
    add("inline_cid_token_changed", cid_message("replacement-token@example.org", red), "poster-red", case="cid_token_presentation", rationale="Only the related-part CID token and its matching reference change.")
    add("inline_cid_payload_changed", cid_message("poster-one@example.org", blue), "poster-blue", case="inline_payload_changed")
    data_html = '<html><body><p>Garden day is Saturday.</p><img src="data:image/png;base64,{}" alt="Garden day poster"></body></html>'.format(base64.b64encode(red).decode())
    add("inline_data_uri", image_env + text_part(data_html, "html"), "poster-red", case="data_uri_inline_presentation", rationale="A faithful rendering embeds the exact CID image bytes as a data URI; filenames/CIDs are packaging for this inline display resource.")
    for name, url, occ in [("remote_image_reference", "https://example.org/fictional/garden-poster.png", "remote-poster-one"), ("remote_image_url_changed", "https://example.org/fictional/updated-poster.png", "remote-poster-two")]:
        remote_html = '<html><body><p>Garden day is Saturday.</p><img src="{}" alt="Garden day poster"></body></html>'.format(url)
        add(name, image_env + text_part(remote_html, "html"), occ, case="remote_image_reference", rationale="Only the remote URL is observable. No bytes are fetched or equality to embedded pixels assumed.")
    image_only_env = envelope(subject="Poster", date="Thu, 27 Aug 2026 08:00:00 -0700")
    add("image_only_red", image_only_env + binary_part(red, "image/png", disposition="inline"), "image-only-red", case="image_only_email")
    add("image_only_red_rewrapped", image_only_env + binary_part(red, "image/png", width=40, disposition="inline"), "image-only-red", case="image_only_reencoding")
    add("image_only_blue", image_only_env + binary_part(blue, "image/png", disposition="inline"), "image-only-blue", case="image_only_payload_changed")

    nested_header = b'Content-Type: message/rfc822\nContent-Disposition: attachment; filename="original.eml"\n\n'
    nested_env = envelope(subject="Archived field trip note", sender="Family Two <second-family@example.org>")
    nested_cover = text_part("The original message is attached for reference.\n")
    add("nested_message", nested_env + multipart([nested_cover, nested_header + raw], boundary="nested-outer"), "nested-original", case="message_rfc822_attachment")
    add("nested_message_reencoded", nested_env + multipart([nested_cover, nested_header + envelope(encoded=True) + text_part(BODY, transfer="base64")], boundary="nested-repacked"), "nested-original", case="nested_message_inner_presentation")
    add("nested_message_changed", nested_env + multipart([nested_cover, nested_header + envelope() + text_part(BODY.replace("Thursday", "Friday"))], boundary="nested-outer"), "nested-changed", case="nested_message_payload_changed")

    duplicate = envelope(subject="Monthly library reminder", date="Fri, 28 Aug 2026 08:00:00 -0700") + text_part("Please return library books on Monday.\n")
    for name, occurrence in [("identical_delivery_a", "library-delivery-a"), ("identical_delivery_b", "library-delivery-b"), ("identical_delivery_a_readback", "library-delivery-a")]:
        add(name, duplicate, occurrence, communication="library-reminder", received="2026-08-28T08:00:01-07:00", case="indistinguishable_physical_delivery", indistinguishable_group="library-identical", rationale="The fixture history knows the delivery, but bytes, account and receipt evidence cannot distinguish the two deliveries.")
    add("identical_delivery_later_receipt", duplicate, "library-delivery-c", communication="library-reminder", received="2026-08-29T08:00:01-07:00", case="identical_content_distinct_receipt")
    add("trip_received_timezone", raw, "trip", received="2026-08-24T16:12:34+00:00", case="receipt_timezone_presentation")
    add("trip_received_minute", raw, "trip", received="2026-08-24T09:12:00-07:00", precision="minute", case="coarse_received_time", rationale="The connector reports a containing minute, not a zero-second exact receipt.")
    add("trip_missing_sender_date", envelope(exclude=("Date",)) + text_part(BODY), "trip", case="missing_sender_date")
    add("trip_recipient_roles_swapped", envelope(to="Class Guide <guide@example.org>", cc="Family One <family@example.org>") + text_part(BODY), "trip-swapped-recipients", case="to_cc_roles_changed")
    add("trip_sender_changed", envelope(sender="Garden Club <garden-club@example.org>") + text_part(BODY), "trip-other-sender", case="sender_changed")
    add("trip_display_address_format", envelope(sender=encoded_header("Juniper School") + " <office@example.org>", to='"Family One" <family@example.org>', cc='"Class Guide" <guide@example.org>', encoded=True) + text_part(BODY), "trip", case="address_display_format")
    position_html = '<html><body><img src="cid:poster-one@example.org" alt="Garden day poster"><p>Garden day is Saturday.</p></body></html>'
    add("inline_cid_position_changed", image_env + multipart([text_part(position_html, "html"), binary_part(red, "image/png", "poster.png", cid="poster-one@example.org", disposition="inline")], "related", "poster-related"), "poster-position-changed", case="inline_relationship_changed", rationale="A separately authored communication moves the same image from after the body text to before it. Resource bytes alone cannot establish the image's relationship to surrounding content.")
    add("trip_received_missing", raw, "trip", received=None, case="raw_received_unavailable", rationale="The raw message is available but this observation lacks actual receiving-system time; Date must not substitute for it.")
    related_children = [
        b"Content-ID: <root-alpha@example.org>\n" + text_part("<html><body><p>The event is Monday.</p></body></html>", "html"),
        b"Content-ID: <root-beta@example.org>\n" + text_part("<html><body><p>The event is Tuesday.</p></body></html>", "html"),
    ]
    related_envelope = envelope(subject="Select the current announcement")
    related_payload = multipart(related_children, "related", "root-selection-related")
    for suffix in ("alpha", "beta"):
        content = related_payload.replace(b"multipart/related;", ('multipart/related; type="text/html"; start="<root-{}@example.org>";'.format(suffix)).encode("ascii"), 1)
        add("related_root_" + suffix, related_envelope + content, "related-root-" + suffix, case="related_start_selects_body", rationale="These separately authored messages have identical MIME children and order, but multipart/related start selects a different HTML root. Selecting Monday versus Tuesday changes the communication.")
    unresolved_html = '<html><body><p>Garden day is Saturday.</p><img src="cid:missing-poster@example.org" alt="Garden day poster"></body></html>'
    add("inline_unresolved_cid", image_env + text_part(unresolved_html, "html"), "poster-unresolved", case="unresolved_cid_reference", rationale="The body references an absent related part. Missing bytes remain unknown and are not an empty or matching image.")
    unknown_charset = raw.replace(b'charset="utf-8"', b'charset="x-fictional-unknown-charset"', 1)
    add("trip_unknown_charset", unknown_charset, "trip", case="unknown_declared_charset", rationale="A connector presentation declares an unsupported charset. Fixture history identifies the original, but a reader cannot assert reliable decoded text solely by guessing an encoding.")

    # These receipt values are independent fictional receiving-system events,
    # assigned separately from Date rather than parsed or derived from it.
    for observation in observations:
        name = observation["observation_id"]
        if observation["received_at"]["availability"] == "available":
            if name.startswith("pdf_"):
                observation["received_at"]["value"] = "2026-08-25T08:00:05-07:00"
            elif name.startswith(("inline_", "remote_")):
                observation["received_at"]["value"] = "2026-08-26T08:00:05-07:00"
            elif name.startswith("image_only_"):
                observation["received_at"]["value"] = "2026-08-27T08:00:05-07:00"

    targeted = [
        ("trip_plain_utf8", other) for other in (
            "trip_qp_utf8", "trip_base64_utf8", "trip_latin1_qp", "trip_crlf",
            "trip_headers_folded", "trip_alternative", "trip_html_only", "trip_body_only",
            "trip_partial_envelope", "trip_snippet", "trip_body_changed", "reply_one",
            "reply_with_quote", "forward_inline", "quote_only_delivery", "trip_received_timezone",
            "trip_received_minute", "trip_missing_sender_date", "trip_recipient_roles_swapped",
            "trip_sender_changed", "trip_display_address_format", "trip_received_missing")]
    targeted += [
        ("reply_one", "reply_two"), ("pdf_one", "pdf_one_rewrapped"),
        ("pdf_one", "pdf_payload_changed"), ("pdf_one", "pdf_same_name_two_payloads"),
        ("pdf_same_name_two_payloads", "pdf_two_reordered"), ("pdf_one", "pdf_duplicate_twice"),
        ("pdf_one", "pdf_no_attachment"), ("pdf_one", "pdf_filename_changed"),
        ("pdf_one", "pdf_body_only"), ("pdf_payload_changed", "pdf_body_only"),
        ("inline_cid_red", "inline_cid_token_changed"), ("inline_cid_red", "inline_cid_payload_changed"),
        ("inline_cid_red", "inline_data_uri"), ("inline_cid_red", "remote_image_reference"),
        ("remote_image_reference", "remote_image_url_changed"),
        ("inline_cid_red", "inline_cid_position_changed"),
        ("image_only_red", "image_only_red_rewrapped"), ("image_only_red", "image_only_blue"),
        ("nested_message", "nested_message_reencoded"), ("nested_message", "nested_message_changed"),
        ("trip_plain_utf8", "nested_message"),
        ("identical_delivery_a", "identical_delivery_b"),
        ("identical_delivery_a", "identical_delivery_a_readback"),
        ("identical_delivery_a", "identical_delivery_later_receipt"),
        ("related_root_alpha", "related_root_beta"),
        ("inline_cid_red", "inline_unresolved_cid"),
        ("trip_plain_utf8", "trip_unknown_charset"),
    ]
    targeted_keys = {frozenset(pair) for pair in targeted}

    pairs = []
    for left, right in itertools.combinations(observations, 2):
        if left["occurrence_id"] == right["occurrence_id"]:
            truth = "same_occurrence"
            rationale = "Independent fixture history assigns both presentations to one physical delivery; missing fields may prevent a resolver from proving it."
        elif left.get("indistinguishable_group") and left.get("indistinguishable_group") == right.get("indistinguishable_group"):
            truth = "indistinguishable_occurrence"
            rationale = "Distinct physical deliveries have byte-identical messages and identical available account/receipt evidence; communication is shared."
        else:
            truth = "distinct_occurrence"
            rationale = "Independent fixture history assigns distinct physical deliveries; this label is not a claim that every partial projection can distinguish them."
        pairs.append({"left": left["observation_id"], "right": right["observation_id"], "truth": truth,
                      "targeted": frozenset((left["observation_id"], right["observation_id"])) in targeted_keys,
                      "rationale": rationale})
    counts = {truth: sum(pair["truth"] == truth for pair in pairs) for truth in ("same_occurrence", "distinct_occurrence", "indistinguishable_occurrence")}
    manifest = {"schema_version": 1, "corpus_origin": "independent_fictional_generation",
                "truth_semantics": "Labels describe independently authored physical-delivery history, never matcher output. Same communication does not prove same physical occurrence. Same-occurrence projections may be insufficient to resolve.",
                "observation_count": len(observations), "pair_count": len(pairs), "pair_truth_counts": counts,
                "targeted_pair_count": len(targeted),
                "projection_semantics": {"raw": "Read the actual MIME file; missing headers remain unavailable.",
                                         "body_only": "Only visible body evidence is available; envelope and omitted attachments are unavailable, not empty.",
                                         "snippet": "A truncated body projection; no full-body equality or completeness claim is permitted."},
                "time_semantics": "received_at is independent synthetic receiving-system evidence, never inferred from Date. Minute precision denotes the containing minute. Offset changes preserve the instant.",
                "observations": observations, "pairs": pairs}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    names = {entry["file"] for entry in observations}
    stale = [path for path in (ROOT / "raw").glob("*.eml") if str(path.relative_to(ROOT)) not in names]
    if stale:
        raise RuntimeError("Unexpected files in generated corpus; remove stale fixture files deliberately.")
    digest = hashlib.sha256()
    for path in sorted((ROOT / "raw").glob("*.eml")) + [ROOT / "manifest.json"]:
        digest.update(str(path.relative_to(ROOT)).encode("utf-8") + b"\0" + path.read_bytes())
    print(json.dumps({"observations": len(observations), "pairs": len(pairs), "truth_counts": counts, "corpus_sha256": digest.hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
