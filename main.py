#!/usr/bin/env python3
"""Entrypoint for the 25 Nov 2026 news-image entry.

Copies entry.png to /output/entry.png, then validates the copy:
PNG magic bytes, CRC of every chunk, size at most 1 MiB, and exact
1024x1024 dimensions. Standard library only; the copy is byte-for-byte
identical to the source, so repeated runs are deterministic.
"""
import os
import shutil
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
OUT_DIR = "/output"
DEST = os.path.join(OUT_DIR, "entry.png")
LIMIT = 1024 * 1024
EXPECT = (1024, 1024)
MAGIC = b"\x89PNG\r\n\x1a\n"


def die(reason):
    sys.stderr.write("FAIL: %s\n" % reason)
    raise SystemExit(1)


def iter_chunks(blob):
    """Yield (kind, payload) for each PNG chunk in blob."""
    cursor = 8
    while cursor < len(blob):
        if cursor + 8 > len(blob):
            die("chunk header cut off at byte %d" % cursor)
        size, kind = struct.unpack_from(">I4s", blob, cursor)
        start = cursor + 8
        stop = start + size
        if stop + 4 > len(blob):
            die("chunk %s runs past end of file" % kind.decode("latin-1"))
        stored, = struct.unpack_from(">I", blob, stop)
        actual = zlib.crc32(kind + blob[start:stop]) & 0xFFFFFFFF
        if stored != actual:
            die("CRC mismatch in %s chunk" % kind.decode("latin-1"))
        yield kind, blob[start:stop]
        cursor = stop + 4
        if kind == b"IEND":
            if cursor != len(blob):
                die("bytes after the IEND chunk")
            return
    die("no IEND chunk found")


def validate_png(path):
    with open(path, "rb") as handle:
        blob = handle.read()
    if len(blob) > LIMIT:
        die("file is %d bytes, above the 1 MiB limit" % len(blob))
    if blob[:8] != MAGIC:
        die("not a PNG file (bad magic bytes)")
    dims = None
    for kind, payload in iter_chunks(blob):
        if kind == b"IHDR":
            dims = struct.unpack_from(">II", payload, 0)
    if dims != EXPECT:
        die("dimensions are %sx%s, expected 1024x1024" % (dims or (None, None)))
    return len(blob)


def main():
    if not os.path.isfile(SOURCE):
        die("entry.png is missing next to main.py")
    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(SOURCE, DEST)
    total = validate_png(DEST)
    print("OK: /output/entry.png 1024x1024 %d bytes" % total)


if __name__ == "__main__":
    main()
