"""Refresh public GitHub receipts for the frozen PyPA sample. Requires PyYAML and curl."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from hashlib import sha256
import itertools
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlencode

import yaml


ROOT = Path(__file__).resolve().parent
REPO = "pypa/packaging"
PATH = ".github/workflows/test.yml"
API = f"https://api.github.com/repos/{REPO}"
WHEN = "2026-11-19T00:00:00Z"
NAME_VAR = re.compile(r"\$\{\{\s*matrix\.([A-Za-z_][A-Za-z_0-9]*)\s*\}\}")


class Unsupported(ValueError):
    """A predeclared eligibility requirement was not met."""


def fetch(url):
    return subprocess.check_output([
        "curl", "--fail", "--silent", "--show-error", "--location", "--retry", "2",
        "--max-time", "35", "--user-agent", "read-only-maintainer-replay", url,
    ])


def normalize_time(stamp):
    if not stamp:
        raise Unsupported("a completed job lacks its end time")
    return datetime.fromisoformat(stamp).isoformat(timespec="seconds")


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def matrix_rows(matrix):
    axes = {k: v for k, v in matrix.items() if k not in {"include", "exclude"}}
    if not all(isinstance(v, list) for v in axes.values()):
        raise Unsupported("a matrix axis is dynamic")
    base = [dict(zip(axes, values)) for values in itertools.product(*axes.values())] if axes else []
    raw_rows = [r for r in base if not any(
        all(r.get(k) == v for k, v in rule.items()) for rule in matrix.get("exclude", [])
    )]
    rows = [dict(r) for r in raw_rows]
    additions = []
    for item in matrix.get("include", []):
        compatible = [i for i, row in enumerate(raw_rows)
                      if all(k not in axes or row[k] == v for k, v in item.items())]
        if compatible:
            for i in compatible:
                rows[i].update(item)
        else:
            additions.append(item)
    return rows + additions


def required_checks(definition):
    jobs = yaml.safe_load(definition)["jobs"]
    gate = jobs.get("pass", {})
    dependencies = gate.get("needs")
    if gate.get("name") != "All pass" or not isinstance(dependencies, list) or gate.get("if") != "always()":
        raise Unsupported("no supported unconditional All pass aggregator")
    steps = gate.get("steps", [])
    if len(steps) != 1 or not steps[0].get("uses", "").startswith("re-actors/alls-green@"):
        raise Unsupported("unsupported aggregate implementation")
    if steps[0].get("with") != {"jobs": "${{ toJSON(needs) }}"}:
        raise Unsupported("aggregate permits exceptions or has a different input")
    required = []
    unrelated = []
    for identifier, job in jobs.items():
        if identifier == "pass":
            continue
        needed = identifier in dependencies
        if needed and ("if" in job or job.get("continue-on-error")):
            raise Unsupported("conditional or optional prerequisite needs another adapter")
        name = job.get("name", identifier)
        matrix = job.get("strategy", {}).get("matrix")
        rows = [{}] if matrix is None else matrix_rows(matrix)
        for row in rows:
            try:
                expanded = NAME_VAR.sub(lambda m: str(row[m.group(1)]), name)
            except KeyError as exc:
                raise Unsupported("name needs an unbound matrix variable") from exc
            if "${{" in expanded:
                raise Unsupported("job name uses an unsupported expression")
            (required if needed else unrelated).append(expanded)
    names = required + unrelated + ["All pass"]
    if set(dependencies) - jobs.keys() or len(required) < 2 or len(set(names)) != len(names):
        raise Unsupported("insufficient or ambiguous names in the configured jobs")
    return sorted(required), set(unrelated)


def attempt_jobs(run_id):
    base = f"{API}/actions/runs/{run_id}/attempts/1/jobs"
    page = 1
    records = []
    while True:
        data = json.loads(fetch(f"{base}?per_page=100&page={page}"))
        records.extend(data["jobs"])
        if len(records) >= data["total_count"]:
            return records
        if not data["jobs"]:
            raise RuntimeError(f"Incomplete jobs API response for run {run_id}")
        page += 1


def inspect_run(row):
    run_id, commit = row["id"], row["head_sha"]
    try:
        url = f"https://raw.githubusercontent.com/{REPO}/{commit}/{PATH}"
        definition = fetch(url)
        required, unrelated = required_checks(definition)
        jobs = attempt_jobs(run_id)
        aggregates = [j for j in jobs if j["name"] == "All pass"]
        if len(aggregates) != 1 or aggregates[0]["conclusion"] not in {"success", "failure"}:
            raise Unsupported("aggregate absent or without a success/failure verdict")
        aggregate = aggregates[0]
        end = normalize_time(aggregate["completed_at"])
        records = []
        seen_ids = set()
        for job in jobs:
            if job["id"] in seen_ids or job["run_id"] != run_id or job["head_sha"] != commit or job.get("run_attempt", 1) != 1:
                raise Unsupported("ambiguous job provenance")
            seen_ids.add(job["id"])
            if job["id"] == aggregate["id"] or job["name"] in unrelated:
                continue
            if job["name"] not in required:
                raise Unsupported("unmapped GitHub job name: " + job["name"])
            if job["status"] != "completed" or not job["conclusion"]:
                raise Unsupported("prerequisite timing or conclusion missing")
            records.append({
                "id": job["id"], "name": job["name"], "outcome": job["conclusion"],
                "finished": normalize_time(job["completed_at"]),
            })
        if len({r["name"] for r in records}) < 2 or max(r["finished"] for r in records) > end:
            raise Unsupported("incomplete or inconsistent aggregate timing")
        wf_hash = sha256(definition).hexdigest()
        return {
            "run": run_id, "commit": commit, "created": row["created_at"], "attempt": 1,
            "repository": REPO, "url": row["html_url"], "workflow_url": url, "workflow_sha256": wf_hash,
            "required": required, "unrelated_names": sorted(unrelated),
            "jobs": sorted(records, key=lambda j: (j["finished"], j["name"], j["id"])),
            "aggregate": {"id": aggregate["id"], "outcome": aggregate["conclusion"], "finished": end},
        }, definition, None
    except Unsupported as exc:
        return None, None, str(exc)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame", type=Path, help="use an already downloaded GitHub run-list response")
    parser.add_argument("--failures", action="store_true", help="collect the separately frozen failure supplement")
    args = parser.parse_args()
    protocol = "FAILURE-SUPPLEMENT" if args.failures else "PROTOCOL"
    suffix = "-failures" if args.failures else ""
    target = 6 if args.failures else 16
    frame_url = f"{API}/actions/workflows/test.yml/runs?" + urlencode({
        "event": "push", "branch": "main", "created": "<" + WHEN,
        "status": "failure" if args.failures else "completed", "per_page": 30 if args.failures else 50,
    })
    digest = (ROOT / (protocol + ".sha256")).read_text().split()[0]
    if sha256((ROOT / (protocol + ".md")).read_bytes()).hexdigest() != digest:
        raise RuntimeError("Protocol digest mismatch")
    frame = json.loads(args.frame.read_bytes() if args.frame else fetch(frame_url))["workflow_runs"]
    ordered = sorted(frame, key=lambda x: (x["created_at"], x["id"]), reverse=True)
    if any(x["created_at"] >= WHEN or x["head_branch"] != "main" or x["event"] != "push" for x in ordered):
        raise RuntimeError("GitHub frame falls outside the protocol")
    if len({x["id"] for x in ordered}) != len(ordered):
        raise RuntimeError("Duplicate IDs in the frame")
    data = ROOT / "data"
    (data / "workflows").mkdir(parents=True, exist_ok=True)
    frame_record = [{"run": x["id"], "created": x["created_at"], "commit": x["head_sha"]} for x in ordered]
    write_json(data / ("frame" + suffix + ".json"), {"url": frame_url, "candidates": frame_record})
    selected = []
    skipped = []
    start = 0
    with ThreadPoolExecutor(max_workers=4) as pool:
        while start < len(ordered) and len(selected) < target:
            group = ordered[start:start + min(4, target - len(selected))]
            for row, (run, definition, reason) in zip(group, pool.map(inspect_run, group)):
                if not reason and args.failures and run["aggregate"]["outcome"] != "failure":
                    reason = "first-attempt native All pass job did not fail"
                if reason:
                    skipped.append({"run": row["id"], "reason": reason})
                else:
                    selected.append(run)
                    (data / "workflows" / (run["workflow_sha256"] + ".yml")).write_bytes(definition)
            start += len(group)
    write_json(data / ("runs" + suffix + ".json"), {"protocol_sha256": digest, "runs": selected, "skipped": skipped})
    print(f"Selected {len(selected)} attempts. Skipped {len(skipped)}. Frame size {len(ordered)}.")
    if not selected:
        raise SystemExit("No eligible attempts. See data/runs.json.")


if __name__ == "__main__":
    main()
