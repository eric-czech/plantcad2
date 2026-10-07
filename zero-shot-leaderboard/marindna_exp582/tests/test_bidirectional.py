import numpy as np

from exp582_evals.bidirectional import (
    align_reverse_complement_probabilities,
    directional_probe_feature,
    target_log_likelihood_ratio,
    two_sided_probabilities,
)


def test_reverse_complement_alignment_reverses_positions_and_alleles():
    values = np.arange(24).reshape(2, 3, 4)
    expected = values[:, ::-1, :][..., [3, 2, 1, 0]]
    np.testing.assert_array_equal(
        align_reverse_complement_probabilities(values), expected
    )


def test_two_sided_product_and_target_ratio():
    forward = np.asarray([[[0.4, 0.3, 0.2, 0.1]]])
    reverse = np.asarray([[[0.1, 0.2, 0.3, 0.4]]])
    np.testing.assert_allclose(
        two_sided_probabilities(forward, reverse), forward, atol=1e-15
    )
    ratio = target_log_likelihood_ratio(
        forward[:, 0],
        reverse[:, 0],
        np.asarray([0]),
        np.asarray([3]),
    )
    np.testing.assert_allclose(ratio, np.log(0.1) - np.log(0.4), atol=1e-15)


def test_directional_probe_keeps_reference_and_delta_for_each_view():
    forward_reference = np.asarray([[1.0, 2.0]])
    forward_alternate = np.asarray([[4.0, 6.0]])
    reverse_reference = np.asarray([[10.0, 20.0]])
    reverse_alternate = np.asarray([[40.0, 60.0]])
    np.testing.assert_array_equal(
        directional_probe_feature(
            forward_reference,
            forward_alternate,
            reverse_reference,
            reverse_alternate,
        ),
        [[1.0, 2.0, 3.0, 4.0, 10.0, 20.0, 30.0, 40.0]],
    )
