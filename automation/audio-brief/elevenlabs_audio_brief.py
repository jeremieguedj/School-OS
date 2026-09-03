#!/usr/bin/env python3
"""Create a verified ElevenLabs MP3 from a Drive-derived School-OS manifest."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from typing import Any


API_URL = "https://api.elevenlabs.io/v1/text-to-dialogue?output_format=mp3_44100_128"
MAX_TEXT_CHARACTERS = 2000
# These two public premade voices were verified by a successful
# /v1/text-to-dialogue call with the Keychain-backed account on 2026-09-02.
# Voice IDs are still provider/account configuration: validate against
# /v1/voices before a paid synthesis request, and replace this map when needed.
VOICES = {
    "narrator": "CwhRBWXzGAHq8TQ4Fs17",  # Roger
    "voice_a": "CwhRBWXzGAHq8TQ4Fs17",  # Roger
    "voice_b": "EXAVITQu4vr4xnSDxMaL",  # Sarah
}


class BriefError(RuntimeError):
    """An expected, safe-to-report generation failure."""


def fnv1a_u32(value: str) -> int:
    result = 0x811C9DC5
    for byte in value.encode("utf-8"):
        result ^= byte
        result = (result * 0x01000193) & 0xFFFFFFFF
    return result


def normalize_spoken_text(value: str) -> str:
    return value.replace("[", "(").replace("]", ")").strip()


def tag_for(record: dict[str, Any]) -> str:
    section = record["section"]
    if section == "news":
        return "[warmly]"
    if section == "guideline":
        return "[clear, calm]"
    if section == "action":
        status = record.get("due_status", "normal")
        if status not in {"normal", "due_today", "overdue", "resolved"}:
            raise BriefError(f"unsupported action due_status: {status}")
        if status in {"due_today", "overdue"}:
            return "[gently, urgent]"
        return "[warmly]" if status == "resolved" else "[clear, matter-of-fact]"
    raise BriefError(f"unsupported section: {section}")


def turn_for(record: dict[str, Any]) -> dict[str, str]:
    voice_role = record["voice_role"]
    if voice_role not in VOICES:
        raise BriefError(f"unsupported voice_role: {voice_role}")
    prefixes = {"news": "News", "guideline": "School guideline", "action": "Action update"}
    return {
        "voice_id": VOICES[voice_role],
        "text": f"{tag_for(record)} {prefixes[record['section']]}: {normalize_spoken_text(record['spoken_text'])}",
    }


def require_string(record: dict[str, Any], field: str) -> None:
    if not isinstance(record.get(field), str) or not record[field].strip():
        raise BriefError(f"manifest record has no usable {field}")


def build_inputs(manifest: dict[str, Any]) -> tuple[list[dict[str, str]], int]:
    try:
        run_date = dt.date.fromisoformat(manifest.get("run_date"))
    except (TypeError, ValueError) as error:
        raise BriefError("manifest run_date must be YYYY-MM-DD") from error
    records = manifest.get("records")
    if not isinstance(records, list):
        raise BriefError("manifest records must be a list")
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise BriefError("each manifest record must be an object")
        for field in ("section", "voice_role", "spoken_text", "source_tid", "fact_or_row_id"):
            require_string(record, field)
        key = f"{record['section']}:{record['fact_or_row_id']}"
        if key not in seen:
            seen.add(key)
            unique.append(record)
    opening = {"voice_id": VOICES["narrator"], "text": f"[warmly] School audio brief for {run_date.strftime('%B %-d, %Y')}."}
    closing = {"voice_id": VOICES["narrator"], "text": "[warmly] End of today's new school information."}
    accepted = [opening]
    for position, record in enumerate(unique):
        candidate = turn_for(record)
        if sum(len(turn["text"]) for turn in accepted + [candidate, closing]) <= MAX_TEXT_CHARACTERS:
            accepted.append(candidate)
        else:
            if len(accepted) == 1:
                raise BriefError("first complete record exceeds the 2,000-character limit")
            return accepted + [closing], len(unique) - position
    if len(accepted) == 1:
        return [], 0
    return accepted + [closing], 0


def keychain_secret(service: str, account: str) -> str:
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
            capture_output=True, check=True, text=True,
        )
    except FileNotFoundError as error:
        raise BriefError("macOS Keychain command is unavailable") from error
    except subprocess.CalledProcessError as error:
        raise BriefError("ElevenLabs secret is unavailable in macOS Keychain") from error
    secret = result.stdout.strip()
    if not secret:
        raise BriefError("ElevenLabs secret is empty")
    return secret


def is_mp3(content: bytes) -> bool:
    return content.startswith(b"ID3") or (len(content) >= 2 and content[0] == 0xFF and content[1] & 0xE0 == 0xE0)


def validate_voice_ids(inputs: list[dict[str, str]], api_key: str) -> None:
    """Fail before synthesis when the configured voices are not visible to this key."""
    request = urllib.request.Request(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": api_key, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, UnicodeDecodeError) as error:
        raise BriefError("ElevenLabs voice catalog could not be read") from error
    available = {voice.get("voice_id") for voice in payload.get("voices", []) if isinstance(voice, dict)}
    unavailable = sorted({turn["voice_id"] for turn in inputs} - available)
    if unavailable:
        raise BriefError(
            "configured voice IDs are unavailable to this ElevenLabs key; "
            "refresh the mapping from GET /v1/voices"
        )


def request_audio(inputs: list[dict[str, str]], run_date: str, api_key: str) -> bytes:
    serialized = json.dumps(inputs, ensure_ascii=False, separators=(",", ":"))
    payload = {
        "model_id": "eleven_v3",
        "seed": fnv1a_u32(f"{run_date}\n{serialized}"),
        "apply_text_normalization": "off",
        "inputs": inputs,
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            content_type, body = response.headers.get_content_type(), response.read()
    except urllib.error.HTTPError as error:
        # Keep the actionable server reason, but never expose request headers or the API key.
        try:
            detail = json.loads(error.read().decode("utf-8", errors="replace"))
            message = detail.get("detail", {}).get("message") or detail.get("detail", {}).get("status")
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            message = None
        suffix = f": {message}" if message else ""
        raise BriefError(f"ElevenLabs request failed with HTTP {error.code}{suffix}") from error
    except urllib.error.URLError as error:
        raise BriefError("ElevenLabs request could not reach the API") from error
    if content_type != "audio/mpeg":
        raise BriefError("ElevenLabs response was not audio/mpeg")
    if not is_mp3(body):
        raise BriefError("ElevenLabs response did not have an MP3 signature")
    return body


def write_fresh_mp3(output_dir: Path, run_date: str, body: bytes) -> tuple[Path, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"sha-daily-audio-{run_date}.mp3"
    if target.exists():
        raise BriefError(f"refusing to overwrite an existing audio file: {target}")
    with tempfile.NamedTemporaryFile(dir=output_dir, prefix=".audio-", suffix=".tmp", delete=False) as temp:
        temp.write(body)
        temporary = Path(temp.name)
    try:
        saved = temporary.read_bytes()
        if not saved or not is_mp3(saved):
            raise BriefError("temporary audio file failed MP3 verification")
        digest = hashlib.sha256(saved).hexdigest()
        temporary.replace(target)
        return target, digest
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keychain-service", default="School-OS.ElevenLabs.APIKey")
    parser.add_argument("--keychain-account", default=os.environ.get("USER", ""))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        inputs, omitted = build_inputs(manifest)
        if not inputs:
            print("audio skipped: no new information in this run")
            return 0
        if args.dry_run:
            print(json.dumps({"inputs": inputs, "omitted_records": omitted}, ensure_ascii=False, indent=2))
            return 0
        if not args.keychain_account:
            raise BriefError("keychain account is required; set --keychain-account")
        key = keychain_secret(args.keychain_service, args.keychain_account)
        validate_voice_ids(inputs, key)
        body = request_audio(inputs, manifest["run_date"], key)
        output, digest = write_fresh_mp3(args.output_dir, manifest["run_date"], body)
        status = f"audio truncated: {omitted} manifest records omitted" if omitted else "audio attached-ready"
        print(f"{status}: {output.name}")
        print(f"sha256: {digest}")
        return 0
    except (BriefError, OSError, json.JSONDecodeError) as error:
        print(f"audio failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
