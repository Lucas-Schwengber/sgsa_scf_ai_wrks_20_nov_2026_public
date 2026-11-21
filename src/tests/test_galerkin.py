"""
Tests of the Galerkin solver and of its Hermite basis.
"""

from functools import lru_cache

import numpy as np
import pytest
from scipy import integrate

from ot_1d.families import Gamma, Gaussian
from ot_1d.galerkin import HermiteBasis, solve_galerkin
from ot_1d.metrics import evaluation_grid, expectation, relative_l2p_error
from ot_1d.problem import Problem

PROBLEMS = {
    "gauss_mu": Problem.from_score(Gaussian(0.0, 1.0), "mu"),
    "gauss_sigma": Problem.from_score(Gaussian(0.0, 1.0), "sigma"),
    "gauss_sin": Problem(Gaussian(0.0, 1.0), np.sin, "gauss_sin"),
    "gamma_shape": Problem.from_score(Gamma(2.0, 1.0), "shape"),
    "gamma_scale": Problem.from_score(Gamma(2.0, 1.0), "scale"),
}

# Tail mass for the quadratures of the basis tests: products of two basis
# functions of degree 8 still have visible mass beyond the default 1e-13.
TAIL = 1e-40


### ---------------------------------------------------------------------------
### Helpers
### ---------------------------------------------------------------------------

def _reference_dphi(problem, x):
    """
    Closed-form phi'(x) = (1/p(x)) int_{lower}^{x} h p, by adaptive quadrature.

    Each integral starts from the nearer tail, at the point holding 1e-20 of
    the tail mass of its end point, and is divided by p(x) inside the
    integrand, so the absolute tolerance applies to phi' itself.

    Parameters
    ----------
    problem : Problem
        The weighted Poisson problem.
    x : array_like
        Evaluation points in the interior of the support, length m.

    Returns
    -------
    numpy.ndarray
        Values of phi'(x), length m.
    """
    family = problem.family
    x = np.asarray(x, dtype=float)
    start = np.where(family.cdf(x) <= 0.5,
                     family.ppf(family.cdf(x) * 1e-20),
                     family.isf(family.sf(x) * 1e-20))
    px = family.pdf(x)

    def integrand(t):
        y = start + t * (x - start)
        return (x - start) * problem.h(y) * family.pdf(y) / px

    value, _ = integrate.quad_vec(integrand, 0.0, 1.0,
                                  epsabs=1e-12, epsrel=1e-12)
    return value


@lru_cache(maxsize=None)
def _case(name):
    """
    Problem, evaluation grid and exact phi' for one of the pilot cases.

    The grid is the shared evaluation grid on ``family.domain(1e-6)``.

    Parameters
    ----------
    name : str
        Key of ``PROBLEMS``.

    Returns
    -------
    problem : Problem
        The problem.
    x : numpy.ndarray
        Grid nodes, length m.
    wp : numpy.ndarray
        Quadrature weights times the density at the nodes, length m.
    truth : numpy.ndarray
        Exact phi' at the nodes, length m.
    """
    problem = PROBLEMS[name]
    family = problem.family
    a, b = family.domain(1e-6)
    x, w = evaluation_grid(family, a, b)
    wp = w * family.pdf(x)
    try:
        truth = problem.exact_dphi(x)
    except NotImplementedError:
        truth = _reference_dphi(problem, x)
    return problem, x, wp, truth


def _error(solution, name):
    """
    Relative L2(p) error of a solution on the grid of a pilot case.

    Parameters
    ----------
    solution : Solution
        Output of the solver.
    name : str
        Key of ``PROBLEMS``.

    Returns
    -------
    float
        The relative L2(p) error of phi' on ``family.domain(1e-6)``.
    """
    _, x, wp, truth = _case(name)
    return relative_l2p_error(solution(x), truth, wp)


def _median_error(name, degree, n, seeds=20, **kwargs):
    """
    Median Monte Carlo error of the Hermite Galerkin solver over seeds.

    Parameters
    ----------
    name : str
        Key of ``PROBLEMS``.
    degree : int
        Degree K of the Hermite basis.
    n : int
        Number of draws.
    seeds : int, optional
        Number of replications, seeded 0 to ``seeds - 1``. Default is 20.
    **kwargs
        Passed to :func:`solve_galerkin`.

    Returns
    -------
    float
        Median over the seeds of the relative L2(p) error.
    """
    problem = PROBLEMS[name]
    errors = [
        _error(solve_galerkin(problem, HermiteBasis(degree), n=n,
                              rng=np.random.default_rng(seed), **kwargs),
               name)
        for seed in range(seeds)]
    return float(np.median(errors))


class MonomialBasis:
    """
    Monomials z, z^2, ..., z^K in the standardised variable.

    Spans the same polynomials as :class:`HermiteBasis` up to additive
    constants; used to test that the solver accepts any basis object.

    Attributes
    ----------
    size : int
        Number of basis functions K.
    loc : float
        Location of the standardisation.
    scale : float
        Scale of the standardisation.
    """

    def __init__(self, degree):
        """
        Initialize the basis with the identity standardisation z = x.

        Parameters
        ----------
        degree : int
            Highest degree K.
        """
        self.size = degree
        self.loc = 0.0
        self.scale = 1.0

    def standardise(self, loc, scale):
        """
        Set the standardised variable z = (x - loc) / scale.

        Parameters
        ----------
        loc : float
            Location.
        scale : float
            Scale, positive.

        Returns
        -------
        self : MonomialBasis
            The basis itself.
        """
        self.loc, self.scale = float(loc), float(scale)
        return self

    def fit(self, x):
        """
        Standardise with the sample mean and standard deviation of draws.

        Parameters
        ----------
        x : array_like
            Draws, length n.

        Returns
        -------
        self : MonomialBasis
            The basis itself.
        """
        return self.standardise(np.mean(x), np.std(x))

    def psi(self, x):
        """
        Evaluate the monomials.

        Parameters
        ----------
        x : array_like
            Evaluation points, length m.

        Returns
        -------
        numpy.ndarray
            Array of shape (m, K) whose column k - 1 holds z^k.
        """
        z = (np.asarray(x, dtype=float).ravel() - self.loc) / self.scale
        return z[:, None] ** np.arange(1, self.size + 1)

    def dpsi(self, x):
        """
        Evaluate the x-derivatives of the monomials.

        Parameters
        ----------
        x : array_like
            Evaluation points, length m.

        Returns
        -------
        numpy.ndarray
            Array of shape (m, K) whose column k - 1 holds k z^(k-1) / scale.
        """
        z = (np.asarray(x, dtype=float).ravel() - self.loc) / self.scale
        k = np.arange(1, self.size + 1)
        return k * z[:, None] ** (k - 1) / self.scale


def test_reference_helper_matches_known_solutions():
    """
    The quadrature helper agrees with the exact formulas and CDF differences.
    """
    for name in ("gauss_mu", "gauss_sigma", "gamma_scale"):
        problem, x, _, truth = _case(name)
        np.testing.assert_allclose(_reference_dphi(problem, x), truth,
                                   rtol=0, atol=1e-10)

    # gamma_shape: phi' = -dF/d(shape) / p, by a central difference in shape
    problem, x, _, truth = _case("gamma_shape")
    family, step = problem.family, 1e-3

    def cdf(shift):
        return family.with_params(shape=2.0 + shift).cdf(x)

    dcdf = (-cdf(2 * step) + 8 * cdf(step)
            - 8 * cdf(-step) + cdf(-2 * step)) / (12 * step)
    np.testing.assert_allclose(truth, -dcdf / family.pdf(x),
                               rtol=1e-5, atol=1e-6)


### ---------------------------------------------------------------------------
### Basis
### ---------------------------------------------------------------------------

def test_hermite_shapes_and_low_degrees():
    """
    psi and dpsi have shape (m, K) and start with z, (z^2-1)/sqrt(2), ...
    """
    basis = HermiteBasis(5)
    z = np.linspace(-2.0, 2.0, 7)
    psi, dpsi = basis.psi(z), basis.dpsi(z)
    assert basis.size == 5 and basis.degree == 5
    assert psi.shape == (7, 5) and dpsi.shape == (7, 5)
    assert HermiteBasis(1).psi(z).shape == (7, 1)
    assert basis.psi(0.3).shape == (1, 5)
    np.testing.assert_allclose(psi[:, 0], z)
    np.testing.assert_allclose(psi[:, 1], (z**2 - 1) / np.sqrt(2))
    np.testing.assert_allclose(psi[:, 2], (z**3 - 3 * z) / np.sqrt(6))
    np.testing.assert_allclose(dpsi[:, 0], np.ones_like(z))
    np.testing.assert_allclose(dpsi[:, 1], np.sqrt(2) * z)
    with pytest.raises(ValueError):
        HermiteBasis(0)


@pytest.mark.parametrize("loc, scale", [(0.0, 1.0), (1.5, 0.7)])
def test_hermite_orthonormal_under_matching_gaussian(loc, scale):
    """
    The basis is centred and orthonormal under N(loc, scale^2).
    """
    basis = HermiteBasis(8).standardise(loc, scale)
    family = Gaussian(loc, scale)

    def gram(x):
        psi = basis.psi(x)
        return psi[:, :, None] * psi[:, None, :]

    np.testing.assert_allclose(expectation(family, gram, tail=TAIL),
                               np.eye(8), atol=1e-10)
    np.testing.assert_allclose(expectation(family, basis.psi, tail=TAIL),
                               np.zeros(8), atol=1e-10)


def test_hermite_dpsi_matches_finite_differences():
    """
    dpsi is the x-derivative of psi, including the 1/scale of the chain rule.
    """
    basis = HermiteBasis(7).standardise(0.4, 1.8)
    x = np.linspace(-3.0, 4.0, 15)
    step = 1e-5
    numerical = (basis.psi(x + step) - basis.psi(x - step)) / (2 * step)
    np.testing.assert_allclose(basis.dpsi(x), numerical, rtol=1e-7, atol=1e-7)


def test_standardise_and_fit():
    """
    standardise evaluates the basis at z = (x - loc)/scale; fit uses draws.
    """
    plain = HermiteBasis(4)
    basis = HermiteBasis(4)
    assert (basis.loc, basis.scale) == (0.0, 1.0)
    assert basis.standardise(2.0, 3.0) is basis
    assert (basis.loc, basis.scale) == (2.0, 3.0)

    x = np.linspace(-4.0, 9.0, 11)
    z = (x - 2.0) / 3.0
    np.testing.assert_allclose(basis.psi(x), plain.psi(z))
    np.testing.assert_allclose(basis.dpsi(x), plain.dpsi(z) / 3.0)
    assert not np.allclose(basis.psi(x), plain.psi(x))

    draws = np.random.default_rng(0).gamma(2.0, size=500)
    assert basis.fit(draws) is basis
    assert basis.loc == pytest.approx(np.mean(draws))
    assert basis.scale == pytest.approx(np.std(draws))
    # the empirical measure is standardised, so psi_1, psi_2 average to zero
    np.testing.assert_allclose(basis.psi(draws)[:, :2].mean(axis=0),
                               [0.0, 0.0], atol=1e-12)

    with pytest.raises(ValueError):
        basis.standardise(0.0, 0.0)


### ---------------------------------------------------------------------------
### Deterministic reference mode
### ---------------------------------------------------------------------------

# The Hermite basis is not orthogonal under the Gamma density and cond(A)
# grows fast with K there (about 1e8 at K = 8, 1e15 at K = 12), so the exact
# recovery of gamma_scale is only asked up to K = 8; see
# test_reference_conditioning.
EXACT_CASES = (
    [("gauss_mu", K) for K in (1, 2, 3, 4, 6, 8, 12)]
    + [("gauss_sigma", K) for K in (2, 3, 4, 6, 8, 12)]
    + [("gamma_scale", K) for K in (2, 3, 4, 6, 8)])


@pytest.mark.parametrize("name, degree", EXACT_CASES)
def test_reference_recovers_linear_solutions(name, degree):
    """
    With phi in the span, the deterministic mode gives the exact phi'.
    """
    problem = PROBLEMS[name]
    solution = solve_galerkin(problem, HermiteBasis(degree))
    assert _error(solution, name) < 1e-8
    assert solution.method == "galerkin"
    assert solution.domain == problem.family.support()
    assert solution.info["n"] is None
    assert solution.info["degree"] == degree
    assert solution.info["rank"] == degree
    assert solution.info["coef"].shape == (degree,)
    assert solution.info["loc"] == pytest.approx(problem.family.mean())
    assert solution.info["scale"] == pytest.approx(problem.family.std())


def test_reference_system_for_standard_gaussian():
    """
    Under N(0, 1), A = diag(1, ..., K) and gauss_mu has phi = psi_1.
    """
    degree = 8
    solution = solve_galerkin(PROBLEMS["gauss_mu"], HermiteBasis(degree))
    info = solution.info
    np.testing.assert_allclose(info["A"], np.diag(np.arange(1.0, degree + 1)),
                               atol=1e-9)
    assert info["cond"] == pytest.approx(degree)
    np.testing.assert_allclose(info["coef"], np.eye(degree)[0], atol=1e-10)
    assert abs(info["h_mean"]) < 1e-12


def test_reference_needs_degree_two_for_linear_dphi():
    """
    At K = 1 phi' is a constant, so a linear exact phi' is missed.
    """
    for name in ("gauss_sigma", "gamma_scale"):
        solution = solve_galerkin(PROBLEMS[name], HermiteBasis(1))
        assert _error(solution, name) > 0.5


def test_reference_error_decreases_with_degree_gauss_sin():
    """
    For gauss_sin the basis error falls fast along odd K; even K adds nothing.
    """
    problem = PROBLEMS["gauss_sin"]

    def error(degree):
        return _error(solve_galerkin(problem, HermiteBasis(degree)),
                      "gauss_sin")

    # phi is odd, so psi_K with K even has a zero coefficient
    errors = [error(K) for K in (1, 3, 5, 7, 9, 11)]
    assert all(e1 < 0.5 * e0 for e0, e1 in zip(errors, errors[1:]))
    assert errors[-1] < 1e-5
    for K in (2, 4, 8):
        assert error(K) == pytest.approx(error(K - 1), rel=1e-8)


def test_reference_error_decreases_with_degree_gamma_shape():
    """
    For gamma_shape the basis error falls with K, at an algebraic rate.
    """
    problem = PROBLEMS["gamma_shape"]
    errors = [_error(solve_galerkin(problem, HermiteBasis(K)), "gamma_shape")
              for K in (1, 2, 3, 4, 6, 8)]
    assert all(e1 < 0.8 * e0 for e0, e1 in zip(errors, errors[1:]))
    assert errors[0] > 0.3 and errors[-1] < 0.01


def test_reference_conditioning():
    """
    cond(A) is K under the Gaussian and grows fast with K under the Gamma.
    """
    for K in (4, 12):
        info = solve_galerkin(PROBLEMS["gauss_sin"], HermiteBasis(K)).info
        assert info["cond"] == pytest.approx(K, rel=1e-6)
    conds = [solve_galerkin(PROBLEMS["gamma_shape"], HermiteBasis(K)).info
             ["cond"] for K in (2, 4, 8, 12)]
    assert all(c1 > 10 * c0 for c0, c1 in zip(conds, conds[1:]))
    assert conds[2] > 1e6 and conds[3] > 1e12
    # ill-conditioned but still usable at K = 12: no blow-up of the error
    solution = solve_galerkin(PROBLEMS["gamma_scale"], HermiteBasis(12))
    assert _error(solution, "gamma_scale") < 1e-2


def test_reference_ignores_centre_h():
    """
    centre_h has no effect in the deterministic mode.
    """
    problem = PROBLEMS["gamma_shape"]
    plain = solve_galerkin(problem, HermiteBasis(4))
    centred = solve_galerkin(problem, HermiteBasis(4), centre_h=True)
    np.testing.assert_array_equal(plain.info["coef"], centred.info["coef"])
    assert centred.info["centre_h"] is False


### ---------------------------------------------------------------------------
### Monte Carlo mode
### ---------------------------------------------------------------------------

def test_monte_carlo_is_reproducible():
    """
    A seeded generator fixes the solution; passing its draws gives the same.
    """
    problem = PROBLEMS["gamma_shape"]

    def solve(seed):
        return solve_galerkin(problem, HermiteBasis(4), n=500,
                              rng=np.random.default_rng(seed))

    first, again, other = solve(3), solve(3), solve(4)
    np.testing.assert_array_equal(first.info["coef"], again.info["coef"])
    assert not np.allclose(first.info["coef"], other.info["coef"])

    draws = problem.family.sample(500, np.random.default_rng(3))
    given = solve_galerkin(problem, HermiteBasis(4), samples=draws)
    np.testing.assert_array_equal(first.info["coef"], given.info["coef"])
    # samples take precedence over n
    given = solve_galerkin(problem, HermiteBasis(4), n=7, samples=draws)
    assert given.info["n"] == 500


def test_monte_carlo_system_and_info():
    """
    A, b, loc and scale are the sample averages of the same draws.
    """
    problem = PROBLEMS["gamma_shape"]
    draws = problem.family.sample(400, np.random.default_rng(1))
    basis = HermiteBasis(5)
    solution = solve_galerkin(problem, basis, samples=draws)
    info = solution.info

    # the caller's basis is left untouched
    assert (basis.loc, basis.scale) == (0.0, 1.0)

    fitted = HermiteBasis(5).fit(draws)
    dpsi, psi = fitted.dpsi(draws), fitted.psi(draws)
    A = np.einsum("ij,ik->jk", dpsi, dpsi) / 400
    b = -np.mean(problem.h(draws)[:, None] * psi, axis=0)
    np.testing.assert_allclose(info["A"], A, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(info["b"], b, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(info["coef"],
                               np.linalg.lstsq(A, b, rcond=None)[0],
                               rtol=1e-6)
    assert info["n"] == 400 and info["degree"] == 5 and info["rank"] == 5
    assert info["loc"] == pytest.approx(np.mean(draws))
    assert info["scale"] == pytest.approx(np.std(draws))
    assert info["cond"] == pytest.approx(np.linalg.cond(A), rel=1e-6)
    assert info["h_mean"] == pytest.approx(np.mean(problem.h(draws)))
    assert info["centre_h"] is False

    x = np.linspace(0.1, 8.0, 9)
    np.testing.assert_allclose(solution(x), fitted.dpsi(x) @ info["coef"])


def test_dphi_preserves_shape_and_is_nan_outside_support():
    """
    dphi returns the input shape, with nan outside the support of p.
    """
    problem = PROBLEMS["gamma_scale"]
    solution = solve_galerkin(problem, HermiteBasis(3), n=200,
                              rng=np.random.default_rng(0))
    x = np.array([[-1.0, 0.5, 1.0], [2.0, 3.0, 4.0]])
    values = solution(x)
    assert values.shape == (2, 3)
    assert np.isnan(values[0, 0]) and np.all(np.isfinite(values.ravel()[1:]))
    np.testing.assert_allclose(solution(x[1]), values[1])
    assert solution(2.0).shape == ()
    assert float(solution(2.0)) == pytest.approx(values[1, 0])


@pytest.mark.parametrize("name", ["gauss_sigma", "gamma_scale"])
def test_monte_carlo_error_scales_like_root_n(name):
    """
    With phi in the span, the median error falls by 10 from n=1e3 to 1e5.
    """
    coarse = _median_error(name, 2, 1_000)
    fine = _median_error(name, 2, 100_000)
    assert 5.0 < coarse / fine < 20.0
    assert fine < 0.03


def test_monte_carlo_error_approaches_reference_gauss_sin():
    """
    For gauss_sin the Monte Carlo error tends to the basis error as n grows.
    """
    degree = 3
    reference = _error(
        solve_galerkin(PROBLEMS["gauss_sin"], HermiteBasis(degree)),
        "gauss_sin")
    gaps = [abs(_median_error("gauss_sin", degree, n) - reference)
            for n in (1_000, 10_000, 100_000)]
    assert gaps[0] > gaps[1] > gaps[2]
    assert gaps[2] < 0.05 * reference


def test_monte_carlo_is_unstable_at_high_degree_and_small_n():
    """
    At n = 100 the error and cond(A) blow up with K: expected, not hidden.
    """
    problem = PROBLEMS["gauss_sin"]
    low = _median_error("gauss_sin", 3, 100)
    high = _median_error("gauss_sin", 12, 100)
    assert low < 0.5
    assert high > 100 * low

    draws = problem.family.sample(100, np.random.default_rng(0))
    cond_low = solve_galerkin(problem, HermiteBasis(3),
                              samples=draws).info["cond"]
    cond_high = solve_galerkin(problem, HermiteBasis(12),
                               samples=draws).info["cond"]
    # the exact A has cond 3 and 12
    assert cond_low < 10 and cond_high > 1e4


### ---------------------------------------------------------------------------
### Injectable basis and centring of h
### ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["gauss_sin", "gamma_shape"])
def test_monomial_basis_gives_the_same_solution(name):
    """
    Monomials and Hermite polynomials give the same phi' once h is centred.

    The two bases span the same polynomials only up to additive constants,
    and b = -mean(h psi) sees those constants through the sample mean of h.
    So the solutions agree to round-off in the deterministic mode (E[h] = 0)
    and with ``centre_h=True``, but not with the plain b of the default.
    """
    problem, x, _, _ = _case(name)
    draws = problem.family.sample(1_000, np.random.default_rng(0))

    hermite = solve_galerkin(problem, HermiteBasis(4), samples=draws,
                             centre_h=True)
    monomial = solve_galerkin(problem, MonomialBasis(4), samples=draws,
                              centre_h=True)
    assert monomial.info["degree"] == 4
    np.testing.assert_allclose(monomial(x), hermite(x), rtol=1e-9, atol=1e-9)

    hermite = solve_galerkin(problem, HermiteBasis(4))
    monomial = solve_galerkin(problem, MonomialBasis(4))
    np.testing.assert_allclose(monomial(x), hermite(x), rtol=1e-9, atol=1e-9)

    hermite = solve_galerkin(problem, HermiteBasis(4), samples=draws)
    monomial = solve_galerkin(problem, MonomialBasis(4), samples=draws)
    gap = np.max(np.abs(monomial(x) - hermite(x)))
    h_mean = abs(hermite.info["h_mean"])
    assert 1e-3 * h_mean < gap < 1e3 * h_mean


@pytest.mark.parametrize("basis_class", [HermiteBasis, MonomialBasis])
def test_centre_h_changes_b_through_the_mean_of_h(basis_class):
    """
    Centring leaves A alone and shifts b by mean(h) times mean(psi).
    """
    basis = basis_class(5)
    problem = PROBLEMS["gamma_shape"]
    draws = problem.family.sample(300, np.random.default_rng(5))
    plain = solve_galerkin(problem, basis, samples=draws)
    centred = solve_galerkin(problem, basis, samples=draws, centre_h=True)
    assert centred.info["centre_h"] is True

    h_mean = np.mean(problem.h(draws))
    assert abs(h_mean) > 1e-4
    assert centred.info["h_mean"] == pytest.approx(h_mean)
    np.testing.assert_array_equal(plain.info["A"], centred.info["A"])

    psi_mean = basis.fit(draws).psi(draws).mean(axis=0)
    shift = centred.info["b"] - plain.info["b"]
    np.testing.assert_allclose(shift, h_mean * psi_mean,
                               rtol=1e-9, atol=1e-12)
    if basis_class is HermiteBasis:
        # psi_1 and psi_2 have sample mean zero after fit
        np.testing.assert_allclose(shift[:2], [0.0, 0.0], atol=1e-12)
        assert np.max(np.abs(shift[2:])) > 1e-6
    assert np.all(np.isfinite(centred(draws)))
