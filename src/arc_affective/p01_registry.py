"""P01 local-only data provenance gate. No EEG signal decoding."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re

SHA = re.compile(r"^[0-9a-fA-F]{64}$")
ELECTRODE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
REQUIRED = ("dataset", "version", "license", "approved_use", "files",
            "sampling_hz", "reference", "electrodes", "rating_scale")


def validate_manifest(manifest: dict, root: Path, verify_hashes: bool = False) -> dict:
    """Validate metadata, rights declaration and optional local SHA256 checks."""
    if not isinstance(manifest, dict):
        raise ValueError("Manifest must be a JSON object")
    for key in REQUIRED:
        if key not in manifest:
            raise ValueError(f"Missing required field: {key}")
    for key in ("dataset", "version", "reference", "rating_scale"):
        if not isinstance(manifest[key], str) or not manifest[key].strip():
            raise ValueError(f"Invalid {key}")
    if manifest["license"] not in ("CC-BY-4.0", "CC0-1.0", "approved-restricted"):
        raise ValueError("Unreviewed license")
    if manifest["approved_use"] is not True:
        raise ValueError("Research use has not been approved")
    hz = manifest["sampling_hz"]
    if type(hz) not in (int, float) or not math.isfinite(hz) or not 0 < hz <= 100000:
        raise ValueError("Invalid sample frequency")
    electrodes = manifest["electrodes"]
    if (not isinstance(electrodes, list) or not electrodes or
            any(not isinstance(x, str) or not ELECTRODE.fullmatch(x) for x in electrodes) or
            len(electrodes) != len(set(electrodes))):
        raise ValueError("Empty, duplicate or invalid electrodes")
    files = manifest["files"]
    if not isinstance(files, list) or not files:
        raise ValueError("Missing file inventory")
    root = root.resolve(strict=True)
    seen = set()
    for item in files:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise ValueError("Invalid file entry")
        name, sha = item["path"], item["sha256"]
        if not isinstance(name, str) or not name or not isinstance(sha, str) or not SHA.fullmatch(sha):
            raise ValueError("Invalid path/checksum")
        path = Path(name)
        if path.is_absolute() or any(part in (".", "..") for part in path.parts):
            raise ValueError("Unsafe path")
        if name in seen:
            raise ValueError("Repeated file path")
        seen.add(name)
        if verify_hashes:
            absolute = (root / path).resolve(strict=True)
            if not absolute.is_relative_to(root) or not absolute.is_file():
                raise ValueError("File escapes the local dataset root")
            digest = hashlib.sha256()
            with absolute.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1048576), b""):
                    digest.update(chunk)
            if digest.hexdigest() != sha.lower():
                raise ValueError("Checksum mismatch: " + name)
    return {"schema_version": 1, "dataset": manifest["dataset"],
            "version": manifest["version"], "status": "metadata_validated",
            "files_checked": len(files) if verify_hashes else 0,
            "hashes_verified": bool(verify_hashes),
            "montage_equivalence_established": False,
            "cross_corpus_eligibility": "unassessed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--verify-hashes", action="store_true")
    args = parser.parse_args()
    print(json.dumps(validate_manifest(
        json.loads(args.manifest.read_text(encoding="utf-8")),
        args.root, args.verify_hashes), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
