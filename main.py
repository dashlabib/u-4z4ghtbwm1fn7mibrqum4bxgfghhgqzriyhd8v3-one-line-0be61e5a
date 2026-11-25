#!/usr/bin/env python3
"""Publish the one-line entry to /output/entry.txt.

Reads entry.txt beside this script as raw bytes, validates the
competition gate (1-140 characters, non-blank, single line, no control
characters), writes the bytes unchanged to /output/entry.txt, then
re-reads the published file and refuses on any byte mismatch.
Standard library only; deterministic.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENTRY = HERE / "entry.txt"
OUTPUT = Path("/output/entry.txt")

MAX_CHARS = 140


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main():
    try:
        raw = ENTRY.read_bytes()
    except OSError as exc:
        fail(f"cannot read {ENTRY}: {exc}")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(f"entry.txt is not valid UTF-8: {exc}")

    # A single trailing newline is the file's line ending, not content.
    body = text[:-1] if text.endswith("\n") else text

    if text.startswith("\ufeff"):
        fail("entry.txt starts with a UTF-8 byte-order mark")

    if not (1 <= len(text) <= MAX_CHARS):
        fail(f"entry is {len(text)} characters, must be 1-{MAX_CHARS}")

    if not body.strip():
        fail("entry is blank")

    if "\n" in body or "\r" in body:
        fail("entry must be a single line")

    if any(ord(ch) < 0x20 and ch not in ("\t",) for ch in body):
        fail("entry contains a control character")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        OUTPUT.write_bytes(raw)
    except OSError as exc:
        fail(f"cannot write {OUTPUT}: {exc}")

    try:
        published = OUTPUT.read_bytes()
    except OSError as exc:
        fail(f"cannot re-read {OUTPUT}: {exc}")

    if published != raw:
        fail("published bytes differ from entry.txt")

    print(f"published {len(text)} characters to {OUTPUT}")


if __name__ == "__main__":
    main()
