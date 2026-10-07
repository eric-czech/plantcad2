# MarinDNA exp582 evaluations

Compare the d1536 pretrained and random MoE conditions from [MarinDNA #582](https://github.com/Open-Athena/marin-dna/issues/582) with the existing exp472 dense results.
Report the original 20 tasks, maize allele-frequency scoring, and inference-only bidirectional methods first.
Frozen whole-window and variant-token probes will be added separately after the initial results are reviewed.

The `historical/` artifacts are unchanged copies of previous computations, with source revisions and SHA-256 hashes in its two manifests.
No dense-model computation is rerun; every historical comparison is read from archived results.
The task catalog pins the same dataset revision and all 20 tasks.

```bash
uv run --locked --extra cpu pytest
uv run --locked --extra cpu python -m exp582_evals.historical .
```

MoE scoring and embedding adapters are being validated before any production evaluation.
Both conditions now encode one token per DNA character: pretrained uses its original language vocabulary IDs, and scratch uses the reduced DNA vocabulary.
The training project supplies the lowercase character tokenizer; its original BPE tokenizer remains available separately for future text evaluations.
Candidate scoring uses the four A/C/G/T output-logit softmax for these encodings.
The native runner receives full windows, and causal attention masks the right flank when predicting each target; the synthetic prefix scorer supplies only the left prefix.
Allele-frequency scoring keeps full-vocabulary ALT-minus-REF likelihood and forward/reverse-complement averaging; the pretrained output vocabulary is not reduced during training or likelihood scoring.
The archive includes already-computed full-vocabulary dense metrics, alongside the previous A/C/G/T-restricted metrics.
With one token per base, whole-window feature pooling is the ordinary mean and a variant-token feature covers exactly the variant base.
The generic BPE scoring utilities remain available for interpreting earlier diagnostic artifacts, but are not the planned exp582 DNA encoding.
The training branch owns native model restoration and CoreWeave execution; all jobs use batch priority and user `eczech`.

`runtime_validation` generates separate synthetic windows and validates saved GPU token likelihoods and frozen features against the scoring interface.
It covers causal next-base scoring, REF/ALT reversal, reverse-complement averaging, and a train-only standardized fixed-alpha toy probe for each readout.
It also checks the historical FP32 strand-averaged `[REF, ALT − REF]` feature contract on four synthetic variant pairs, using forward position 4,096 and reverse-complement position 4,095.
These fixtures contain no benchmark labels, and their metrics are validation diagnostics, not scientific results or a substitute for the real probe's genomic-block cross-validation.
Keeping the scoring check on the CPU also avoids forwarding private-repository credentials to GPU workers.

## Real-data pilot

The implementation reuses the evaluator from [PR20 at `475fba5`](https://github.com/plantcad/plantcad2/tree/475fba58f81b79efa234d0018eb0776d1a960bfd/zero-shot-leaderboard/evo2_20b).
The original files live under `../evo2_20b/`, and the wheel includes them with the same relative paths.
`protocol.py` loads that code; `native.py` adapts MoE predictions to its inference interface.
Task formulas, reverse complements, row-range loading, chunk planning, whole-task metrics, strand selection, grouped ridge fitting, 1,000 genomic-block bootstrap draws and saved probes come from that implementation.
`protocol-provenance.json` records copied source hashes and the few integration changes.

`uv run --locked --extra cpu python -m exp582_evals.real_data --catalog task_catalog.json --genome <FASTA> --output <inputs/preparation.json>` prepares original-format Parquet rows: 128 per task and 2,112 maize variants.
It pins source revisions and reference genome, preserves archived exp472 genomic train/test memberships and verifies alleles and outer-split window separation.
It does not expand the benchmark into a whole-corpus sequence-request JSON.

The native runner uses batches of eight on one collective H100 node and the old row-range chunks (64 task rows or 32 AF rows).
It emits the original task, AF and frozen-embedding array schemas with extra checkpoint/tokenizer/input/source checksums.
The evaluation wheel is also hash-pinned and transferred through CoreWeave storage, so GPU workers need no private GitHub credentials.
The AF adapter calls the original FP32 ALT-minus-REF suffix reduction; nucleotide IDs come from actual character encoding rather than uppercase vocabulary lookup.
JAX runtime metadata explicitly leaves unavailable PyTorch allocator/GPU-event fields empty.

After verified chunk collection, `uv run --locked --extra cpu python -m exp582_evals.real_metrics --preparation <inputs/preparation.json> --directory <results> --condition <random|pretrained> --checkpoint-digest <SHA256>` invokes the original reducers and probe fitter, using this MoE checkpoint's AF scores as the probe baseline.
Only the pilot supplies a subset of the archived split; the original full-benchmark split builder retains its existing defaults and sample-size checks.
Saved probe estimators are reloaded and their predictions checked against the saved Parquet outputs.
This pilot validates integration, not final model quality; dense results remain archived computations only.
