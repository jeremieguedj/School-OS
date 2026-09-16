"""Small, provider-free comparison helpers. No I/O or record operations.

Callers retain original observations and follow the approved metadata recipe.
Results neither establish identity nor prove processing or persistence.
"""

import base64
import binascii
import quopri
import re


_WORD = re.compile(r"=\?([A-Za-z0-9_-]+)\?([bBqQ])\?([^?\s]+)\?=")
_CHARSETS = {
    "ascii", "us-ascii", "utf-8", "utf8", "iso-8859-1", "latin-1",
    "latin1", "windows-1252", "cp1252",
}


def _require_text(value):
    if not isinstance(value, str):
        raise TypeError("Expected a string; missing values must remain unknown")


def _check_subject_text(text):
    if any((ord(c) < 32 and c != "\t") or ord(c) == 127 for c in text):
        raise ValueError("Unsupported subject control character or header wrap")
    try:
        text.encode("utf-8", errors="strict")
    except UnicodeError:
        raise ValueError("Subject contains unsupported Unicode") from None


def normalize_subject(text: str, *, representation: str) -> str:
    """Normalize an explicitly identified raw_header or decoded subject.

    Raw headers unfold CRLF+WSP and strictly decode supported B/Q words once.
    Decoded text is never decoded or unfolded again. Both trim outer whitespace
    and preserve literal interior spacing/case/prefixes. No representation guess.
    """
    _require_text(text)
    _require_text(representation)
    if representation == "decoded":
        _check_subject_text(text)
        return text.strip()
    if representation != "raw_header":
        raise ValueError("Subject representation must be raw_header or decoded")
    unfolded = re.sub(r"\r\n(?=[ \t])", "", text)
    _check_subject_text(unfolded)
    pieces = []
    end = 0
    previous_word = False
    for word in _WORD.finditer(unfolded):
        literal = unfolded[end:word.start()]
        if "=?" in literal:
            raise ValueError("Unsupported or malformed encoded subject word")
        if ((word.start() and unfolded[word.start() - 1] not in " \t")
                or (word.end() < len(unfolded)
                    and unfolded[word.end()] not in " \t")):
            raise ValueError("Encoded subject words require whitespace separation")
        charset, encoding, payload = word.groups()
        if charset.lower() not in _CHARSETS or len(word.group()) > 75:
            raise ValueError("Unsupported charset or encoded-word length")
        try:
            raw = payload.encode("ascii", errors="strict")
            if encoding.lower() == "b":
                decoded = base64.b64decode(raw, validate=True)
            else:
                if re.search(r"=(?![0-9A-Fa-f]{2})", payload):
                    raise ValueError
                decoded = quopri.decodestring(raw.replace(b"_", b" "))
            value = decoded.decode(charset, errors="strict")
        except (ValueError, LookupError, UnicodeError, binascii.Error):
            raise ValueError("Unsupported or malformed encoded subject word") from None
        if previous_word and literal and not literal.strip(" \t"):
            literal = ""
        pieces.extend((literal, value))
        previous_word = True
        end = word.end()
    tail = unfolded[end:]
    if "=?" in tail:
        raise ValueError("Unsupported or malformed encoded subject word")
    result = "".join(pieces) + tail
    _check_subject_text(result)
    return result.strip()


def normalize_address_parts(local_part: str, domain: str) -> tuple:
    """Return (unchanged extracted local part, lowercased extracted domain).

    Trim only outer space/tab. This is not an address/display-name parser or a
    deliverability check. Quoted local parts and non-ASCII/literal domains are
    outside this small helper's supported input; the caller must not guess.
    """
    _require_text(local_part)
    _require_text(domain)
    local_part, domain = local_part.strip(" \t"), domain.strip(" \t")
    if (not local_part or any(not part for part in local_part.split("."))
            or any(not c.isprintable() or c.isspace() or c in '()<>[]:;@,\\"'
                   for c in local_part)):
        raise ValueError("Unsupported or invalid extracted local part")
    labels = domain.split(".")
    if any(not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", label)
           for label in labels):
        raise ValueError("Unsupported or invalid extracted domain")
    return local_part, domain.lower()


def utf8_size(text: str) -> int:
    """Count exact UTF-8 bytes; do not serialize, normalize, split or persist."""
    _require_text(text)
    try:
        return len(text.encode("utf-8", errors="strict"))
    except UnicodeError:
        raise ValueError("Text cannot be encoded as strict UTF-8") from None
