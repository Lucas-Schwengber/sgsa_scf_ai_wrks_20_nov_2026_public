"""
Tests of the exact solver against formulas that do not use its quadrature.
"""

import time

import numpy as np
import pytest
from scipy import integrate, special

from ot_1d.families import Gamma, Gaussian
from ot_1d.ground_truth import solve_exact
from ot_1d.problem import Problem, Solution

# Tail probabilities from 1e-10 to 0.5, used on both sides of the median.
TAIL_PROBS = 10.0 ** np.linspace(-10.0, np.log10(0.5), 41)

ELEMENTARY_CASES = [
    (Gaussian(0.0, 1.0), "mu"),
    (Gaussian(0.0, 1.0), "sigma"),
    (Gaussian(1.5, 0.7), "mu"),
    (Gaussian(1.5, 0.7), "sigma"),
    (Gaussian(-3.0, 4.0), "sigma"),
    (Gamma(2.0, 1.0), "scale"),
    (Gamma(0.5, 2.0), "scale"),
    (Gamma(5.0, 0.3), "scale"),
]

GAMMAS = [Gamma(2.0, 1.0), Gamma(0.5, 2.0), Gamma(5.0, 0.3)]

# Eighth-order central difference weights for the offsets -4, ..., 4.
STENCIL = np.array([1 / 280, -4 / 105, 1 / 5, -4 / 5, 0.0,
                    4 / 5, -1 / 5, 4 / 105, -1 / 280])


### ---------------------------------------------------------------------------
### Helpers
### ---------------------------------------------------------------------------

def tail_points(family):
    """
    Points at the quantiles 1e-10, ..., 0.5 and 0.5, ..., 1 - 1e-10.

    Parameters
    ----------
    family : Family
        The density p.

    Returns
    -------
    x_lower : numpy.ndarray
        Points with F(x) in ``TAIL_PROBS``, length 41, increasing.
    x_upper : numpy.ndarray
        Points with 1 - F(x) in ``TAIL_PROBS``, length 41, decreasing.
    """
    return family.ppf(TAIL_PROBS), family.isf(TAIL_PROBS)


def gamma_shape_dphi_by_differences(family, x, upper):
    """
    Reference phi' for the Gamma shape score, by differences of the CDF.

    Uses phi' = -(dF/d shape) / p with an eighth-order central difference
    in the shape; the survival function replaces the CDF in the upper half
    so the difference keeps its relative accuracy in the tail.

    Parameters
    ----------
    family : Gamma
        The density p.
    x : numpy.ndarray
        Evaluation points, length m.
    upper : bool
        Whether to difference the survival function instead of the CDF.

    Returns
    -------
    numpy.ndarray
        Reference values of phi'(x), length m.
    """
    shape = family.params["shape"]
    step = 2e-3 * min(1.0, shape)
    total = np.zeros_like(x)
    for offset, weight in zip(range(-4, 5), STENCIL):
        member = family.with_params(shape=shape + offset * step)
        total += weight * (member.sf(x) if upper else member.cdf(x))
    dcdf = (-total if upper else total) / step
    return -dcdf / family.pdf(x)


def gamma_shape_dphi_by_series(family, x):
    """
    Reference phi' for the Gamma shape score, by a power series.

    Differentiates in the shape a, term by term, the series
    F(x) = exp(-z) sum_n z^(a+n) / Gamma(a+n+1) with z = x / scale. All
    terms have the same sign when log z < digamma(a + 1), so the sum is
    accurate to rounding in the lower half of the distribution.

    Parameters
    ----------
    family : Gamma
        The density p.
    x : numpy.ndarray
        Evaluation points at or below the median, length m.

    Returns
    -------
    numpy.ndarray
        Reference values of phi'(x), length m.
    """
    shape, scale = family.params["shape"], family.params["scale"]
    z = x / scale
    n = np.arange(200)[:, None]
    terms = (np.exp(-z + (shape + n) * np.log(z)
                    - special.gammaln(shape + n + 1))
             * (np.log(z) - special.digamma(shape + n + 1)))
    return -terms.sum(axis=0) / family.pdf(x)


def gauss_sin_dphi(x):
    """
    Closed form of phi' for p = N(0, 1) and h = sin, by the complex erfc.

    Uses int_{-inf}^{x} exp(iy) p(y) dy = exp(-1/2) Phi(x - i), with Phi
    the normal CDF, and the complementary integral above the median.

    Parameters
    ----------
    x : numpy.ndarray
        Evaluation points, length m.

    Returns
    -------
    numpy.ndarray
        Values of phi'(x), length m.
    """
    z = (x - 1j) / np.sqrt(2.0)
    below = 0.5 * np.exp(-0.5) * special.erfc(-z).imag
    above = -0.5 * np.exp(-0.5) * special.erfc(z).imag
    return np.where(x <= 0, below, above) / Gaussian(0.0, 1.0).pdf(x)


### ---------------------------------------------------------------------------
### Accuracy
### ---------------------------------------------------------------------------

@pytest.mark.parametrize("family, param", ELEMENTARY_CASES,
                         ids=lambda v: v if isinstance(v, str) else repr(v))
def test_matches_elementary_formulas(family, param):
    """
    Score problems with an elementary phi' are solved to 1e-11, tails too.
    """
    problem = Problem.from_score(family, param)
    solution = solve_exact(problem)
    for x in tail_points(family):
        # atol only matters where phi' crosses zero (sigma at the median)
        np.testing.assert_allclose(solution(x), problem.exact_dphi(x),
                                   rtol=1e-11, atol=1e-12 * family.std())


@pytest.mark.parametrize("family", GAMMAS, ids=repr)
def test_gamma_shape_matches_cdf_differences(family):
    """
    The Gamma shape problem agrees with -dF/d(shape) / p on both sides.
    """
    solution = solve_exact(Problem.from_score(family, "shape"))
    x_lower, x_upper = tail_points(family)
    np.testing.assert_allclose(
        solution(x_lower),
        gamma_shape_dphi_by_differences(family, x_lower, upper=False),
        rtol=1e-9)
    np.testing.assert_allclose(
        solution(x_upper),
        gamma_shape_dphi_by_differences(family, x_upper, upper=True),
        rtol=1e-9)


@pytest.mark.parametrize("family", GAMMAS + [Gamma(0.1, 1.0)], ids=repr)
def test_gamma_shape_matches_series_near_zero(family):
    """
    Near x = 0, where h is log-singular, phi' matches the series to 1e-11.
    """
    solution = solve_exact(Problem.from_score(family, "shape"))
    x_lower, _ = tail_points(family)
    np.testing.assert_allclose(solution(x_lower),
                               gamma_shape_dphi_by_series(family, x_lower),
                               rtol=1e-11)


def test_gauss_sin_matches_closed_form_and_quad():
    """
    A non-score h: phi' matches the complex-erfc formula and scipy quad.
    """
    family = Gaussian(0.0, 1.0)
    solution = solve_exact(Problem(family, np.sin, "gauss_sin"))
    for x in tail_points(family):
        np.testing.assert_allclose(solution(x), gauss_sin_dphi(x),
                                   rtol=1e-11, atol=1e-13)

    def integrand(y):
        return np.sin(y) * family.pdf(y)

    for x in [-6.3, -3.0, -1.0, -0.1, 0.5, 2.0, 5.0, 6.3]:
        if x <= 0:
            tail = integrate.quad(integrand, -np.inf, x,
                                  epsabs=0.0, epsrel=1e-13)[0]
        else:
            tail = -integrate.quad(integrand, x, np.inf,
                                   epsabs=0.0, epsrel=1e-13)[0]
        assert solution(x) == pytest.approx(tail / family.pdf(x), rel=1e-10)


@pytest.mark.parametrize("problem", [
    Problem(Gaussian(0.0, 1.0), np.sin, "gauss_sin"),
    Problem.from_score(Gamma(2.0, 1.0), "shape"),
], ids=lambda p: p.name)
def test_ode_residual_is_small(problem):
    """
    The flux p phi' satisfies (p phi')' = h p, by finite differences.
    """
    family = problem.family
    solution = solve_exact(problem)
    # includes points next to the median, where the two branches meet
    x = np.concatenate([family.ppf(np.linspace(1e-4, 1 - 1e-4, 201)),
                        family.ppf(0.5) + np.array([-1e-3, 0.0, 1e-3])])
    lower, _ = family.support()
    step = 1e-3 * np.minimum(family.std(), x - lower)

    def flux(y):
        return family.pdf(y) * solution(y)

    dflux = (-flux(x + 2 * step) + 8 * flux(x + step)
             - 8 * flux(x - step) + flux(x - 2 * step)) / (12 * step)
    rhs = problem.h(x) * family.pdf(x)
    assert np.max(np.abs(dflux - rhs)) < 1e-9 * np.max(np.abs(rhs))


def test_kink_in_h_is_resolved():
    """
    For h = |x - a| - E|X - a|, not smooth at a, phi' is still exact.
    """
    family = Gaussian(0.0, 1.0)
    a = 0.3
    c = 2 * family.pdf(a) + a * (2 * family.cdf(a) - 1)
    solution = solve_exact(Problem(family, lambda y: np.abs(y - a) - c,
                                   "gauss_abs"))
    x = np.concatenate([*tail_points(family), [0.29, 0.3, 0.31]])
    exact = np.where(x <= a,
                     (a - c) * family.cdf(x) + family.pdf(x),
                     (a + c) * family.sf(x) - family.pdf(x)) / family.pdf(x)
    np.testing.assert_allclose(solution(x), exact, rtol=1e-11)


def test_far_tail_beyond_the_mesh():
    """
    Beyond the quantile 1e-290 the slow quadrature path is still accurate.
    """
    family = Gaussian(0.0, 1.0)
    problem = Problem.from_score(family, "sigma")
    solution = solve_exact(problem)
    assert solution.info["edges_lower"][0] > -37.0
    assert solution.info["edges_upper"][0] < 37.0
    x = np.array([-37.0, -36.0, 36.0, 37.0])
    np.testing.assert_allclose(solution(x), problem.exact_dphi(x),
                               rtol=1e-10)


### ---------------------------------------------------------------------------
### Interface
### ---------------------------------------------------------------------------

def test_solution_metadata():
    """
    The solver returns a Solution with the agreed method, domain and info.
    """
    family = Gamma(2.0, 1.0)
    solution = solve_exact(Problem.from_score(family, "shape"))
    assert isinstance(solution, Solution)
    assert solution.method == "exact"
    assert solution.domain == family.support()
    info = solution.info
    assert abs(info["mean_h"]) < 1e-13
    assert info["centring_ratio"] < 1e-13
    assert abs(info["median_jump"]) < 1e-13
    assert info["median"] == pytest.approx(family.ppf(0.5))
    for side in ("lower", "upper"):
        assert info[f"error_estimate_{side}"] < 1e-11
        assert info[f"n_unresolved_{side}"] == 0
        assert info[f"edges_{side}"][-1] == info["median"]
    # the mesh covers the quantiles 1e-10 and 1 - 1e-10 with room to spare
    assert family.cdf(info["edges_lower"][0]) < 1e-100
    assert family.sf(info["edges_upper"][0]) < 1e-100


def test_vectorisation():
    """
    Scalars, unsorted arrays and 2D arrays give the same values.
    """
    family = Gamma(2.0, 1.0)
    solution = solve_exact(Problem.from_score(family, "shape"))
    rng = np.random.default_rng(0)
    x = family.ppf(rng.uniform(1e-6, 1 - 1e-6, size=24))
    assert np.any(np.diff(x) < 0)

    values = solution(x)
    assert values.shape == x.shape
    order = np.argsort(x)
    np.testing.assert_array_equal(solution(x[order]), values[order])

    grid = x.reshape(4, 6)
    assert solution(grid).shape == (4, 6)
    np.testing.assert_array_equal(solution(grid), values.reshape(4, 6))

    for xi, vi in zip(x[:5], values[:5]):
        scalar = solution(float(xi))
        assert np.ndim(scalar) == 0
        assert scalar == vi
        assert solution.dphi(float(xi)) == vi


def test_nan_outside_the_support():
    """
    Points outside the open support give nan and do not affect the others.
    """
    solution = solve_exact(Problem.from_score(Gamma(2.0, 1.0), "scale"))
    values = solution(np.array([-1.0, 0.0, 1.0, np.inf, np.nan, 3.0]))
    assert np.isnan(values[[0, 1, 3, 4]]).all()
    np.testing.assert_allclose(values[[2, 5]], [1.0, 3.0], rtol=1e-12)


def test_non_centred_h_raises():
    """
    A right-hand side with non-zero mean is rejected unless asked not to.
    """
    family = Gaussian(0.0, 1.0)
    problem = Problem(family, lambda x: x**2, "not_centred")
    with pytest.raises(ValueError, match="not centred"):
        solve_exact(problem)
    solution = solve_exact(problem, check_centred=False)
    assert solution.info["mean_h"] == pytest.approx(1.0, abs=1e-12)
    assert solution.info["mean_abs_h"] == pytest.approx(1.0, abs=1e-12)

    centred = Problem(family, lambda x: x**2 - 1.0, "centred")
    assert abs(solve_exact(centred).info["mean_h"]) < 1e-13


def test_speed():
    """
    Solving and evaluating at 4000 points takes well under five seconds.
    """
    family = Gamma(2.0, 1.0)
    a, b = family.domain(1e-6)
    x = np.linspace(a, b, 4000)
    start = time.perf_counter()
    solution = solve_exact(Problem.from_score(family, "shape"))
    values = solution(x)
    elapsed = time.perf_counter() - start
    assert np.all(np.isfinite(values))
    assert elapsed < 5.0
