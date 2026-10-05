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
Language BPE needs explicit base-coordinate handling: four vocabulary logits cannot represent the original next-base task.
The proposed causal-prefix scoring rule remains a protocol choice for review.
The training branch owns native model restoration and CoreWeave execution; all jobs use batch priority and user `eczech`.
