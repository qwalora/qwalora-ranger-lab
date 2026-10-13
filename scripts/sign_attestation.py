#!/usr/bin/env python3
"""
Qwalora Ranger - cohort attestation signer.

Re-measures every board from scratch (not trusting any committed report), builds
a canonical record, and signs it with the cohort's Ed25519 key. The signature is
the one the public dossier verifies in the browser (WebCrypto Ed25519), so a
badge cannot be forged without the program's private key.

The record is signed over the RFC 8785-ish canonical form: JSON with sorted keys
and no whitespace, UTF-8 encoded. The site imports the raw 32-byte public key and
verifies the 64-byte signature over those exact bytes.

Env:
  QW_COHORT_PRIVKEY  base64 of the 32-byte Ed25519 seed (GitHub secret)
  QW_CANDIDATE       candidate handle (defaults to the repo owner)
Writes: evidence/attestation.json
"""
import base64
import importlib
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def measure():
    progress = importlib.import_module("progress")
    rows = progress.grade_all(ROOT)
    return rows


def main():
    seed_b64 = os.environ.get("QW_COHORT_PRIVKEY")
    if not seed_b64:
        print("QW_COHORT_PRIVKEY not set; refusing to produce an unsigned badge.",
              file=sys.stderr)
        return 2
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization

    seed = base64.b64decode(seed_b64)
    sk = Ed25519PrivateKey.from_private_bytes(seed)
    pk_raw = sk.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    rows = measure()
    done = [r for r in rows if r["done"]]
    record = {
        "schema": "qwalora.ranger.attestation/v1",
        "candidate": os.environ.get("QW_CANDIDATE",
                                    os.environ.get("GITHUB_REPOSITORY_OWNER", "unknown")),
        "repo": os.environ.get("GITHUB_REPOSITORY", "local"),
        "commit": os.environ.get("GITHUB_SHA", "local")[:12],
        "boards_total": len(rows),
        "boards_complete": len(done),
        "boards": [{"board": r["board"], "attack": r["attack"],
                    "score": r["score"], "done": r["done"]} for r in rows],
        "issued": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    msg = canonical(record)
    sig = sk.sign(msg)

    attestation = {
        "record": record,
        "signature": base64.b64encode(sig).decode(),
        "algorithm": "Ed25519",
        "public_key": base64.b64encode(pk_raw).decode(),
        "canonicalization": "json-sorted-compact-utf8",
    }
    out = ROOT / "evidence" / "attestation.json"
    out.write_text(json.dumps(attestation, indent=2) + "\n")
    print(f"signed: {len(done)}/{len(rows)} boards -> evidence/attestation.json")
    # also drop the public key so the program can publish it once
    (ROOT / "cohort-pubkey.b64").write_text(base64.b64encode(pk_raw).decode() + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
