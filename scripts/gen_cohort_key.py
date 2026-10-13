#!/usr/bin/env python3
"""
Generate a cohort Ed25519 keypair.

Prints the base64 seed to store as the GitHub secret QW_COHORT_PRIVKEY, and the
base64 raw public key to publish once in the site (so the dossier can verify
badges). Run locally; never commit the seed.
"""
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sk = Ed25519PrivateKey.generate()
seed = sk.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption(),
)
pk = sk.public_key().public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw,
)
print("QW_COHORT_PRIVKEY (GitHub secret, keep private):")
print("  " + base64.b64encode(seed).decode())
print("\nPublic key (publish in the site for verification):")
print("  " + base64.b64encode(pk).decode())
