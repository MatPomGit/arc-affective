#!/usr/bin/env python3
"""Validate the isolated public ARC Affective MkDocs source; no deployment."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_POLICY = "config/pages-policy.json"


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    try:
        cfg = json.loads((root / REQUIRED_POLICY).read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return ["PAGES_POLICY: missing or invalid JSON"]
    if cfg.get("schema_version") != 1 or type(cfg.get("schema_version")) is not int:
        errors.append("PAGES_POLICY: unsupported schema")
    if cfg.get("source_dir") != "pages" or cfg.get("output_dir") != "_public_site":
        errors.append("PAGES_POLICY: unexpected source or output")
    if cfg.get("publication_requires_owner_approval") is not True:
        errors.append("PAGES_POLICY: explicit approval is required")
    names = cfg.get("allowed_files")
    if not isinstance(names, list) or not names or len(names) != len(set(names)):
        return sorted(set(errors + ["PAGES_POLICY: invalid allowlist"]))
    if names != ["index.md"]:
        errors.append("PAGES_POLICY: public source expansion requires independent review")
    for name in names:
        rel = PurePosixPath(name)
        if (not isinstance(name, str) or rel.is_absolute() or len(rel.parts) != 1
                or name.startswith(".") or name in {".", ".."} or "\\" in name):
            errors.append("PAGES_POLICY: unsafe approved path")
    forbidden = cfg.get("prohibited_patterns")
    if not isinstance(forbidden, list) or not forbidden or not all(isinstance(x, str) and x for x in forbidden):
        return sorted(set(errors + ["PAGES_POLICY: prohibited patterns missing"]))
    folder = root / "pages"
    if not folder.is_dir() or folder.is_symlink():
        return sorted(set(errors + ["PAGES_SOURCE: missing or symlink directory"]))
    for path in sorted(folder.rglob("*")):
        relative = path.relative_to(folder).as_posix()
        if path.is_symlink():
            errors.append("PAGES_SYMLINK: " + relative)
        elif path.is_file():
            if relative not in names:
                errors.append("PAGES_UNAPPROVED: " + relative)
                continue
            try:
                data = path.read_bytes()
                if len(data) > cfg.get("max_file_bytes", 0):
                    errors.append("PAGES_TOO_LARGE: " + relative)
                contents = data.decode("utf-8")
                if any(re.search(p, contents, re.IGNORECASE) for p in forbidden):
                    errors.append("PAGES_INTERNAL_CONTENT: " + relative)
                if re.search(r"(?i)(?:dla\s+agenta\s*:|agent\s*:\s*(?:wykonaj|popraw|zrób)|uwagi?\s+redakcyjne|notatka\s+dla\s+autora|how to contribute)", contents):
                    errors.append("PAGES_EDITORIAL_CONTENT: " + relative)
                if re.search(r'(?i)(?:\.\./|file://|data:[^"\\s]*base64)', contents):
                    errors.append("PAGES_UNSAFE_REFERENCE: " + relative)
            except (OSError, UnicodeError, re.error, TypeError):
                errors.append("PAGES_UNREADABLE: " + relative)
        elif not path.is_dir():
            errors.append("PAGES_UNSUPPORTED: " + relative)
    for name in names:
        if not (folder / name).is_file():
            errors.append("PAGES_MISSING: " + name)
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = validate(args.root)
    for problem in errors:
        print("FAIL:", problem)
    print("ARC Affective public Pages:", "FAIL" if errors else "PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
