"""
Tests of the finite-difference solver of the weighted Poisson equation.

The reference phi' is the elementary formula of the family where it exists
and otherwise the closed form (1/p) int h p, integrated from the nearer end
of the support with ``scipy.integrate.quad_vec``. Errors are relative L2(p)
errors of phi' on the solver's own domain [a, b].
"""

import functools

import numpy as np
import pytest
from scipy import integrate

from ot_1d.families import Gamma, Gaussian
from ot_1d.fd import solve_fd
from ot_1d.metrics import evaluation_grid, relative_l2p_error
from ot_1d.problem import Problem, Solution

CASES = ["gauss_mu", "gauss_sigma", "gauss_sin", "gamma_shape", "gamma_scale"]
INFORMATIVE = ["gauss_sin", "gamma_shape"]


### ---------------------------------------------------------------------------
### Problems and reference solution
### ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=None)
def _problem(case):
    """
    Build one of the five pilot problems.

    Parameters
    ----------
    case : str
        One of ``CASES``.

    Returns
    -------
    Problem
        The weighted Poisson problem.
    """
    if case == "gauss_sin":
        return Problem(Gaussian(0, 1), np.sin, "gauss_sin")
    family_name, param = case.split("_")
    family = Gaussian(0, 1) if family_name == "gauss" else Gamma(2, 1)
    return Problem.from_score(family, param, name=case)


def _closed_form_dphi(problem, x):
    """
    Closed form phi'(x) = (1/p(x)) int_{lower}^{x} h p by adaptive quadrature.

    Points below the median are integrated from the lower end of the
    support and the others from the upper end (using E_p[h] = 0), with the
    integrand divided by p(x) beforehand so that every point is resolved to
    the same relative accuracy.

    Parameters
    ----------
    problem : Problem
        The weighted Poisson problem.
    x : numpy.ndarray
        Evaluation points inside the support, of any shape.

    Returns
    -------
    numpy.ndarray
        Values of phi', same shape as ``x``.
    """
    family = problem.family
    x = np.asarray(x, dtype=float)
    points = x.ravel()
    logp = family.logpdf(points)
    below = points < family.ppf(0.5)
    lower, upper = family.support()
    out = np.empty_like(points)
    for mask, end, sign in ((below, lower, 1.0), (~below, upper, -1.0)):
        if not mask.any():
            continue
        xm, logpm = points[mask], logp[mask]

        def ratio(y, logpm=logpm):
            return problem.h(y) * np.exp(family.logpdf(y) - logpm)

        if np.isfinite(end):
            def integrand(s, xm=xm, end=end, ratio=ratio):
                return np.abs(xm - end) * ratio(end + (xm - end) * s)
            limits = (0.0, 1.0)
        else:
            def integrand(t, xm=xm, sign=sign, ratio=ratio):
                return ratio(xm - sign * t)
            limits = (0.0, np.inf)
        value, _ = integrate.quad_vec(integrand, *limits, epsabs=1e-13,
                                      epsrel=1e-12, norm="max", limit=2000)
        out[mask] = sign * value
    return out.reshape(x.shape)


def _reference_dphi(problem, x):
    """
    Reference phi': the elementary formula if any, else the closed form.

    Parameters
    ----------
    problem : Problem
        The weighted Poisson problem.
    x : numpy.ndarray
        Evaluation points inside the support, of any shape.

    Returns
    -------
    numpy.ndarray
        Values of phi', same shape as ``x``.
    """
    try:
        return problem.exact_dphi(x)
    except NotImplementedError:
        return _closed_form_dphi(problem, x)


@functools.lru_cache(maxsize=None)
def _grid(case, eps):
    """
    Evaluation grid and reference values on the quantile domain of a case.

    Parameters
    ----------
    case : str
        One of ``CASES``.
    eps : float
        Tail mass defining the domain [a, b].

    Returns
    -------
    x : numpy.ndarray
        Quadrature nodes in (a, b), length m.
    wp : numpy.ndarray
        Quadrature weights times the density, length m.
    truth : numpy.ndarray
        Reference phi' at the nodes, length m.
    """
    problem = _problem(case)
    a, b = problem.family.domain(eps)
    x, w = evaluation_grid(problem.family, a, b)
    return x, w * problem.family.pdf(x), _reference_dphi(problem, x)


def _error(case, n_nodes, eps=1e-6, bc="zero_flux"):
    """
    Relative L2(p) error of the FD phi' on its own domain.

    Parameters
    ----------
    case : str
        One of ``CASES``.
    n_nodes : int
        Number of grid nodes.
    eps : float, optional
        Tail mass of the domain truncation. Default is 1e-6.
    bc : str, optional
        Boundary condition of :func:`ot_1d.fd.solve_fd`. Default is
        ``"zero_flux"``.

    Returns
    -------
    float
        The relative L2(p) error over [a, b].
    """
    problem = _problem(case)
    x, wp, truth = _grid(case, eps)
    solution = solve_fd(
        problem, n_nodes, eps=eps, bc=bc,
        boundary_dphi=functools.partial(_reference_dphi, problem))
    return relative_l2p_error(solution(x), truth, wp)


def _orders(errors):
    """
    Observed convergence orders between successive grid doublings.

    Parameters
    ----------
    errors : sequence of float
        Errors at N, 2N, 4N, ..., length k.

    Returns
    -------
    numpy.ndarray
        Values log2(errors[j] / errors[j+1]), length k - 1.
    """
    errors = np.asarray(errors, dtype=float)
    return np.log2(errors[:-1] / errors[1:])


def test_closed_form_helper_matches_elementary_formulas():
    """
    The quadrature reference agrees with the exact phi' where one exists.
    """
    for case in ("gauss_mu", "gauss_sigma", "gamma_scale"):
        problem = _problem(case)
        x, _, truth = _grid(case, 1e-6)
        np.testing.assert_allclose(_closed_form_dphi(problem, x), truth,
                                   rtol=1e-10, atol=1e-12)


### ---------------------------------------------------------------------------
### Exact Neumann data: discretisation error only
### ---------------------------------------------------------------------------

@pytest.mark.parametrize("case", INFORMATIVE)
def test_exact_neumann_converges_at_second_order(case):
    """
    With exact boundary fluxes the error of phi' falls like dx^2.

    For ``gauss_sin`` the observed orders are 2.00. For ``gamma_shape`` at
    eps = 1e-6 they rise slowly towards 2 (about 1.76, 1.81, 1.87 here):
    the lower end a = 1.4e-3 is much smaller than dx, and the O(dx^2) flux
    error divided by p ~ x near 0 gives logarithmic factors.
    """
    errors = [_error(case, n, bc="exact_neumann")
              for n in (200, 400, 800, 1600)]
    orders = _orders(errors)
    assert np.all(orders > 1.7) and np.all(orders < 2.3), orders


@pytest.mark.parametrize("case", ["gamma_shape", "gamma_scale"])
def test_gamma_order_is_two_away_from_the_origin(case):
    """
    On a domain whose lower end is not near 0 the Gamma order is 2.

    With eps = 1e-2 the lower end is a = 0.149; this isolates the slow
    approach to order 2 at eps = 1e-6 as an effect of the end near x = 0.
    """
    errors = [_error(case, n, eps=1e-2, bc="exact_neumann")
              for n in (200, 400, 800, 1600)]
    orders = _orders(errors)
    assert np.all(orders > 1.9) and np.all(orders < 2.1), orders


@pytest.mark.parametrize("case, bound", [
    ("gauss_mu", 5e-6), ("gauss_sigma", 1e-5), ("gauss_sin", 5e-6),
    ("gamma_shape", 5e-4), ("gamma_scale", 1e-4)])
def test_exact_neumann_error_is_small_on_a_fine_grid(case, bound):
    """
    At N = 1600 the discretisation error is far below the truncation error.

    Observed: 2.1e-6, 3.7e-6, 2.2e-6 for the Gaussian cases, 1.6e-4 for
    ``gamma_shape`` and 2.6e-5 for ``gamma_scale``.
    """
    assert _error(case, 1600, bc="exact_neumann") < bound


### ---------------------------------------------------------------------------
### Zero flux: domain-truncation error
### ---------------------------------------------------------------------------

@pytest.mark.parametrize("case", CASES)
def test_zero_flux_error_decreases_with_eps(case):
    """
    On a fine grid the zero-flux error falls as the domain widens.

    The truncation error behaves like sqrt(eps): each factor 100 in eps
    gains about a factor 10 (observed 5.9 to 11.3 over the five cases).
    """
    errors = [_error(case, 1600, eps=eps) for eps in (1e-2, 1e-4, 1e-6)]
    ratios = np.array(errors[:-1]) / np.array(errors[1:])
    assert np.all(ratios > 4.0) and np.all(ratios < 25.0), (errors, ratios)


def test_zero_flux_truncation_error_matches_sqrt_two_eps():
    """
    For ``gauss_mu`` the zero-flux error at eps = 1e-6 is about sqrt(2 eps).

    Setting the flux to zero at a and b shifts the flux by its true end
    value p phi'; the resulting error of phi' is that shift divided by p,
    whose squared L2(p) norm is about eps phi'(a)^2 per end.
    """
    error = _error("gauss_mu", 1600, eps=1e-6)
    assert error == pytest.approx(np.sqrt(2e-6), rel=0.1)


@pytest.mark.parametrize("case", CASES)
def test_zero_flux_error_saturates_in_n(case):
    """
    At eps = 1e-6 refining the grid stops helping: truncation dominates.

    The error at N = 3200 is within 1% of the one at N = 1600, and far
    above the error of the exact-Neumann variant on the same grid.
    """
    coarse = _error(case, 1600)
    fine = _error(case, 3200)
    assert fine == pytest.approx(coarse, rel=1e-2)
    assert coarse > 5.0 * _error(case, 1600, bc="exact_neumann")


### ---------------------------------------------------------------------------
### Linear system
### ---------------------------------------------------------------------------

@pytest.mark.parametrize("bc", ["zero_flux", "exact_neumann"])
@pytest.mark.parametrize("case", CASES)
def test_discrete_equations_hold(case, bc):
    """
    The returned phi satisfies every flux balance, and h is recentred.

    The balances are recomputed here from ``info`` alone, in the form
    (F_{i+1/2} - F_{i-1/2}) / w_i = (h_i - c) p_i with w_i = dx in the
    interior and dx/2 at the two boundary nodes.
    """
    problem = _problem(case)
    family = problem.family
    solution = solve_fd(
        problem, 400, bc=bc,
        boundary_dphi=functools.partial(_reference_dphi, problem))
    info = solution.info
    x, phi, dx, c = info["x"], info["phi"], info["dx"], info[
        "recentring_constant"]

    assert info["residual_relative"] < 1e-13
    assert info["residual_norm"] < 1e-11
    assert abs(info["compatibility_defect"]) < 1e-13
    assert phi[info["pin"]] == 0.0

    a, b = solution.domain
    if bc == "zero_flux":
        flux_a, flux_b = 0.0, 0.0
    else:
        flux_a = family.pdf(a) * _reference_dphi(problem, np.array([a]))[0]
        flux_b = family.pdf(b) * _reference_dphi(problem, np.array([b]))[0]
    assert info["flux_a"] == pytest.approx(flux_a, abs=1e-15)
    assert info["flux_b"] == pytest.approx(flux_b, abs=1e-15)

    width = np.full(len(x), dx)
    width[[0, -1]] = dx / 2
    source = (problem.h(x) - c) * family.pdf(x)
    assert np.sum(source * width) == pytest.approx(flux_b - flux_a,
                                                   abs=1e-13)
    if bc == "zero_flux":
        mass = family.pdf(x) * width
        assert c == pytest.approx(np.sum(problem.h(x) * mass) / mass.sum(),
                                  abs=1e-13)

    half = 0.5 * (x[:-1] + x[1:])
    flux = np.concatenate([[flux_a], family.pdf(half) * np.diff(phi) / dx,
                           [flux_b]])
    np.testing.assert_allclose(np.diff(flux) / width, source, atol=1e-10)


### ---------------------------------------------------------------------------
### Solution contract
### ---------------------------------------------------------------------------

def test_solution_contract():
    """
    The Solution has the agreed fields, shapes and behaviour outside [a, b].
    """
    problem = _problem("gauss_sin")
    solution = solve_fd(problem, 50)
    a, b = solution.domain
    assert isinstance(solution, Solution)
    assert solution.method == "fd"
    assert (a, b) == problem.family.domain(1e-6)

    info = solution.info
    assert info["n_nodes"] == 50 and info["eps"] == 1e-6
    assert info["bc"] == "zero_flux"
    assert info["x"].shape == (50,) and info["phi"].shape == (50,)
    assert info["x"][0] == a and info["x"][-1] == b
    assert info["dx"] == pytest.approx((b - a) / 49)
    np.testing.assert_allclose(np.diff(info["x"]), info["dx"])
    for key in ("recentring_constant", "residual_norm"):
        assert isinstance(info[key], float)

    points = np.array([[a - 1.0, a, 0.0], [0.5, b, b + 1e-9]])
    values = solution(points)
    assert values.shape == points.shape
    assert np.isnan(values[0, 0]) and np.isnan(values[1, 2])
    assert np.all(np.isfinite(values.ravel()[1:5]))
    assert np.shape(solution(0.3)) == ()
    assert np.isnan(solution(np.inf)) and np.isnan(solution(np.nan))

    # between two edge midpoints phi' is the divided difference of phi
    x, phi = info["x"], info["phi"]
    mid = 0.5 * (x[10] + x[11])
    assert solution(mid) == pytest.approx((phi[11] - phi[10]) / info["dx"])


def test_end_values_come_from_the_boundary_flux():
    """
    At a and b the returned phi' is the prescribed flux divided by p.
    """
    problem = _problem("gamma_shape")
    reference = functools.partial(_reference_dphi, problem)
    zero = solve_fd(problem, 50)
    np.testing.assert_array_equal(zero(np.array(zero.domain)), 0.0)
    exact = solve_fd(problem, 50, bc="exact_neumann", boundary_dphi=reference)
    ends = np.array(exact.domain)
    np.testing.assert_allclose(exact(ends), reference(ends), rtol=1e-12)


def test_invalid_arguments_raise():
    """
    Missing Neumann data, an unknown bc and a one-node grid are rejected.
    """
    problem = _problem("gauss_mu")
    with pytest.raises(ValueError, match="boundary_dphi"):
        solve_fd(problem, 50, bc="exact_neumann")
    with pytest.raises(ValueError, match="unknown bc"):
        solve_fd(problem, 50, bc="dirichlet")
    with pytest.raises(ValueError, match="n_nodes"):
        solve_fd(problem, 1)
