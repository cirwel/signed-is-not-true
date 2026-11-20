# Addendum: every listed job passed, and a required job is missing

*Exploratory. Run on 19 November 2026, after the report was submitted. Not part of the
report, its hypothesis locks or its judged results.*

The report's third design rule ends with "Next: such a request, compared by a rule." This
addendum is a first, small look at that on records nobody in this project wrote. The
question: can a receiver trust a handoff in which every listed job passed, when a required
job is missing from the list?

## What this is

An internally run replay. I chose the project, wrote the checker and scored the results.
The rules for what counts as complete are PyPA's: the `pypa/packaging` test workflow as it
stood at each commit, and the recorded verdict of its own `All pass` job. The job
histories and verdicts are public GitHub records. The incomplete handoffs were constructed
for this study from those records. No PyPA maintainer took part, none was asked, and
nothing here is a claim that a maintainer or an agent ever sent such a handoff. No LLM
reads anything in this replay: all three methods are rules in code.

The three methods, given the same receipts each time:

1. **Trust the list.** Accept if the list is not empty and every listed job succeeded.
2. **Count.** Also require as many distinct job names as the workflow requires, no
   duplicates, and every receipt from the requested run, attempt and commit.
3. **Exact names.** Require one passing receipt from the requested run, attempt and commit
   for each required job name.

## The count check tied exact name matching

On all 59 decision packets the count check and exact name matching gave the same
decision. Matching names caught nothing that counting distinct passing jobs from the
correct run did not.

Read this tie narrowly. No packet in this sample could have separated the two. The adapter
removes jobs outside the workflow's required set before any method sees the receipts, so
every listed name is a required name (0 of 59 packets list any other). The two checks
differ only when a list reaches the right count with a job that was never required, and
that case was not built. In the one spot-checked failed run, 17 jobs outside the required
set had passed, so the raw record contains the material for it. The tie shows that
counting was enough on handoffs built this way. It does not show that names are
unnecessary.

## Results

**Sixteen successful runs.** The first 16 eligible pushes to `main` before 19 November
2026, all first attempts, all on one version of the workflow with 54 required jobs,
created between 13 and 18 November. Just before the last required job finished, 53 of 54
had succeeded in every run.

| Handoff | Reference | Trust the list | Count | Exact names |
|---|---|---:|---:|---:|
| 53 listed successes, before the 54th job finished (16) | Hold | 16 accepted | 16 held | 16 held |
| The same runs at completion (16) | Accept | 16 accepted | 16 accepted | 16 accepted |

Trusting the list approved all 16 early. Both completeness checks held all 16 early and
accepted all 16 at completion. In 15 of the 16 runs the outstanding job was the same one
(`Downstream virtualenv`), so these are close to 16 repeats of one case.

**Six native failures, selected separately.** This supplement was written after the
result above was known, because the 16 runs contained no failure. It takes the six most
recent first-attempt failures of `All pass`, from April to October 2026, across five
versions of the workflow with 37 to 54 required jobs. They were selected for having
failed, so they say nothing about how often failures or incomplete handoffs occur.

| Handoff | Reference | Trust the list | Count | Exact names |
|---|---|---:|---:|---:|
| The full record of each failed run (6) | Hold | 6 held | 6 held | 6 held |
| Constructed: only that run's successes listed (6) | Hold | 6 accepted | 6 held | 6 held |

Shown the full record, all three methods held all six. When I constructed handoffs
listing only the successes, trusting the list accepted all six and both completeness
checks held all six. Every job on those lists did pass. In five of the six runs between 1
and 38 required jobs had failed. In the sixth none had failed: 36 of 54 were cancelled.

**Fifteen constructed stale-receipt controls, kept apart.** For 15 of the 16 successful
runs, the receipt of the last job to finish was replaced by a passing receipt for the same
job from the closest earlier run in the sample (the oldest run has no earlier one). Trusting the list accepted all
15. Both completeness checks held all 15, on run identity. These are constructed controls
and are not counted with the rows above.

The rows reuse runs: 22 distinct runs, 59 packets.

## Limits

- One project, one workflow, completion of CI only. Nothing here bears on whether code
  outside those checks is correct.
- Where a trusted `All pass` verdict for the exact run is already available, it answers
  the question directly and none of this is needed.
- The checker assumes the request and the receipts come from trusted sources. It
  authenticates nothing.
- The protocols were frozen locally by hash before the outcomes were fetched. They were
  not registered with anyone outside.
- The reader of older workflow files was corrected during the failure supplement, before
  the verdicts of the affected runs were examined. `maintainer-handoff-replay/ADAPTER-NOTE.md`
  records it.
- It does not test the report's LLM receivers, and no one outside has repeated it.

## Verify

From `addendum/maintainer-handoff-replay/`, with Python 3.9 or later and no network:

```sh
sha256sum -c SHA256SUMS                  # 24 files, all OK
python3 replay.py --verify               # Verified 47 packets from 16 runs.
python3 replay.py --failures --verify    # Verified 12 packets from 6 runs.
```

Two runs to check against GitHub by hand:

- Successful: [run 44384018340](https://github.com/pypa/packaging/actions/runs/44384018340).
  Last required job, [`Downstream virtualenv`](https://github.com/pypa/packaging/actions/runs/44384018340/job/135083562005);
  [`All pass`](https://github.com/pypa/packaging/actions/runs/44384018340/job/135086518191) succeeded.
- Failed: [run 30328648221](https://github.com/pypa/packaging/actions/runs/30328648221).
  43 of 44 required jobs succeeded, `Windows / 3.13t` failed, and
  [`All pass`](https://github.com/pypa/packaging/actions/runs/30328648221/job/90180382710) failed.

The protocol, the failure supplement, the frames, the per-commit workflow files with
PyPA's licence notices, and the code are in that directory.

This text was drafted by an AI coding agent (Claude) under the author's direction. The
agent also reran the checks above and compared the two runs with GitHub's records.
