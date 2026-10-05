"""The MoE inference boundary for the existing PlantCAD2 evaluation protocol."""

import time
from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd
import torch

from exp582_evals.protocol import original


class NativeAdapter:
    plantcad_native = True

    def __init__(self, scorer: Any, tokenizer: Any) -> None:
        self.scorer, self.tokenizer = scorer, tokenizer
        ids = [tokenizer.encode(base, add_special_tokens=False).ids for base in "ACGT"]
        if any(len(x) != 1 for x in ids) or [x[0] for x in ids] != list(
            scorer.base_ids
        ):
            raise ValueError(
                "Nucleotide projection does not match actual character encoding"
            )
        if [x[0] for x in ids] not in ([3, 4, 5, 6], [64, 66, 70, 83]):
            raise ValueError("Unexpected exp582 nucleotide IDs")

    def score_positions(
        self,
        sequences: pd.Series,
        positions: list[int],
        batch_size: int,
        progress: Callable[[int, int], None] | None = None,
    ) -> tuple[np.ndarray, dict]:
        if batch_size != self.scorer.batch_size:
            raise ValueError("Native collective batch size differs")
        start = time.monotonic()
        outputs = []
        for offset in range(0, len(sequences), batch_size):
            batch = sequences.iloc[offset : offset + batch_size].tolist()
            ids = [
                self.tokenizer.encode(x, add_special_tokens=False).ids for x in batch
            ]
            output = self.scorer.evaluate(
                ids, [positions] * len(batch), [0] * len(batch), allele_frequency=False
            )
            outputs.append(output["probabilities"][:, : len(positions)])
            if progress is not None:
                progress(offset + len(batch), len(sequences))
        wall = time.monotonic() - start
        tokens = int(sequences.str.len().sum())
        return np.concatenate(outputs), {
            "sequences": len(sequences),
            "tokens": tokens,
            "wall_seconds": wall,
            "gpu_seconds": None,
            "sequences_per_second": len(sequences) / wall,
            "tokens_per_second": tokens / wall,
        }

    def allele_frequency(self, frame: pd.DataFrame) -> tuple[dict, dict]:
        """Use original suffix reduction and strand-averaged frozen representations."""
        protocol = original()
        predictions = {"row_id": frame.row_id.to_numpy(dtype=np.int64)}
        embeddings = {"row_id": predictions["row_id"]}
        strands = {}
        for strand in ("fwd", "rc"):
            position = protocol.af.variant_position(8192, strand)
            values = {"ref": [], "alt": []}
            for offset in range(0, len(frame), self.scorer.batch_size):
                batch = frame.iloc[offset : offset + self.scorer.batch_size]
                refs = batch.sequence.tolist()
                alts = [
                    s[:4096] + a.upper() + s[4097:]
                    for s, a in zip(refs, batch.alt, strict=True)
                ]
                for allele, sequences in [("ref", refs), ("alt", alts)]:
                    if strand == "rc":
                        sequences = [
                            protocol.af.reverse_complement(s) for s in sequences
                        ]
                    ids = [
                        self.tokenizer.encode(s, add_special_tokens=False).ids
                        for s in sequences
                    ]
                    values[allele].append(
                        self.scorer.evaluate(
                            ids,
                            [[position]] * len(ids),
                            [position] * len(ids),
                            allele_frequency=True,
                        )
                    )
            merged = {
                allele: {key: np.concatenate([x[key] for x in rows]) for key in rows[0]}
                for allele, rows in values.items()
            }
            paired = {
                key: torch.from_numpy(
                    np.stack([merged[a][key] for a in ("ref", "alt")], axis=1)
                )
                for key in ("acgt_logs", "full_logs", "valid")
            }
            scores = protocol.af.reduce_uncached(
                paired["acgt_logs"], paired["full_logs"], paired["valid"], position
            ).numpy()
            for col, index in [
                ("llr_acgt", 0),
                ("llr_full_vocab", 1),
                ("non_acgt_targets", 2),
            ]:
                predictions[f"{col}_{strand}"] = scores[:, index]
            strands[strand] = merged
        for representation, field in [
            ("whole_window", "mean"),
            ("variant_token", "variant"),
        ]:
            for allele in ("ref", "alt"):
                embeddings[f"{representation}_{allele}"] = (
                    strands["fwd"][allele][field].astype(np.float32)
                    + strands["rc"][allele][field].astype(np.float32)
                ) * np.float32(0.5)
        return predictions, embeddings
