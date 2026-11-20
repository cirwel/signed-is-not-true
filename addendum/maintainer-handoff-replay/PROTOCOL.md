# Maintainer handoff replay protocol

This is a locally frozen, exploratory internal replay. CIRWEL chose the project, wrote the checker and scores the results. PyPA wrote the workflow before this study. No outside maintainer or model is being tested. Selection and scoring below were written after inspection of the workflow definition and before retrieving the run list, jobs or outcomes.

## Frame and selection

Use the public `pypa/packaging` `.github/workflows/test.yml`. Inspect the newest 50 completed pushes to `main` created before 2026-11-19 00:00 UTC, in descending creation order. Use the first 16 eligible distinct run IDs. Eligibility requires a completed first attempt, an upstream `All pass` job with a success or failure verdict, at least two distinct timestamped prerequisite jobs and a readable workflow definition at that push SHA. The workflow must assign the strict `re-actors/alls-green` decision to the prerequisite jobs, with static job names or supported static matrices. Skip and record unsupported definitions or incomplete/uninterpretable timing data. A disagreement with the native decision never excludes a run. Report the native outcome mix. This is a convenience sample from one project.

## Decision and reference

An incoming handoff asserts that the required checks succeeded on this specific repository, run, attempt and commit. The independent reference for final completion is the upstream aggregate job's recorded verdict. At the early cut, at least one known prerequisite has not finished and the aggregate has not completed, so the appropriate decision is hold. The timestamps and job conclusions are real. Both handoffs are constructed views of those events. They are not claims made by upstream maintainers or agents.

Create two primary packets for each run. The early packet contains prerequisites that had finished strictly before the last recorded prerequisite completion second. This withholds all jobs tied in that final second. The terminal packet includes every prerequisite receipt available when the native aggregate finished. The checker sees the request and these receipts, never the aggregate job's verdict. Restrict the primary comparison to these two packets per run.

Compare three deterministic policies, using the same receipts. (1) Accept if the nonempty reported set consists entirely of successes. (2) Also require the expected number of distinct job names, no duplicates, and the correct run/attempt/commit on every receipt. (3) Require a unique passing receipt from that run/attempt/commit for each exact requested name. Ignore unrelated CI activity when constructing the input. Empty requests are invalid. Use a hold for incomplete or conflicting evidence. Count false accepts out of reference holds and false holds out of reference accepts. Report the early and terminal results separately. A simple policy tying the exact-name check is a substantive result.

## Secondary controlled substitution

For each eligible successful terminal packet, choose its last-finishing prerequisite (break ties by name). If an older successful sampled run has a passing receipt for that same job at a different commit, replace the current receipt with the one from the closest earlier qualifying run. Mark the packet incomplete for the requested run. These are constructed stale-evidence controls and must be scored separately from the primary replay. No substitution is evidence of an upstream incident.

## Interpretation and reproducibility

The study asks whether the rules reproduce the maintainer-authored CI decision on these snapshots and which added checks matter. It does not measure prevalence, user behavior, predictive value of EISV or independent adoption. A native aggregate can already answer the completion question when available. Freeze this file's hash locally before requesting run outcomes. Save the upstream recipe, public identifiers, receipt data, verdicts and replay code so another reader can rerun the comparison offline.
