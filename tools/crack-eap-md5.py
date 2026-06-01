#!/usr/bin/env python3

"""
crack-eap-md5.py

Small offline cracker for EAP-MD5 challenge/response exchanges.

EAP-MD5 computes:

    MD5(EAP_ID + password + challenge) = response

Use only on captures and networks you are authorized to assess.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def clean_hex(value: str) -> str:
    return value.replace(":", "").replace(" ", "").strip().lower()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Offline cracker for EAP-MD5 challenge/response material."
    )
    parser.add_argument(
        "eap_id",
        type=int,
        help="EAP identifier in decimal, for example 235",
    )
    parser.add_argument(
        "challenge",
        help="EAP-MD5 challenge in hex",
    )
    parser.add_argument(
        "response",
        help="EAP-MD5 response in hex",
    )
    parser.add_argument(
        "wordlist",
        type=Path,
        help="Password wordlist",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not 0 <= args.eap_id <= 255:
        print("[!] EAP ID must be between 0 and 255", file=sys.stderr)
        return 1

    if not args.wordlist.is_file():
        print(f"[!] Wordlist not found: {args.wordlist}", file=sys.stderr)
        return 1

    try:
        challenge = bytes.fromhex(clean_hex(args.challenge))
        target = clean_hex(args.response)
    except ValueError as exc:
        print(f"[!] Invalid hex input: {exc}", file=sys.stderr)
        return 1

    if len(challenge) == 0:
        print("[!] Empty challenge", file=sys.stderr)
        return 1

    if len(target) != 32:
        print("[!] EAP-MD5 response should be a 16-byte MD5 digest represented as 32 hex characters", file=sys.stderr)
        return 1

    attempts = 0

    with args.wordlist.open("rb") as handle:
        for line in handle:
            attempts += 1
            password = line.rstrip(b"\r\n")
            digest = hashlib.md5(bytes([args.eap_id]) + password + challenge).hexdigest()

            if digest == target:
                printable = password.decode(errors="ignore")
                print(f"[+] Password found: {printable}")
                print(f"[+] Attempts: {attempts}")
                return 0

    print("[-] Password not found")
    print(f"[-] Attempts: {attempts}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
