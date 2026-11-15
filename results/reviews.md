# Reviews of the analysis and the report

Seven review passes by three reviewers were made on the rewritten report, and a fourth agent had audited
the first version (section 7). All of them are AI models. The author read the report after the fourth
pass and is responsible for it; the later passes and the changes that followed them are in sections 5, 6
and 8. Section 8 is about the two arms added on the evening of 15 November, after the resubmission of
that day.

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

## 5. Third pass by the same second-family reviewer, 15 November 2026, about 03:35 UTC

**Reviewer:** gpt-6-sol again, read-only, after nemotron3 had finished its runs and the report had been
aligned with the sprint's official template. It checked 341 numbers in the main text against the tables
and the run records and found no mismatch. Before it, the nemotron3 cells, every row of Table 1 and the
badge-wording counts were recounted from the run records by a script that does not import the analysis
code; all agreed.

| Finding | What was done |
|---|---|
| "Left 3 unfinished" and "left 12 unfinished" count nemotron3's runs with neither a hold nor a wrong payout; Table R5 counts 7 and 18 runs that neither held nor paid every customer, because some of those had already paid a wrong amount | Section 4.2 now gives the three-way split in words that say what it is (held before any wrong payout, paid a wrong amount, neither); Appendix A gives both counts, each with its definition |
| "Four of five workers answered a failed tool call with a true but incomplete report" leaves out that gemma4 did the same in 15 of 40 runs with a reasoning field | The abstract now says "most workers" and "a true report of unfinished work"; contribution 4 says which worker did what "mostly", "almost always" and "always" |
| "One wording of each prompt and signal" in the new limitations paragraph overlooks the follow-up wordings | Now "in the locked design, one wording of each prompt and signal" |

## 6. Fourth pass by the same second-family reviewer, 15 November 2026, about 12:03 UTC

**Reviewer:** gpt-6-sol again, read-only, on the frozen report: after the cut-off of 12:00 UTC had been
applied and after qwen3.6, which reached 20 seeds of Study 2 at 11:10 UTC, had been added to the text as
a seventh receiver. It checked 385 numbers in the main text, the two main tables and the figure captions
against the tables and the run records and found no mismatch, and it confirmed from the run records'
finish times that the rule for showing qwen3.6 was recorded when that receiver had 18 runs. Before it,
every row of Table 1, the cells of all seven receivers and the counts of receivers that the prose states
in words were recounted from the run records by scripts that do not import the analysis code; all
agreed. A fresh clone of the branch rebuilt the same tables, figures and report with
`bash scripts/regenerate.sh`.

| Finding | What was done |
|---|---|
| The abstract and contribution 2 label nemotron3's 60 to 22 of 80 "pre-registered", but the pre-registered test pooled the locked receivers (175 to 138 of 200); and "raised them (20 to 79 of 80)" gives one receiver's exploratory result for two | Both now say "within the pre-registered test" (contribution 2 adds that it pooled the three locked receivers), mark the second receiver and the scope note as exploratory, and give both receivers' counts with the scope note (71 and 79 of 80). The same was done for the named check, where "58 to 2 of 60" had stood for two receivers: now "stopping 2 and 45 of 60" |
| "Four of seven receivers checked almost nothing" (conclusion, README) confuses checking with catching: gpt-5.4-nano read the refunds table in 29 of 80 such runs and caught 1 | Now "caught almost nothing", also in Sections 4.2 and 4.4 where the same word was used |
| The lock-file entry of 11:17 UTC says the scope note made no change for qwen3.6 (it caught 1 of 40 with it, 0 of 40 without), and says the generator checks "each of these counts" when it checks the counts of receivers | A dated correction was added to the lock file; the earlier entry is left as written |
| Section 4.3 still said "of these five workers" just before adding qwen3.6 as a sixth | qwen3.6's sentence now comes with the workers that sent the same kind of report, and the text says "of these six workers"; the generator stops the build if any worker of Table E4 other than claude-haiku-5-5 disclosed the failure |
| "No signal → 'Result: MISMATCH'" in Table 1 and "on that line alone" describe the signal too narrowly: it is the signature line plus the evidence result | Table 1's caption now says what the label stands for, Section 4.2 names both lines, and the sentence about qwen3.6 says "under that signal" |

## 7. Audit of the first submitted version by another agent, 14 November 2026, about 10:15 UTC

**Reviewer:** the agent session that built the author's second entry to the same sprint
([`crux-brief`](https://github.com/cirwel/crux-brief), a different track), working read-only on this
repository at commit `6c05b9c`: the version first submitted, which had Study 1 only. Its note records its
agent identity but not its model, so it counts here as a supplemental review and not as an independent
model family. It came before the rewrite and before every pass above; it is listed last so that the
section numbers the report and the lock file refer to stay as they are.

**No problem found in:** the 320 run records of Study 1 (no crash, none unfinished); every count and
Wilson interval of Study 1 against `results/tables.md`; the cost figures; the marking of the code written
before the sprint; the page limit.

| Finding | What was done |
|---|---|
| The abstract of the first version had 256 words, over the limit of 250 | The rewritten abstract has 248 |
| Three page breaks in the first PDF split a sentence, a figure from its caption, and the conclusion | The rewritten report keeps each figure with its caption, and its main text ends on page 8 |
| In `results/tables.md`, Table 7 was printed before Table 6 | The two are now numbered in the order they are printed (15 November, after the resubmission; no number changed) |

## 8. Fifth pass by the same second-family reviewer, 15 November 2026, about 23:05 UTC

**Reviewer:** gpt-6-sol again, read-only, on the report with the two arms run after the cut-off (the
request carried in the handoff, and other wordings of the two instructions). It checked 477 numbers about
the new arms and the run totals against `results/tables_request.md` and the run records, recounted the
1,600 and 240 run files itself, and found no mismatch. It confirmed that the first runs finished after
the commits that recorded what was expected, and that Table D2 reports the two expectations that held
only in part as such. Before it, a script that does not import the analysis code had recounted both arms
from the run records; all agreed.

| Finding | What was done |
|---|---|
| "Carrying the request closed the gap" overstates what was measured: every run of the arm showed the request line, so there was no comparison on the same handoffs without it | A control was run: the same 60 false dones without the line, under the three prompts that do not refer to it (900 runs, `runs/request_base/`), with the expectation recorded in the lock file first (B1 in Table D2). The abstract, contribution 6, Section 4.5 and the conclusion now state the condition (request shown, instruction given), give the result without the line, and say that the arm is exploratory and was run after the cut-off |
| Design rule 3 implied that a signed binding and a comparison with the table had been tested. The request was a line of text, no signature on it was verified, and the two weaker receivers often caught the shortfall from the message without reading the table | Rule 3 now says the request was shown as a line of the handoff and names a signed request compared by a rule in code as the next test; Section 4.5 points to the count of runs that read the table first (Table E11); Appendix A says the line's signature was neither made nor verified |
| In Methods, "the last two were run after the cut-off" read as if it meant the last two badge wordings | The sentence now follows the two arms it is about and names them; Appendix D says "the first three follow-up arms" |
| Table 2 and Table E10 did not say which comparison "told which check" was in the row with the request shown, and did not show the rates under the new request sentence | Table 2's header names the comparison (duty: report against table) and its third row adds the rate under the request sentence; Table E10 has a column for the request sentence, and its caption says what "told which check" is |
| A trim had turned "a median cost of 0.6 ms" into "in 0.6 ms", and Section 5 said "in under a millisecond"; 64 of the 320 Study 1 runs took 1 ms or more | Section 4.1 says "at a median of 0.6 ms" again and Section 5 says "in about a millisecond" |
| Appendix A said the two arms were run "from 22:12 UTC", which is when the expectations were committed; the first run finished at 22:13:19 UTC | Appendix A now gives both times |
