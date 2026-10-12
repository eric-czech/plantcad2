# Result 1 — exp586 MarinMoE 1.5B-60M 0.22T (scratch, 1× LR)

This is the first completed checkpoint from [MarinDNA #586](https://github.com/Open-Athena/marin-dna/issues/586). New inference was run only for this final checkpoint; every comparison model reuses prior results.

| Model | Total parameters | Active parameters | DNA training tokens | Approx. training FLOPs |
| :--- | ---: | ---: | ---: | ---: |
| MarinMoE 1.5B-60M 0.22T (scratch, 1× LR) | 1.395B | 60.555M | 216.159B tokens (1 nt/token) | 1.36×10²⁰ |

“Scratch” means random initialization. “1× LR” means the unmodified Hero-ladder learning-rate heuristic.

## Main result

![Best-settings model comparison](assets/exp586-model-family-overview.png)

At its selected **8K Natural** readout, MarinMoE 1.5B-60M 0.22T (scratch, 1× LR) reaches **0.7045** on the 20-task composite. This is the best Marin autoregressive result in the comparison: **+0.0203** over the token-matched MarinDNA 1B 0.22T checkpoint and **+0.0079** over the more extensively trained MarinDNA 1B 0.56T checkpoint.

It also exceeds PlantCAD2-Small (**0.6818**), while remaining below PlantCAD2.5-Large (**0.7229**), PlantCAD2-Large (**0.7344**), and Evo 2 20B (**0.7566**).

## Full task results at the selected setting

![Full-split task heatmap](assets/exp586-task-heatmap.png)

Against the best dense checkpoint, MarinMoE gains on conservation, masked motifs, and structural variants, while trailing slightly on core/non-core classification. The net composite improvement is **+0.0079**.

<details>
<summary><strong>Group scores and historical comparison</strong></summary>

| Model | Conservation | Masked motif | Core/non-core | Structural variant | Composite |
| :--- | ---: | ---: | ---: | ---: | ---: |
| MarinMoE 1.5B-60M 0.22T (scratch, 1× LR) | 0.6959 | 0.5811 | 0.6853 | 0.8559 | 0.7045 |
| MarinDNA 1B 0.22T | 0.6624 | 0.5428 | 0.6871 | 0.8448 | 0.6843 |
| MarinDNA 1B 0.56T | 0.6693 | 0.5696 | 0.6951 | 0.8526 | 0.6966 |
| PlantCAD2-Small | 0.6445 | 0.6059 | 0.6823 | 0.7946 | 0.6818 |
| PlantCAD2-Large | 0.7024 | 0.6777 | 0.7166 | 0.8410 | 0.7344 |
| PlantCAD2.5-Large | 0.7097 | 0.6954 | 0.7414 | 0.7450 | 0.7229 |
| Evo 2 20B | 0.7887 | 0.6552 | 0.7224 | 0.8600 | 0.7566 |

All values use the full splits and 8,192-position inputs. The composite gives each of the four task groups equal weight.

</details>

<details>
<summary><strong>All 20 task rows</strong></summary>

| Task | n | Metric | MarinMoE 1.5B-60M 0.22T (scratch, 1× LR) | Dense 0.56T | PC2 Small | PC2 Large | PC2.5 Large | Evo 2 20B |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Conservation · Andropogoneae, genome-wide | 38,060 | AUROC | 0.7391 | 0.7256 | 0.6555 | 0.7245 | 0.7170 | 0.7320 |
| Conservation · Poaceae, non-TIS CDS | 183,685 | AUROC | 0.7244 | 0.6977 | 0.6462 | 0.7125 | 0.7290 | 0.8620 |
| Conservation · Poaceae, TIS CDS | 36,662 | AUROC | 0.6241 | 0.5848 | 0.6319 | 0.6703 | 0.6830 | 0.7720 |
| Masked motif · Maize TIS (start) | 39,035 | Accuracy | 0.5419 | 0.4805 | 0.5449 | 0.6571 | 0.6960 | 0.6020 |
| Masked motif · Maize TTS (stop) | 39,035 | Accuracy | 0.4357 | 0.3857 | 0.2302 | 0.4096 | 0.4460 | 0.4530 |
| Masked motif · Maize splice donor | 153,869 | Accuracy | 0.8278 | 0.8206 | 0.8754 | 0.9104 | 0.9210 | 0.8220 |
| Masked motif · Maize splice acceptor | 153,869 | Accuracy | 0.8292 | 0.8162 | 0.8537 | 0.8996 | 0.9130 | 0.8260 |
| Masked motif · Tomato TIS (start) | 35,484 | Accuracy | 0.3997 | 0.4027 | 0.5274 | 0.5960 | 0.6120 | 0.5860 |
| Masked motif · Tomato TTS (stop) | 35,483 | Accuracy | 0.2118 | 0.2216 | 0.2051 | 0.2848 | 0.2940 | 0.3790 |
| Masked motif · Tomato splice donor | 140,456 | Accuracy | 0.7044 | 0.7184 | 0.8165 | 0.8387 | 0.8460 | 0.7890 |
| Masked motif · Tomato splice acceptor | 140,455 | Accuracy | 0.6984 | 0.7109 | 0.7940 | 0.8257 | 0.8350 | 0.7850 |
| Core/non-core · Maize TIS (start) | 36,409 | AUROC | 0.6068 | 0.6099 | 0.7070 | 0.6960 | 0.7430 | 0.6860 |
| Core/non-core · Maize TTS (stop) | 36,409 | AUROC | 0.6251 | 0.6431 | 0.5980 | 0.6080 | 0.6260 | 0.6860 |
| Core/non-core · Maize splice donor | 144,550 | AUROC | 0.7350 | 0.7628 | 0.7640 | 0.8080 | 0.8420 | 0.7760 |
| Core/non-core · Maize splice acceptor | 144,550 | AUROC | 0.7790 | 0.7928 | 0.7630 | 0.8360 | 0.8730 | 0.8040 |
| Core/non-core · Tomato TIS (start) | 35,478 | AUROC | 0.6159 | 0.6101 | 0.6220 | 0.6460 | 0.6680 | 0.6440 |
| Core/non-core · Tomato TTS (stop) | 35,477 | AUROC | 0.6186 | 0.6239 | 0.5350 | 0.5980 | 0.6060 | 0.6390 |
| Core/non-core · Tomato splice donor | 140,451 | AUROC | 0.7513 | 0.7584 | 0.7350 | 0.7670 | 0.7830 | 0.7660 |
| Core/non-core · Tomato splice acceptor | 140,451 | AUROC | 0.7511 | 0.7598 | 0.7340 | 0.7740 | 0.7900 | 0.7780 |
| Structural variant · Impact prediction | 18,075 | AUPRC | 0.8559 | 0.8526 | 0.7946 | 0.8410 | 0.7450 | 0.8600 |

</details>

## How the selected readouts were chosen

| Endpoint | Selected readout | Result |
| :--- | :--- | ---: |
| Main 20-task suite | 8K Natural | 0.7045 composite |
| Zero-shot maize AF | Centered 2K Natural | 0.1419 Spearman |
| Fitted maize AF | Centered 2K target-position, strand-averaged probe | 0.1935 Spearman |
| Task-independent next-base prediction | Equal two-sided PoE, 4,095 bases per side | 0.9166 NLL |

<details>
<summary><strong>Visual guide to Natural, PoE, and frozen probes</strong></summary>

The zero-shot methods score **probabilities** from a frozen model. The probes instead extract **hidden representations** from that frozen model and fit a small Ridge regression on separate training chromosomes.

```text
ZERO-SHOT PROBABILITIES

5′ — left flank — [X] — right flank — 3′
        └────────▶ X                   forward causal view
                   X ◀────────┘        reverse-complement causal view

Natural, tasks: score the two one-sided views independently; the historical
                protocol reports the better task-level orientation.
Natural, AF:    compute the causal ALT-vs-REF suffix score in both orientations
                and average the two scores.
Two-sided PoE:  align the two A/C/G/T distributions, take their geometric mean,
                renormalize, then score X using evidence from both flanks.

FROZEN-EMBEDDING PROBES

REF and ALT, each in forward + reverse-complement orientation
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
 mean all hidden states   hidden state at [X]
      “Whole”                 “Target”
          │                   │
          └─────────┬─────────┘
                    ▼
     average orientations  OR  concatenate orientations
         “Averaged”                 “Directional”
                    │
                    ▼
        StandardScaler → Ridge → predicted allele frequency
```

| Label | What changes | When it is useful |
| :--- | :--- | :--- |
| **Natural** | Uses ordinary causal scoring. Task evaluation selects the better orientation; AF averages the two orientation scores. | Historical baseline and best overall task/zero-shot AF result here. |
| **Full vocab** | Same AF suffix score, but probabilities are normalized over the tokenizer’s full vocabulary instead of only A/C/G/T. | Checks whether non-DNA token mass matters; it is effectively identical for this eight-token scratch vocabulary. |
| **Two-sided PoE** | Multiplies aligned forward and reverse-complement base probabilities with equal weight. No fitted parameters. | Best label-free use of both flanks for nucleotide prediction; helpful for some task groups, but not the overall suite. |
| **Whole vs target probe** | Uses either the mean hidden state across the window or only the state at the variant. | The target state is more informative for AF. |
| **Averaged vs directional probe** | Either averages aligned strand representations or concatenates them before Ridge. | Averaging is smaller and performs better here. |

The PoE definition is unchanged from [the detailed exp582 explanation](https://github.com/eric-czech/plantcad2/pull/2#issuecomment-6042124363).

</details>

### Context length

<p align="center"><img src="assets/exp586-task-context-deltas.png" alt="Task-score context deltas" width="720"></p>

The centered 2K crop generally reduces task accuracy, especially for masked motifs and maize splice-site core/non-core classification. It nevertheless gives the best zero-shot AF rank correlation.

<details>
<summary><strong>Natural versus two-sided task scores</strong></summary>

| Context / method | Conservation | Masked motif | Core/non-core | 3-group composite |
| :--- | ---: | ---: | ---: | ---: |
| 8K · Natural | 0.6959 | 0.5811 | 0.6853 | 0.6541 |
| 8K · Two-sided PoE | 0.7154 | 0.5880 | 0.6449 | 0.6494 |
| 2K · Natural | 0.6931 | 0.5657 | 0.6752 | 0.6446 |
| 2K · Two-sided PoE | 0.7166 | 0.5753 | 0.6406 | 0.6442 |

The three-group composite excludes structural variants because their established metric has no centered two-sided definition. PoE improves conservation and motifs, but its core/non-core loss prevents it from improving the combined score.

</details>

### Zero-shot allele frequency

<p align="center"><img src="assets/exp586-af-readouts.png" alt="Allele-frequency readouts" width="640"></p>

The best zero-shot choice is the centered **2K Natural** score. Two-sided PoE raises Pearson correlation but lowers the rank correlation used here.

<details>
<summary><strong>AF correlations on the fixed 94,075-variant split</strong></summary>

| Model / context | Readout | Pearson | Spearman |
| :--- | :--- | ---: | ---: |
| MarinMoE 1.5B-60M 0.22T (scratch, 1× LR) · 8K | Natural | 0.13148 | 0.13715 |
| MarinMoE 1.5B-60M 0.22T (scratch, 1× LR) · 8K | Full vocab | 0.13148 | 0.13715 |
| MarinMoE 1.5B-60M 0.22T (scratch, 1× LR) · 8K | Two-sided PoE | 0.17271 | 0.13458 |
| MarinMoE 1.5B-60M 0.22T (scratch, 1× LR) · 2K | Natural | 0.13131 | 0.14190 |
| MarinMoE 1.5B-60M 0.22T (scratch, 1× LR) · 2K | Full vocab | 0.13131 | 0.14190 |
| MarinMoE 1.5B-60M 0.22T (scratch, 1× LR) · 2K | Two-sided PoE | 0.16947 | 0.13100 |
| MarinDNA 1B 0.56T · 8K | Natural | 0.13696 | 0.14517 |
| PlantCAD2-Small · legacy 10k | Published | 0.16400 | 0.12700 |
| PlantCAD2-Large · legacy 10k | Published | 0.20200 | 0.15800 |

The PlantCAD2 rows use the older 10k sample and are shown only as historical context. No comparable PlantCAD2.5 or Evo AF result is available.

</details>

### Frozen-embedding probes

<p align="center"><img src="assets/exp586-probe-readouts.png" alt="Frozen-embedding probe readouts" width="700"></p>

The best fitted readout uses the **target-position embedding averaged across orientations**. The 2K and 8K versions are effectively tied; directional concatenation adds features without improving accuracy.

<details>
<summary><strong>Held-out probe Spearman</strong></summary>

| Model / context | Zero-shot | Whole averaged | Whole directional | Target averaged | Target directional |
| :--- | ---: | ---: | ---: | ---: | ---: |
| MarinMoE 1.5B-60M 0.22T (scratch, 1× LR) · 8K | 0.12905 | 0.17755 | 0.17447 | 0.19347 | 0.18937 |
| MarinMoE 1.5B-60M 0.22T (scratch, 1× LR) · 2K | 0.13881 | 0.18143 | 0.17913 | 0.19352 | 0.18981 |
| MarinDNA 1B 0.56T · 8K | 0.14154 | 0.18027 | — | 0.19501 | — |

The new rows use StandardScaler → Ridge with alpha selected by train-only grouped cross-validation. Error bars are paired 1 Mb genomic-block bootstrap 95% intervals.

</details>

### Task-independent PoE check

<p align="center"><img src="assets/exp586-intrinsic-methods.png" alt="Intrinsic bidirectional method comparison" width="600"></p>

Equal two-sided PoE lowers held-out nucleotide NLL at every tested context without using PlantCAD task labels. Both orientations from each source window remain in the same split.

<details>
<summary><strong>Earlier 11.5B-481M MoE references</strong></summary>

| Model | DNA tokens | 20-task composite |
| :--- | ---: | ---: |
| MarinMoE 11.5B-481M (pretrained, 1× LR) | 11.24B | 0.6213 |
| MarinMoE 11.5B-481M (scratch, 2× LR) | 11.24B | 0.6256 |
| MarinMoE 11.5B-481M (pretrained control) | 0 | 0.3607 |

These exp582 checkpoints are architecture references only. They saw far fewer DNA tokens and are not budget-matched to the new 0.22T result.

</details>

<details>
<summary><strong>Training, execution, and verification</strong></summary>

- Architecture: 8-layer d768 latent MoE with 384 routed experts, eight selected per token, two shared experts, 384-wide latent experts, 2,048-token sliding attention, and global attention every fourth layer.
- Tokenizer: eight entries, one token per nucleotide, case normalization, and EOS reserved for future use. EOS was not injected into training examples.
- Learning rate: peak MuonH 0.003320 and Adam 0.0007661 from the Hero scaling heuristic; 1% warmup followed by linear decay to 5% of peak.
- Training: 216,158,699,520 input tokens, 412,290 updates, a global batch of 64 sequences × 8,192 tokens, and ten exact dataset epochs.
- FLOPs: Marin/Levanter analytic forward estimate 209,719,296 FLOPs/token; 3× forward-plus-backward convention gives 1.36×10²⁰ training FLOPs and matches the W&B cumulative analytic counter. Communication, optimizer bookkeeping, and rematerialization are excluded.
- Evaluation: 1,727,943 rows across 20 tasks at 8K, 19 centered tasks at 2K, and 94,075 AF variants at each context. All 4,655 worker artifacts, receipts, checkpoint/tokenizer bindings, and planned shards were read directly from CoreWeave S3 and hash-verified.
- Backend: ring EP for training; dropless Sonic for evaluation after an independent comparison reached 98.96% argmax agreement, 0.00030 NLL difference, and 0.00176 mean probability difference.
- Checkpoint: final update 412,290; canonical metadata digest `737fa99f…72d9`; tokenizer digest `0753679a…78c`.
- [Training run](https://forge.coreweave.com/wandb/eric-czech/marin/runs/exp586-plantcad2-d768-scratch-lrm1-seed0-v1) · [postprocess run](https://forge.coreweave.com/wandb/eric-czech/marin/runs/exp586-plantcad2-d768-scratch-lrm1-seed0-final-eval-postprocess-v1)

</details>
