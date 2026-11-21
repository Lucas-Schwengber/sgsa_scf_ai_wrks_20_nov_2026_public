"""
Tests of the shared contract: families, problems and quadrature metrics.
"""

import numpy as np
import pytest
from scipy import stats

from ot_1d.families import Family, Gamma, Gaussian, ScipyFamily
from ot_1d.metrics import (evaluation_grid, expectation, relative_l2p_error,
                           solution_error)
from ot_1d.problem import Problem, Solution

FAMILIES = [Gaussian(0.0, 1.0), Gaussian(1.5, 0.7), Gamma(2.0, 1.0),
            Gamma(0.5, 2.0), Gamma(5.0, 0.3)]


@pytest.mark.parametrize("family", FAMILIES, ids=repr)
def test_exact_derivatives_match_numerical_defaults(family):
    """
    The exact dlogpdf and score agree with the finite-difference defaults.
    """
    x = family.ppf(np.linspace(0.02, 0.98, 25))
    np.testing.assert_allclose(family.dlogpdf(x), Family.dlogpdf(family, x),
                               rtol=1e-7, atol=1e-8)
    for param in family.params:
        np.testing.assert_allclose(family.score(x, param),
                                   Family.score(family, x, param),
                                   rtol=1e-7, atol=1e-8)


@pytest.mark.parametrize("family", FAMILIES, ids=repr)
def test_score_is_centred(family):
    """
    Every score has mean zero under p, so the score problems are solvable.
    """
    for param in family.params:
        problem = Problem.from_score(family, param)
        assert abs(expectation(family, problem.h)) < 1e-8


@pytest.mark.parametrize("family", FAMILIES, ids=repr)
def test_transport_linearization_solves_the_equation(family):
    """
    Where an elementary formula exists, (p Phi)' = h p holds pointwise.
    """
    x = family.ppf(np.linspace(0.05, 0.95, 19))
    lower, _ = family.support()
    step = 1e-4 * np.minimum(family.std(), x - lower)
    for param in family.params:
        problem = Problem.from_score(family, param)
        try:
            problem.exact_dphi(x)
        except NotImplementedError:
            continue

        def flux(y):
            return family.pdf(y) * problem.exact_dphi(y)

        lhs = (flux(x + step) - flux(x - step)) / (2 * step)
        np.testing.assert_allclose(lhs, problem.h(x) * family.pdf(x),
                                   rtol=1e-5, atol=1e-7)


def test_scipy_family_wraps_any_distribution():
    """
    ScipyFamily gives the same numbers as the hand-written Gamma.
    """
    generic = ScipyFamily("gamma", stats.gamma, a=2.0, scale=1.0)
    exact = Gamma(2.0, 1.0)
    x = exact.ppf(np.linspace(0.05, 0.95, 11))
    np.testing.assert_allclose(generic.pdf(x), exact.pdf(x))
    np.testing.assert_allclose(generic.dlogpdf(x), exact.dlogpdf(x),
                               rtol=1e-7)
    np.testing.assert_allclose(generic.score(x, "a"),
                               exact.score(x, "shape"), rtol=1e-7)


def test_with_params_and_domain():
    """
    with_params returns a modified copy; domain returns central quantiles.
    """
    family = Gaussian(0.0, 1.0)
    shifted = family.with_params(mu=2.0)
    assert shifted.params == {"mu": 2.0, "sigma": 1.0}
    assert family.params["mu"] == 0.0
    a, b = family.domain(1e-6)
    assert a == pytest.approx(-b)
    assert family.cdf(a) == pytest.approx(1e-6, rel=1e-6)
    with pytest.raises(KeyError):
        family.with_params(scale=1.0)


@pytest.mark.parametrize("family", FAMILIES, ids=repr)
def test_expectation_moments(family):
    """
    The quadrature reproduces the mean and variance of each family.
    """
    mean = expectation(family, lambda x: x)
    var = expectation(family, lambda x: (x - family.mean()) ** 2)
    assert mean == pytest.approx(family.mean(), abs=1e-8)
    assert var == pytest.approx(family.std() ** 2, rel=1e-7)


def test_evaluation_grid_and_errors():
    """
    The grid integrates p to its mass on [a, b]; errors behave as norms.
    """
    family = Gamma(2.0, 1.0)
    a, b = family.domain(1e-6)
    x, w = evaluation_grid(family, a, b)
    wp = w * family.pdf(x)
    assert np.all(np.diff(x) > 0) and x[0] > a and x[-1] < b
    assert wp.sum() == pytest.approx(1 - 2e-6, abs=1e-10)

    truth = x
    assert relative_l2p_error(truth, truth, wp) == 0.0
    assert relative_l2p_error(1.1 * truth, truth, wp) == pytest.approx(0.1)

    problem = Problem.from_score(family, "scale")
    solution = Solution(dphi=lambda y: 1.1 * y, domain=(a, b), method="test")
    err = solution_error(solution, problem.exact_dphi, family, a, b)
    assert err == pytest.approx(0.1)
