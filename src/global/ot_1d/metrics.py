"""
Deterministic quadrature grids and the L2(p) error used to compare solvers.

All solvers are scored on the same grid: composite Gauss-Legendre nodes on an
interval [a, b], with panel edges that mix uniform spacing in x and uniform
spacing in probability, so both the bulk and the tails of p are resolved.
"""

import numpy as np

from .families import Family


### ---------------------------------------------------------------------------
### Quadrature grids
### ---------------------------------------------------------------------------

def gauss_legendre_grid(edges, order=8):
    """
    Composite Gauss-Legendre nodes and weights on consecutive panels.

    Parameters
    ----------
    edges : array_like
        Increasing panel edges, length m + 1.
    order : int, optional
        Number of Gauss-Legendre nodes per panel. Default is 8.

    Returns
    -------
    x : numpy.ndarray
        Nodes in increasing order, length m * order.
    w : numpy.ndarray
        Weights for the Lebesgue integral over [edges[0], edges[-1]],
        length m * order.
    """
    edges = np.asarray(edges, dtype=float)
    t, wt = np.polynomial.legendre.leggauss(order)
    half = 0.5 * np.diff(edges)
    mid = 0.5 * (edges[:-1] + edges[1:])
    x = (mid[:, None] + half[:, None] * t[None, :]).ravel()
    w = (half[:, None] * wt[None, :]).ravel()
    return x, w


def _dyadic_edges(end, neighbour, support_end):
    """
    Dyadic panel edges between an interval end and its neighbouring edge.

    Used where the support of p ends at a finite point, near which p or the
    integrand may have an algebraic or logarithmic singularity. The panels
    halve until they are as small as the distance to the end of the support.

    Parameters
    ----------
    end : float
        End of the integration interval (a or b).
    neighbour : float
        The panel edge next to ``end``.
    support_end : float
        End of the support of p on the same side, possibly infinite.

    Returns
    -------
    numpy.ndarray
        Extra edges strictly between ``end`` and ``neighbour``; empty when
        the support is unbounded on that side.
    """
    gap = abs(end - support_end)
    width = abs(neighbour - end)
    if not np.isfinite(gap) or width <= gap:
        return np.empty(0)
    if gap == 0.0:
        levels = 200
    else:
        levels = min(int(np.ceil(np.log2(width / gap))), 200)
    return end + (neighbour - end) * 0.5 ** np.arange(1, levels + 1)


def evaluation_grid(family, a, b, n_panels=400, order=8):
    """
    Quadrature grid on [a, b] adapted to the density of a family.

    Half of the panel edges are uniform in x and half are uniform in
    probability between F(a) and F(b). Where the support of p has a finite
    end, the end panel is refined dyadically towards it.

    Parameters
    ----------
    family : Family
        The density p.
    a : float
        Lower end of the interval, finite and inside the support.
    b : float
        Upper end of the interval, finite and inside the support.
    n_panels : int, optional
        Approximate number of panels before the dyadic refinement.
        Default is 400.
    order : int, optional
        Number of Gauss-Legendre nodes per panel. Default is 8.

    Returns
    -------
    x : numpy.ndarray
        Nodes in increasing order, strictly inside (a, b).
    w : numpy.ndarray
        Weights for the Lebesgue integral over [a, b], same length as
        ``x``. Multiply by ``family.pdf(x)`` for integrals against p.
    """
    m = max(n_panels // 2, 1)
    uniform = np.linspace(a, b, m + 1)
    probs = np.linspace(family.cdf(a), family.cdf(b), m + 1)
    quantile = np.clip(family.ppf(probs[1:-1]), a, b)
    edges = np.unique(np.concatenate([uniform, quantile]))
    lower, upper = family.support()
    edges = np.unique(np.concatenate([
        edges,
        _dyadic_edges(a, edges[1], lower),
        _dyadic_edges(b, edges[-2], upper)]))
    return gauss_legendre_grid(edges, order)


def expectation(family, f, tail=1e-13, n_panels=400, order=8):
    """
    Deterministic approximation of E_p[f(X)].

    Integrates over the quantile interval [F^{-1}(tail), F^{-1}(1 - tail)].

    Parameters
    ----------
    family : Family
        The density p.
    f : callable
        Maps a numpy.ndarray of points, length m, to an array whose first
        axis has length m (so vector- and matrix-valued f are allowed).
    tail : float, optional
        Probability mass left out in each tail. Default is 1e-13.
    n_panels : int, optional
        Approximate number of panels. Default is 400.
    order : int, optional
        Number of Gauss-Legendre nodes per panel. Default is 8.

    Returns
    -------
    float or numpy.ndarray
        The integral of f p, with the shape of one value of f.
    """
    a, b = family.domain(tail)
    x, w = evaluation_grid(family, a, b, n_panels, order)
    wp = w * family.pdf(x)
    return np.tensordot(wp, np.asarray(f(x)), axes=(0, 0))


### ---------------------------------------------------------------------------
### Errors
### ---------------------------------------------------------------------------

def l2p_norm(values, wp):
    """
    Discrete L2(p) norm of a function sampled on a quadrature grid.

    Parameters
    ----------
    values : numpy.ndarray
        Function values at the grid nodes, length m.
    wp : numpy.ndarray
        Quadrature weights times the density at the nodes, length m.

    Returns
    -------
    float
        The square root of sum(wp * values**2).
    """
    return float(np.sqrt(np.sum(wp * np.asarray(values) ** 2)))


def relative_l2p_error(estimate, truth, wp):
    """
    Relative L2(p) error between two functions sampled on the same grid.

    Parameters
    ----------
    estimate : numpy.ndarray
        Approximate values of phi' at the grid nodes, length m.
    truth : numpy.ndarray
        Exact values of phi' at the grid nodes, length m.
    wp : numpy.ndarray
        Quadrature weights times the density at the nodes, length m.

    Returns
    -------
    float
        ||estimate - truth|| / ||truth|| in the discrete L2(p) norm.
    """
    estimate = np.asarray(estimate, dtype=float)
    truth = np.asarray(truth, dtype=float)
    return l2p_norm(estimate - truth, wp) / l2p_norm(truth, wp)


def solution_error(solution, truth, family, a, b, n_panels=400, order=8):
    """
    Relative L2(p) error of a solver's phi' on [a, b].

    Convenience wrapper that builds the grid and evaluates both functions.
    In sweeps, build the grid once with :func:`evaluation_grid`, evaluate
    the truth once, and call :func:`relative_l2p_error` instead.

    Parameters
    ----------
    solution : callable
        Approximation of phi', e.g. a :class:`~ot_1d.problem.Solution`.
    truth : callable
        Exact phi'.
    family : Family
        The density p.
    a : float
        Lower end of the comparison interval.
    b : float
        Upper end of the comparison interval.
    n_panels : int, optional
        Approximate number of panels. Default is 400.
    order : int, optional
        Number of Gauss-Legendre nodes per panel. Default is 8.

    Returns
    -------
    float
        The relative L2(p) error over [a, b].
    """
    x, w = evaluation_grid(family, a, b, n_panels, order)
    wp = w * family.pdf(x)
    return relative_l2p_error(solution(x), truth(x), wp)
