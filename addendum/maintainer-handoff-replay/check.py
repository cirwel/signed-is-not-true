"""Decide a handoff from the requested checks and authoritative receipts."""

import argparse
import json
from collections import Counter
from pathlib import Path


def decide(request, receipts):
    """Require exactly one passing result for each check in the requested scope."""
    scope = request["scope"]
    checks = request["checks"]
    if not isinstance(scope, str) or not scope:
        raise ValueError("The request needs a nonempty scope.")
    if not isinstance(checks, list) or not checks or not all(isinstance(x, str) and x for x in checks):
        raise ValueError("The request needs a nonempty list of check names.")
    required = set(checks)
    if len(required) != len(checks):
        raise ValueError("Required check names must be unique.")
    if not isinstance(receipts, list):
        raise ValueError("Receipts must be a list.")
    local = [r for r in receipts if r["scope"] == scope]
    counts = Counter(r["name"] for r in local)
    problems = {
        "missing": sorted(required - counts.keys()),
        "failed_or_pending": sorted({r["name"] for r in local if r["outcome"] != "success"}),
        "duplicate": sorted(name for name, count in counts.items() if count > 1),
        "unexpected": sorted(counts.keys() - required),
        "wrong_scope": sorted({r["name"] for r in receipts if r["scope"] != scope}),
    }
    return {"decision": "hold" if any(problems.values()) else "accept", **problems}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("receipts", type=Path)
    args = parser.parse_args()
    try:
        result = decide(json.loads(args.request.read_text()), json.loads(args.receipts.read_text()))
    except (KeyError, TypeError, ValueError, OSError) as exc:
        parser.exit(2, f"Invalid handoff input: {exc}\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["decision"] == "accept" else 1)


if __name__ == "__main__":
    main()
