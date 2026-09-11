#!/usr/bin/env python3
"""Privately persist one exact host response received over a noncanonical PTY."""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from school_os.codex_bridge import MAX_DRIVE_FETCH_RESPONSE_BYTES  # noqa: E402


# This generic private writer may receive a Drive fetch response.  JsonlPeer
# applies the tighter operation-specific ceiling when it consumes the file.
MAX_RESPONSE_BYTES = MAX_DRIVE_FETCH_RESPONSE_BYTES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("response_path", type=Path)
    parser.add_argument("byte_count", type=int)
    args = parser.parse_args(argv)
    run_dir = args.run_dir.resolve(strict=True)
    response_path = args.response_path.resolve()
    if not run_dir.is_dir() or stat.S_IMODE(run_dir.stat().st_mode) != 0o700:
        parser.error("run_dir must be a mode-0700 directory")
    try:
        response_path.relative_to(run_dir)
    except ValueError:
        parser.error("response_path escapes run_dir")
    if response_path.parent != run_dir or not response_path.name.endswith(".response.json"):
        parser.error("response_path must be a direct response JSON child")
    if args.byte_count < 1 or args.byte_count > MAX_RESPONSE_BYTES:
        parser.error("byte_count is outside the bounded response range")
    remaining = args.byte_count
    chunks: list[bytes] = []
    while remaining:
        chunk = sys.stdin.buffer.read(remaining)
        if not chunk:
            parser.error("response payload was truncated")
        chunks.append(chunk)
        remaining -= len(chunk)
    payload = b"".join(chunks)
    descriptor = os.open(response_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)
    print("SCHOOL_OS_RESPONSE", response_path, len(payload), hashlib.sha256(payload).hexdigest(), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
