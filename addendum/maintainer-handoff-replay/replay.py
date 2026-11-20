"""Replay the frozen maintainer checks offline using Python's standard library."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from check import decide


ROOT = Path(__file__).resolve().parent
POLICIES = ("reported_success", "count_and_run", "required_checks")


def scoped_request(run):
    scope = f"{run['repository']}:{run['run']}:{run['attempt']}:{run['commit']}"
    return {"scope": scope, "checks": run["required"]}


def receipts(jobs, scope):
    return [{"scope": scope, "name": row["name"], "outcome": row["outcome"],
             "source_job_id": row["id"]} for row in jobs]


def make_packets(runs):
    packets = []
    by_time = sorted(runs, key=lambda r: (r["created"], r["run"]))
    for i, run in enumerate(by_time):
        request = scoped_request(run)
        last_time = max(j["finished"] for j in run["jobs"])
        early = [j for j in run["jobs"] if j["finished"] < last_time]
        final = [j for j in run["jobs"] if j["finished"] <= run["aggregate"]["finished"]]
        primary = [
            ("early", early, "hold"),
            ("terminal", final, "accept" if run["aggregate"]["outcome"] == "success" else "hold"),
        ]
        for kind, jobs, reference in primary:
            packets.append({
                "run": run["run"], "kind": kind, "request": request,
                "receipts": receipts(jobs, request["scope"]), "reference": reference,
            })

        if run["aggregate"]["outcome"] != "success":
            continue
        # Resolve ties in a documented direction, independent of the result of any policy.
        last_job = min((j for j in final if j["finished"] == last_time), key=lambda j: j["name"])
        for prior in reversed(by_time[:i]):
            if prior["aggregate"]["outcome"] != "success" or prior["commit"] == run["commit"]:
                continue
            match = [j for j in prior["jobs"] if j["name"] == last_job["name"] and j["outcome"] == "success"]
            if len(match) != 1:
                continue
            current = receipts([j for j in final if j["id"] != last_job["id"]], request["scope"])
            foreign = receipts(match, scoped_request(prior)["scope"])
            packets.append({
                "run": run["run"], "kind": "stale_control", "request": request,
                "receipts": current + foreign, "reference": "hold",
            })
            break
    return packets


def decisions(request, observed):
    successful = bool(observed) and all(r["outcome"] == "success" for r in observed)
    unique_names = {r["name"] for r in observed}
    counted = (successful and len(observed) == len(unique_names) == len(request["checks"])
               and all(r["scope"] == request["scope"] for r in observed))
    return {
        "reported_success": "accept" if successful else "hold",
        "count_and_run": "accept" if counted else "hold",
        "required_checks": decide(request, observed)["decision"],
    }


PRIMARY_GROUPS = {
    "early": {"early"}, "terminal": {"terminal"},
    "primary": {"early", "terminal"}, "stale_control": {"stale_control"},
}
FAILURE_GROUPS = {"terminal_failure": {"terminal_failure"}, "omitted_failure": {"omitted_failure"}}


def failure_packets(runs):
    packets = []
    for run in runs:
        request = scoped_request(run)
        if run["aggregate"]["outcome"] != "failure":
            raise ValueError("Unexpected native verdict in the failure supplement")
        observed = receipts(run["jobs"], request["scope"])
        passing = [r for r in observed if r["outcome"] == "success"]
        kinds = {"terminal_failure": observed}
        if len(passing) < len(observed):
            kinds["omitted_failure"] = passing
        for kind, receipt_list in kinds.items():
            packets.append({
                "kind": kind, "run": run["run"], "request": request,
                "receipts": receipt_list, "reference": "hold",
            })
    return packets


def score(packets, groups):
    totals = {}
    for label, kinds in groups.items():
        subset = [p for p in packets if p["kind"] in kinds]
        reference = Counter(p["reference"] for p in subset)
        rows = {p: {"false_accept": 0, "false_hold": 0} for p in POLICIES}
        for packet in subset:
            answers = decisions(packet["request"], packet["receipts"])
            for policy, choice in answers.items():
                if choice != packet["reference"]:
                    field = "false_accept" if choice == "accept" else "false_hold"
                    rows[policy][field] += 1
        totals[label] = {
            "reference_hold": reference["hold"], "reference_accept": reference["accept"],
            "policies": rows,
        }
    return totals


def load_data(failures):
    protocol = "FAILURE-SUPPLEMENT" if failures else "PROTOCOL"
    inputs = "runs-failures.json" if failures else "runs.json"
    digest = sha256((ROOT / (protocol + ".md")).read_bytes()).hexdigest()
    frozen = json.loads((ROOT / "data" / inputs).read_text())
    if digest != frozen["protocol_sha256"] or digest != (ROOT / (protocol + ".sha256")).read_text().split()[0]:
        raise ValueError("Protocol digest mismatch")
    for source in {r["workflow_sha256"] for r in frozen["runs"]}:
        body = (ROOT / "data" / "workflows" / (source + ".yml")).read_bytes()
        if sha256(body).hexdigest() != source:
            raise ValueError("Upstream workflow digest mismatch")
    return frozen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="compare with the saved result")
    parser.add_argument("--failures", action="store_true", help="replay the separate natural failure supplement")
    parser.add_argument("--export", nargs=2, metavar=("RUN:STAGE", "DIRECTORY"),
                        help="write just the request and receipts for one decision")
    args = parser.parse_args()
    records = load_data(args.failures)
    packets = failure_packets(records["runs"]) if args.failures else make_packets(records["runs"])
    if args.export:
        run, stage = args.export[0].split(":", 1)
        packet = next((p for p in packets if p["run"] == int(run) and p["kind"] == stage), None)
        if packet is None:
            parser.error("No such run or stage. See the README for supported stages.")
        target = Path(args.export[1])
        target.mkdir(parents=True, exist_ok=True)
        for attr in ("request", "receipts"):
            (target / (attr + ".json")).write_text(json.dumps(packet[attr], indent=2) + "\n")
        return
    groups = FAILURE_GROUPS if args.failures else PRIMARY_GROUPS
    result = {"runs": len(records["runs"]), "skipped": len(records["skipped"]), "groups": score(packets, groups)}
    if args.verify:
        result_name = "results-failures.json" if args.failures else "results.json"
        if json.loads((ROOT / result_name).read_text()) != result:
            raise SystemExit("Offline counts differ from " + result_name)
        print(f"Verified {len(packets)} packets from {len(records['runs'])} runs.")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
