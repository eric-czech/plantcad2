import copy

import numpy as np
import pytest
from test_scoring import backend, character_tokenizer

from exp582_evals.runtime_validation import synthetic_requests, validate_outputs


def test_synthetic_validation_consumes_saved_outputs_and_rejects_mismatches():
    tokenizer = character_tokenizer()
    requests = synthetic_requests(tokenizer, bases=64)
    _, score = backend(6)
    logs = score([item["ids"] for item in requests["requests"]])
    features = np.random.default_rng(582).normal(size=(len(logs), 8))
    metrics = validate_outputs(tokenizer, requests, logs, features, features * 2)
    assert metrics["requests"] == len(logs)
    assert np.isfinite(list(metrics.values())).all()
    with pytest.raises(ValueError, match="counts differ"):
        validate_outputs(tokenizer, requests, logs[:-1], features, features)
    bad = copy.deepcopy(requests)
    bad["requests"][0]["ids"][0] = 99
    with pytest.raises(ValueError, match="canonical tokenization"):
        validate_outputs(tokenizer, bad, logs, features, features)
    bad = copy.deepcopy(requests)
    bad["tokenizer_sha256"] = "wrong"
    with pytest.raises(ValueError, match="Tokenizer differs"):
        validate_outputs(tokenizer, bad, logs, features, features)
