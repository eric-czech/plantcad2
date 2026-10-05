# MarinDNA exp582 evaluations

Compare the d1536 pretrained and random MoE conditions from [MarinDNA #582](https://github.com/Open-Athena/marin-dna/issues/582) with the existing exp472 dense results.
Report the original 20 tasks, maize allele-frequency scoring, and frozen whole-window and variant-token probes together.

The `historical/` artifacts are unchanged copies of previous computations, with source revisions and SHA-256 hashes in its two manifests.
No dense-model inference, training, or probe fitting is part of this workflow.
The task catalog pins the same dataset revision and all 20 tasks.

```bash
uv run pytest
uv run python -m exp582_evals.historical .
```

MoE scoring and embedding adapters are being validated before any production evaluation.
Both conditions now encode one token per DNA character: pretrained uses its original language vocabulary IDs, and scratch uses the reduced DNA vocabulary.
The training project supplies the lowercase character tokenizer; its original BPE tokenizer remains available separately for future text evaluations.
The causal-prefix candidate scorer is exactly the four A/C/G/T output-logit softmax for these encodings, with no right flank supplied.
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
