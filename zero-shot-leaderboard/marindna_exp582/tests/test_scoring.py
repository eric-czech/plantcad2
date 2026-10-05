import numpy as np
import pytest
from scipy.special import log_softmax, softmax
from tokenizers import Tokenizer, models, normalizers, pre_tokenizers

from exp582_evals.scoring import SequenceScorer, embedding_features, reverse_complement


def character_tokenizer():
    tokenizer = Tokenizer(
        models.WordLevel(
            {"[UNK]": 0, "a": 1, "c": 2, "g": 3, "t": 4, "[EOS]": 5}, unk_token="[UNK]"
        )
    )
    tokenizer.normalizer = normalizers.Lowercase()
    tokenizer.pre_tokenizer = pre_tokenizers.Split("", "isolated")
    return tokenizer


def backend(vocab):
    logits = np.random.default_rng(7).normal(size=(vocab, vocab))
    logps = log_softmax(logits, axis=-1)

    def score(batch):
        return [logps[np.asarray(ids[:-1]), np.asarray(ids[1:])] for ids in batch]

    return logits, score


def test_character_candidates_reproduce_original_four_logit_softmax():
    tokenizer = character_tokenizer()
    logits, score = backend(6)
    model = SequenceScorer(tokenizer, score)
    probabilities = model.base_probabilities("tacga", 3)
    np.testing.assert_allclose(
        probabilities, softmax(logits[2, [1, 2, 3, 4]]), atol=1e-15
    )
    np.testing.assert_array_equal(probabilities, model.base_probabilities("tacTTTT", 3))


def test_bpe_retokenizes_before_variant_and_scores_only_divergent_suffix():
    tokenizer = Tokenizer(
        models.BPE(
            {"[UNK]": 0, "a": 1, "c": 2, "g": 3, "t": 4, "cg": 5},
            [("c", "g")],
            unk_token="[UNK]",
        )
    )
    _, score = backend(6)
    model = SequenceScorer(tokenizer, score)
    ref, alt = "ttaca", "ttacg"
    assert len(model.encode(ref)) == 5 and len(model.encode(alt)) == 4
    direct = [np.sum(x) for x in score([model.encode(ref), model.encode(alt)])]
    assert model.llr(ref, alt) == pytest.approx(direct[1] - direct[0])
    candidates = ["ttac" + x for x in "acgt"]
    expected = softmax(
        [np.sum(x) for x in score([model.encode(x) for x in candidates])]
    )
    np.testing.assert_allclose(model.base_probabilities(ref, 4), expected, atol=1e-15)
    with pytest.raises(ValueError, match="shared first token"):
        model.llr("ca", "cg")


def test_no_bos_eos_or_truncation_and_reverse_strand_involution():
    tokenizer = character_tokenizer()
    _, score = backend(6)
    model = SequenceScorer(tokenizer, score, max_tokens=4)
    assert model.encode("AcgT") == [1, 2, 3, 4]
    with pytest.raises(ValueError, match="truncation"):
        model.encode("ACGTA")
    assert reverse_complement(reverse_complement("ACGTN")) == "acgtn"
    assert model.strand_average_llr("actg", "acag") == model.strand_average_llr(
        "cagt", "ctgt"
    )


def test_probe_offsets_match_base_weighted_character_representation():
    tokenizer = Tokenizer(
        models.BPE({"a": 0, "c": 1, "g": 2, "t": 3, "cg": 4}, [("c", "g")])
    )
    hidden = np.asarray([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    whole, variant = embedding_features(tokenizer, "acgt", hidden, 2)
    np.testing.assert_array_equal(whole, (hidden[0] + 2 * hidden[1] + hidden[2]) / 4)
    np.testing.assert_array_equal(variant, hidden[1])
    with pytest.raises(ValueError, match="exactly one"):
        embedding_features(tokenizer, "acgt", hidden, 4)
