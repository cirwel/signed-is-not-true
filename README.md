# Signed is not true

Entry for the Apart Research AI x Epistemics Research Sprint, 13 to 15 November 2026
(Track 2, Trust Infrastructure).

A signature proves who sent a claim. It does not prove the claim. This harness
measures the gap with LLM workers: in a three-worker refunds pipeline run for
two principals, how often does a false "done" get through each of three checks,
and how often does it then cause a wrong payout?

- **A, trust:** accept the "done" message.
- **B, signature only:** accept if the signed voucher's origin, audience and
  validity window verify.
- **C, signature and evidence:** as B, then the receiver reads the effect
  itself, digests it, and compares it with the digest in the voucher.

## What is preexisting and what is sprint work

**Preexisting, written before the sprint, not submitted for judging:**

- `preexisting/federation_tracer.py`: a verbatim copy of
  `scripts/demo/federation_tracer/tracer.py` from
  [cirwel/unitares](https://github.com/cirwel/unitares) (Apache-2.0), last
  changed 2026-08-03. The harness uses its `Governor` class: Ed25519 keys,
  compact-JWS vouchers that bind a SHA-256 evidence digest, origin
  verification, and `verify_voucher` with its `evidence_mismatch` result.
- The entry's design was sketched on 2026-11-04 as a plan for an earlier
  sprint that was not entered. No code or runs existed before this sprint.

**Written during the sprint (everything else in this repository):**

- `HYPOTHESES.md`: the hypothesis lock, committed before the first run.
- `harness/world.py`: the seeded batch, the SQLite world, the tools, the oracle.
- `harness/workers.py`: the LLM worker loop and prompts.
- `harness/run.py`: one run per model, condition and seed; applies the arms.
- `harness/analyze.py`: the tables; `harness/figure.py`: Figure 1.
- `report/REPORT.md`: the report text.
- All runs and results.

## Reproduce

Needs Python 3.11+, the `cryptography` package, and [Ollama](https://ollama.com)
serving the models named below.

```bash
python3 -m harness.run --models gemma4:latest --conditions honest,lie,fault --seeds 0-1 --out runs/smoke
python3 -m harness.analyze runs/smoke

# the full sweep behind the report (40 seeds; "wrong" was added after the hypothesis lock)
python3 -m harness.run --models gemma4:latest,qwen3.6:27b-coding-mxfp8 --conditions honest,lie,fault,wrong --seeds 0-39 --out runs/full
python3 -m harness.analyze runs/full > results/tables.md
python3 -m harness.figure runs/full results/figure1.png
```

Ground truth is the database: the oracle compares the refunds table and the
payouts table with what the seeded batch calls for. No worker's message is
used as evidence of what happened.

## AI assistance

The harness and analysis code were written during the sprint by an AI coding
agent working under the author's direction. The author is responsible for the
report and its claims.
