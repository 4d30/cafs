#!/usr/bin/env python

from vendor.json_canonicalization.python3.src.org.webpki.json import Canonicalize

def canonical_bytes(obj: dict) -> bytes:
    return Canonicalize.canonicalize(obj)
