"""Exercise native inference through the original task/AF entry points."""

import argparse
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
import torch
from tokenizers import Tokenizer, models, normalizers, pre_tokenizers

from exp582_evals.native import NativeAdapter, _center_crop
from exp582_evals.protocol import original


def tokenizer():
    t = Tokenizer(
        models.WordLevel(
            {"?": 0, "a": 3, "c": 4, "g": 5, "t": 6, "A": 7}, unk_token="?"
        )
    )
    t.normalizer = normalizers.Lowercase()
    t.pre_tokenizer = pre_tokenizers.Split("", "isolated")
    return t


class FakeScorer:
    base_ids = (3, 4, 5, 6)
    batch_size = 8

    def evaluate(self, ids, positions, feature_positions, *, allele_frequency):
        assert not allele_frequency
        p = np.array([0.6, 0.1, 0.2, 0.1], np.float32)
        return {"probabilities": np.tile(p, (len(ids), len(positions[0]), 1))}


def test_original_task_scoring_accepts_native_leaf():
    protocol = original()
    adapter = NativeAdapter(FakeScorer(), tokenizer())
    spec = {
        "kind": "conservation",
        "positions": [1],
        "contexts": ["left", "right_reverse_complement"],
    }
    frame = pd.DataFrame(
        {"sequence": ["AAA", "ACA", "AGA", "ATA"], "label": [1, 0, 1, 0]}
    )
    args = argparse.Namespace(batch_size=8, softmax_dtype="fp32", use_cache=False)
    result, arrays = protocol.tasks._score_standard_task(
        spec, frame, adapter, None, args, compute_metrics=False
    )
    assert result["contexts"]["left"]["peak_allocated_gib"] is None
    assert result["contexts"]["left"]["timing"]["gpu_seconds"] is None
    np.testing.assert_array_equal(
        arrays["left__scores"], np.array([0.6, 0.1, 0.2, 0.1], np.float32)
    )
    assert protocol.aggregate.recompute_task(spec, frame, arrays)["best_value"] == 1.0


def test_token_ids_follow_normalizer_instead_of_uppercase_vocab():
    NativeAdapter(FakeScorer(), tokenizer())
    with pytest.raises(ValueError, match="character encoding"):
        NativeAdapter(SimpleNamespace(base_ids=[7, 4, 5, 6]), tokenizer())


def test_center_crop_preserves_the_middle_base_and_rejects_asymmetry():
    assert _center_crop("AAAACCCC", 4) == "AACC"
    with pytest.raises(ValueError, match="centered"):
        _center_crop("AAAAAAA", 4)


def test_original_af_reduction_suffix_and_ambiguity():
    p = original()
    ref = torch.tensor([[-100.0, -100.0, -100.0, -100.0]])
    alt = ref + torch.tensor([[50.0, 1.0, 2.0, 3.0]])
    valid = torch.ones((1, 2, 4), dtype=torch.bool)
    valid[:, :, 2] = False
    acgt = torch.stack([ref, alt], dim=1)
    actual = p.af.reduce_uncached(acgt, acgt, valid, 2)
    # Earlier prefix cancels, ambiguous targets excluded only from ACGT score.
    np.testing.assert_array_equal(actual.numpy(), [[4.0, 6.0, 1.0]])
