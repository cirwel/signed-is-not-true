# Reviews of the analysis and the report

Three reviews were made before the report was resubmitted. All three reviewers are AI models. The
author read the report afterwards and is responsible for it.

## 1. Code review, 14 November 2026, about 21:00 UTC

**Reviewer:** a second instance of the model family that wrote the code (Claude), started with no
context. It read the harness and recomputed six runs by hand.

**No problem found in:** leakage of ground truth into any prompt; the pairing of handoffs; the exact
McNemar test; the Holm adjustment; the replay of recorded handoffs.

| Finding | What was done |
|---|---|
| Handoffs where W1 had imported the orders wrongly were scored as W2's false dones (61 of nemotron3's 126 handoffs at the time) | W2 is now counted only where W1's import was right; the others are in a column of their own |
| Figure 1 put reports that were not in the agreed form together with misreports | The figure uses the three-way split of the tables and leaves those reports out |
| A catch is any hold, whatever reason was given | Table R10 added: what the holds were about |
| Runs ended by a server error count as not caught | Kept (the lock says incomplete runs are counted); disclosed in Appendix A, counted in Table R10 |
| Wrong payouts in Study 3 were found by comparing whole dictionaries, so an unfinished W3 counted as paying wrongly | Study 3 now uses Study 2's rule: at least one committed payout differs from the correct amount |

Each change is recorded with its time in `HYPOTHESES.md` under "Changes after the second lock".

## 2. Independent recount, 14 November 2026, about 23:15 UTC

**Reviewer:** an agent of the same family with no context, told not to open the analysis code, the
tables or the report. It was given the definitions and 23 groups of numbers from the report, wrote
its own script, and counted from the raw run files (6,436 files, none failed to parse).

**Result:** all 23 groups matched. All five quoted lines were found in the transcripts.

| Note from the recount | What was done |
|---|---|
| Per handoff, holds in the note-carrying arm were fewer under the duty prompt for 20 of 20 handoffs (gpt-6-luna) and 11 of 20 (claude-haiku-5-5), more for none | Section 4.4 now reports this test, which takes the handoff as the unit, in place of the test on 60 handoff-and-signal pairs |
| 9 of the 14 false dones gemma4 did not catch under the duty prompt were runs ended by a server error | Stated in Appendix A |
| Three gpt-6-luna runs ended by saying the batch needed review without calling `hold` and are scored as not caught | Definition kept (a catch needs a `hold` call); stated in Appendix A |
| Every silent partial report has `refunds_applied` as its only key | Consistent with the report; W2's prompt is in Appendix C |

## 3. Second-family review of the draft, 14 November 2026, about 23:40 UTC

**Reviewer:** gpt-6-sol (OpenAI), through the Codex command-line tool, read-only, with the report,
both locks, the tables, the code and the run files. It recounted five results from the run files and
checked 25 further numbers in the prose against the tables; all agreed.

| Finding | What was done |
|---|---|
| The run-count table put the goal-prompt runs in the row for the locked design | Fixed: the locked design, each follow-up arm and the totals have rows of their own |
| "Three receivers paid ... usually after noting the mismatch" was false for gemma4, whose reasoning never mentions it | Reworded: two of the three usually noted it |
| The outcome given for H11 left out nemotron3, a locked worker (1 of 7 faithful, 6 not in the agreed form) | Table D1 now gives each locked worker's outcome |
| H4 read as confirmed by the locked runs; all 80 cases come from the *wrong* condition, added after the lock | Table D1 and Section 4.1 now say so |
| "An accurate signature line changed nothing" treats a non-significant contrast as no effect; "caught every false report" is wider than what was observed | Reworded to "made no detectable difference" and "stopped every report that differed from the table" |
| No forged, replayed or expired voucher was ever presented, so the study does not measure what a signature check is for | Added to Methods and Appendix A |
| Table O6 counted a refund missing from both the table and the report as "reported as it was applied" (changes two nemotron3 cells) | Fixed in `harness/analyze_organic.py`; no number in the report changed |
| The harness lets a second payout to a customer replace the first, although the prompt says payouts cannot be recalled; scoring uses final rows | Table R12 added (one run affected, an honest handoff); stated in Appendix A |

The reviewer's own estimate against the rubric before these fixes: Impact and Innovation 4 of 5,
Execution 3 of 5, Presentation 3 of 5.

## 4. Second pass by the same second-family reviewer, 14 November 2026, about 23:45 UTC

**Reviewer:** gpt-6-sol again, read-only, on the revised draft. It confirmed six of its eight findings
as fixed and two as partly fixed (the run totals were still moving while it read; the harness still
allows a payout to be overwritten, which is now measured and disclosed). It was then asked what most
held the report back on execution and on presentation.

| Suggestion | What was done |
|---|---|
| Methods defined a catch as "not letting W3 pay", but the scoring needs a `hold` call and counts unfinished runs as misses | Methods now gives the scoring rule; the badge result is reported as holds, wrong payouts and unfinished runs |
| "Each written into the lock file before its first run" could make the follow-up arms sound confirmatory | Reworded: chosen after seeing earlier results, recorded before their own runs, exploratory |
| The note-carrying arm's p values should be labelled descriptive, and its scope stated | Done in Section 4.4 and in contribution 5 |
| "A signed field for exceptions would let a rule catch the partial reports" claims more than was tested | Reworded as a design that was not tested here |
| Table 1 (twelve rows) repeated Figure 2 | Replaced by a table of the contrasts the prose rests on; the full grid is Table E2 |
| The summary table's six-number cells were hard to read | Table 2 now shows two named receivers; all six are in Table E10 |
| Four recommendations in one paragraph | Now a numbered list, one rule and its supporting result each |
| Cut the badge-wording catalogue and the aside on claims with no work behind them | Both shortened, not cut: each is one of the report's unplanted or mechanism findings |
| Move "Prior work used" to an appendix | Not done: the sprint's rules ask for pre-sprint code to be marked in the report, so it stays in Methods |
