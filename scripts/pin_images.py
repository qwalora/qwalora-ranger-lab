#!/usr/bin/env python3
"""
Qwalora Ranger - image pinner.

Resolves every `name:tag@sha256:REPLACE_WITH_PINNED_DIGEST` placeholder in the
compose file and Dockerfiles to a real digest, so builds are reproducible and
`cosign verify` has something to check. Uses the local Docker CLI; run after
`./qrange up` once (or with network access to the registries).

Pinning by digest is part of the supply-chain story (board 4 / CVE-2024-3094):
you run exactly the bytes you reviewed, every time.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER = "REPLACE_WITH_PINNED_DIGEST"
FILES = [ROOT / "docker-compose.yml",
         ROOT / "lab/targets/web-api/Dockerfile",
         ROOT / "lab/attacker/Dockerfile"]

REF = re.compile(r"([a-z0-9][\w./-]*:[\w.-]+)@sha256:" + PLACEHOLDER)


def digest_for(ref):
    """Return name@sha256:... for a name:tag, via the Docker CLI."""
    for cmd in (
        ["docker", "buildx", "imagetools", "inspect", "--format",
         "{{.Manifest.Digest}}", ref],
        ["docker", "manifest", "inspect", "--verbose", ref],
    ):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
        if out.returncode != 0:
            continue
        m = re.search(r"sha256:[0-9a-f]{64}", out.stdout)
        if m:
            name = ref.split(":")[0] if "/" not in ref.split(":")[-1] else ref.rsplit(":", 1)[0]
            name = ref.rsplit(":", 1)[0]
            return f"{name}@{m.group(0)}"
    return None


def main():
    changed = 0
    missing = []
    for path in FILES:
        if not path.exists():
            continue
        text = path.read_text()
        for ref in sorted(set(m.group(1) for m in REF.finditer(text))):
            pinned = digest_for(ref)
            if not pinned:
                missing.append(ref)
                continue
            text = text.replace(f"{ref}@sha256:{PLACEHOLDER}", pinned)
            changed += 1
            print(f"  pinned {ref} -> {pinned.split('@')[1][:19]}...")
        path.write_text(text)
    if missing:
        print("\n  could not resolve (pull them first, or check connectivity):",
              file=sys.stderr)
        for r in sorted(set(missing)):
            print(f"    - {r}", file=sys.stderr)
        return 1 if changed == 0 else 0
    if changed == 0:
        print("  nothing to pin (already pinned, or no placeholders found).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
