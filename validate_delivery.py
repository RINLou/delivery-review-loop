#!/usr/bin/env python3
"""
validate_delivery.py — mechanical gate for the delivery-review-loop self-check block.

Parses a delivery artifact (markdown) and exits NON-ZERO if the mandatory
self-check block is missing its three required elements:
  ① contract issued / why skipped
  ② evidence highlights
  ③ reviewer conclusion

This is how the loop turns "must include a self-check block" from a
disciplinary rule into a mechanical one (for file/PR deliveries).

Usage:
    python validate_delivery.py DELIVERY.md
    cat DELIVERY.md | python validate_delivery.py -
    python validate_delivery.py DELIVERY.md --strict   # also fail if no AC evidence matrix

Exit codes:
    0  self-check block present and complete
    1  self-check block missing or incomplete
    2  usage / file error

Stdlib only — no third-party dependencies.
"""
import argparse
import re
import sys

# A self-check section header, framework-agnostic (zh + en).
SELFCHECK_HEADER = re.compile(
    r"^#{1,6}\s*.*?(self[-_ ]?check|自检|交付自检|闭环自检|delivery check)\b",
    re.IGNORECASE,
)

# The three required elements — each detected by at least one zh/en token.
REQUIRED = [
    ("contract", re.compile(r"合同|契约|contract", re.IGNORECASE)),
    ("evidence", re.compile(r"证据|evidence", re.IGNORECASE)),
    ("reviewer", re.compile(r"审查|复核|挑刺|reviewer|review", re.IGNORECASE)),
]

# Optional but encouraged: an AC evidence matrix table.
AC_MATRIX = re.compile(r"AC\s*#|acceptance[- ]criteria evidence|证据矩阵", re.IGNORECASE)


def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        print(f"[validate_delivery] cannot read {path!r}: {e}", file=sys.stderr)
        sys.exit(2)


def extract_selfcheck_section(text: str) -> str:
    """Return the text of the self-check section (header line up to next header or EOF)."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if SELFCHECK_HEADER.search(line):
            start = i
            break
    if start is None:
        return ""
    # Section body runs until the next markdown header of equal/higher level or EOF.
    body = [lines[start]]
    for line in lines[start + 1 :]:
        if re.match(r"^#{1,6}\s", line):
            break
        body.append(line)
    return "\n".join(body)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a delivery self-check block.")
    ap.add_argument("path", help="delivery markdown file, or '-' for stdin")
    ap.add_argument("--strict", action="store_true",
                    help="also fail if no acceptance-criteria evidence matrix is present")
    args = ap.parse_args()

    text = read_text(args.path)
    section = extract_selfcheck_section(text)

    if not section:
        print("[FAIL] no self-check block found (header with 'self-check' / '自检' / '交付自检').")
        return 1

    missing = [name for name, pat in REQUIRED if not pat.search(section)]
    if missing:
        print(f"[FAIL] self-check block missing required element(s): {', '.join(missing)}")
        print("       required: ① contract  ② evidence  ③ reviewer conclusion")
        return 1

    warnings = []
    if args.strict and not AC_MATRIX.search(text):
        warnings.append("no acceptance-criteria evidence matrix (AC# / 证据矩阵) found")

    print("[OK] self-check block present and complete (contract / evidence / reviewer).")
    if warnings:
        print("[WARN] " + "; ".join(warnings))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
