# What counts as a completed handoff?

**An internal replay of PyPA’s packaging test workflow · November 19, 2026**

The question was whether a receiving maintainer could safely act on a report in which every listed check had passed. The upstream project supplied the definition of completion through its workflow at each commit and the recorded verdict of its `All pass` job. I ran the check internally. No PyPA maintainer participated.

## Findings

In the first 16 eligible main-branch runs, exactly 53 of 54 required jobs had succeeded just before the final job finished. Reading the 53 positive receipts alone approved every unfinished handoff. Checking the expected count against distinct job names from the requested run held all 16. Matching every required name to a receipt gave the same decisions. Each method accepted all 16 completed runs.

The primary sample contained no native final failures. A separately specified supplement selected six real first-attempt failures of the upstream aggregate. All three methods held all six when shown the receipt of every required job. No method saw the `All pass` verdict or the jobs outside the required set. When I constructed handoffs listing only the successful jobs, checking the listed outcomes alone accepted all six. The count and exact-name methods held all six.

| Handoff evaluated | Reference decision | Errors when trusting listed successes | Errors with expected count and run identity | Errors with exact check names and run identity |
| --- | --- | ---: | ---: | ---: |
| Just before the last check finished, 16 runs | Hold | 16 false accepts | 0 | 0 |
| Same 16 runs after successful completion | Accept | 0 false holds | 0 | 0 |
| Every required job’s receipt from six actual aggregate failures | Hold | 0 | 0 | 0 |
| Same six failures, showing just successes | Hold | 6 false accepts | 0 | 0 |
| Separate substitution of one earlier run’s passing receipt, 15 cases | Hold | 15 false accepts | 0 | 0 |

The rows reuse runs. There were 22 distinct run IDs and 59 decision packets. The incomplete handoffs and receipt substitutions were created for the study. Upstream supplied the real job histories and final outcomes. The six failures were selected deliberately, so these data cannot estimate how often maintainers encounter incomplete reports.

## Two auditable examples

- On the newest primary run, 53 jobs had passed while `Downstream virtualenv` was still outstanding. Its later success completed the 54-job requirement. [Upstream run](https://github.com/pypa/packaging/actions/runs/44384018340) · [Final prerequisite](https://github.com/pypa/packaging/actions/runs/44384018340/job/135083562005) · [Native decision](https://github.com/pypa/packaging/actions/runs/44384018340/job/135086518191)
- In the failure supplement, one run had 43 successes and one failure among 44 required jobs. The native aggregate failed. A handoff listing the 43 successes told the truth about every listed job and left the required set incomplete. [Upstream run](https://github.com/pypa/packaging/actions/runs/30328648221) · [Native decision](https://github.com/pypa/packaging/actions/runs/30328648221/job/90180382710)

## What transfers

A receiving system can obtain the request from a trusted workflow definition and receipts from an authoritative job service. If the upstream maintainer already supplies a trusted aggregate for the exact run, that aggregate directly answers this question. This sample found no added detection from matching exact names beyond the simpler count with distinct names and the correct run identity. No packet in the sample could have separated the two: jobs outside the required set are removed before any method sees the receipts, and the two checks differ only when a list reaches the right count with a job that was never required. The sample covers one project, a set of CI completion decisions and an internal evaluator. It says nothing about the correctness of source code outside those checks, the behavior of an LLM reading the handoff or independent operator replication.

## Reproduce and use the checker

The default replay and standalone checker use Python 3.9+ with its standard library. From this directory run

```sh
python3 replay.py --verify
python3 replay.py --failures --verify
```

To inspect one exact decision, export a packet and pass it to the generic checker.

```sh
python3 replay.py --export 44384018340:early example
python3 check.py example/request.json example/receipts.json
```

The example returns `hold` and names the outstanding `Downstream virtualenv` check. Use `terminal` to inspect the successful handoff. For the omission in the failed run above, use `python3 replay.py --failures --export 30328648221:omitted_failure example`. The checker exits 0 on accept, 1 on hold and 2 for invalid input.

To use another workflow, supply a request with a nonempty `scope` string and a `checks` list of required names. Supply receipts with `scope`, `name` and `outcome` fields, recording a passing result as `success`. Bind scope to the exact unit that was requested. The GitHub adapter combines repository, run, attempt and commit. The checker expects this data from trusted sources and performs no authentication itself. Numeric provider job IDs are retained as provenance in the examples.

## Evidence

- `PROTOCOL.md` and `FAILURE-SUPPLEMENT.md` contain the locally frozen selection and scoring rules. Their corresponding SHA-256 files identify the exact text.
- `data/frame*.json` records the ordered public candidate frames. `data/runs*.json` records eligible attempts, exclusions, per-commit workflow sources, job IDs and the native verdict. Of 13 candidates in the failure frame, six had a successful native aggregate on attempt one. The target of six native failures was reached after 12 candidates. The 13th was not evaluated.
- `data/workflows/` holds the upstream definitions by digest and PyPA’s license notices. `ADAPTER-NOTE.md` records the correction used to read historical workflows with jobs outside the aggregate’s dependencies.
- `results.json` and `results-failures.json` contain the reference denominators, false accepts and false holds. `SHA256SUMS` covers the delivered files.
- To re-fetch public evidence, `collect.py` requires Python 3.11+, PyYAML, curl and network access. Run it in a copy with and without `--failures`. Upstream retention can affect later downloads. The frozen offline replay needs no credentials or network access.
