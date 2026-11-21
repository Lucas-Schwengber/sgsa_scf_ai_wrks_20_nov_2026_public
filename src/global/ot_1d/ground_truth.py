"""
Exact solver: the closed form of the weighted Poisson equation by quadrature.

For a density p with CDF F and a function h with E_p[h] = 0, the solution of
(p phi')' = h p with zero flux at the ends of the support is

    phi'(x) = (1/p(x)) * int_{lower}^{x} h p    where F(x) <= 0.5,
    phi'(x) = -(1/p(x)) * int_{x}^{upper} h p   where F(x) > 0.5,

so the integral always starts from the nearer end of the support and both
factors of the quotient keep their relative accuracy in the tails.

Algorithm. On each side of the median, :func:`solve_exact` builds once a mesh
whose edges are the quantiles 2^-1, 2^-2, ..., down to about 1e-290, so the
mass of p halves from one cell to the next towards the tail. Each cell is
integrated with a 20-point Gauss-Legendre rule and bisected until the rule on
the cell agrees with the rule on its two halves. The cell integrals are summed
from the tail inwards (increasing magnitude), which gives the integral from
the end of the support to every mesh edge. To evaluate phi' at a point, one
more 20-point rule integrates from the mesh edge on the tail side of the point
to the point itself. All points are handled at once with array operations, and
the value at a point does not depend on the other points of the call.

Accuracy. Errors are controlled relative to the integral of ``|h| p`` from
the nearer end of the support, so phi' has small relative error wherever it
is not much smaller than that integral divided by p (it loses relative
accuracy only next to its own zeros). For the Gaussian and Gamma families the
measured relative error is below 1e-13 between the quantiles 1e-10 and
1 - 1e-10.

Limits. h should be smooth inside the support. A kink of h is resolved by
bisection; a jump is too, but it can go undetected when it falls between the
quadrature nodes. Next to a finite non-zero end of the support (a shifted
Gamma, say) the distance to the end is not resolved by floating point, and
accuracy is lost there whatever the quadrature.
"""

import warnings

import numpy as np
from scipy import integrate

from .problem import Solution

_ORDER = 20
_NODES, _WEIGHTS = np.polynomial.legendre.leggauss(_ORDER)

# The mesh edges are the quantiles 2^-k for k = 1, ..., _N_LEVELS (2^-963 is
# about 1.3e-290).
_N_LEVELS = 963
# Cells are bisected at most this many times.
_MAX_DEPTH = 60
# Above this number of cells waiting for refinement, all of them are accepted.
_MAX_PENDING = 20000
# A cell whose error estimate stopped decreasing under bisection is accepted
# as rounding-limited when the estimate is below this fraction of its integral
# of |h| p.
_NOISE_REL = 1e-8
# The mesh stops where an edge is closer than _TINY, or than _MIN_GAP_ULPS
# floating-point spacings, to a finite end of the support, or larger than
# 1 / _TINY in absolute value.
_TINY = 1e-280
_MIN_GAP_ULPS = 1e8
# |E_p[h]| / E_p[|h|] above which h is declared not centred.
_CENTRED_TOL = 1e-8


### ---------------------------------------------------------------------------
### Quadrature on cells
### ---------------------------------------------------------------------------

def _gauss_legendre(f, a, b):
    """
    Gauss-Legendre integrals of a function over many intervals at once.

    Parameters
    ----------
    f : callable
        Integrand: maps a numpy.ndarray of points, length k, to an array of
        length k.
    a : numpy.ndarray
        One end of each interval, length m.
    b : numpy.ndarray
        Other end of each interval, length m. May be smaller than ``a``; the
        integral is always taken from the smaller to the larger end.

    Returns
    -------
    integral : numpy.ndarray
        Approximation of the integral of f over each interval, length m.
    abs_integral : numpy.ndarray
        Approximation of the integral of ``|f|`` over each interval,
        length m.
    """
    mid = 0.5 * (a + b)
    half = 0.5 * (b - a)
    y = mid[:, None] + half[:, None] * _NODES[None, :]
    values = f(y.ravel()).reshape(y.shape)
    w = np.abs(half)[:, None] * _WEIGHTS[None, :]
    return np.sum(w * values, axis=1), np.sum(w * np.abs(values), axis=1)


def _refine(f, edges, tol):
    """
    Adaptive Gauss-Legendre integration over consecutive cells.

    Every cell is compared with its two halves. It is accepted, and replaced
    by its halves, when the two estimates agree; otherwise it is bisected and
    the halves are tested in turn. The tolerance of a cell is ``tol`` times
    the larger of its own integral of ``|f|`` and its share (by width) of the
    integral of ``|f|`` from ``edges[0]`` to the end of the initial cell that
    contains it.

    Two more rules stop the bisection. A cell is accepted as
    rounding-limited when its error estimate, relative to its integral of
    ``|f|``, is below ``_NOISE_REL`` and did not fall by a factor of four
    from its parent. A cell is accepted as unresolved when it cannot be
    bisected (no floating-point number between its ends, or a non-finite
    estimate), after ``_MAX_DEPTH`` bisections, or when more than
    ``_MAX_PENDING`` cells are waiting.

    Parameters
    ----------
    f : callable
        Integrand: maps a numpy.ndarray of points, length k, to an array of
        length k.
    edges : numpy.ndarray
        Strictly monotone initial cell edges, length m + 1 with m >= 1,
        ordered from the tail towards the median.
    tol : float
        Relative tolerance.

    Returns
    -------
    new_edges : numpy.ndarray
        Edges of the refined mesh, length c + 1, in the same order as
        ``edges`` and with the same first and last values.
    integral : numpy.ndarray
        Integral of f over each refined cell (from its smaller to its larger
        end), length c.
    abs_integral : numpy.ndarray
        Integral of ``|f|`` over each refined cell, length c.
    error : numpy.ndarray
        Error estimate of each refined cell, length c.
    n_noise : int
        Number of cells accepted as rounding-limited.
    n_unresolved : int
        Number of cells accepted without meeting any criterion (bisection
        exhausted, as at a jump of f).
    """
    a, b = edges[:-1].copy(), edges[1:].copy()
    frac = np.ones(a.size)
    parent_rel = np.full(a.size, np.inf)
    ref = None
    done = []
    n_noise = 0
    n_unresolved = 0
    for depth in range(_MAX_DEPTH + 1):
        mid = 0.5 * (a + b)
        whole, _ = _gauss_legendre(f, a, b)
        left, abs_left = _gauss_legendre(f, a, mid)
        right, abs_right = _gauss_legendre(f, mid, b)
        cell_abs = abs_left + abs_right
        with np.errstate(all="ignore"):
            err = np.abs(whole - (left + right))
            if ref is None:
                ref = np.cumsum(cell_abs)
            rel = np.where(cell_abs > 0, err / cell_abs, 0.0)
            converged = err <= tol * np.maximum(cell_abs, ref * frac)
        noise = (~converged & (depth >= 1) & (rel <= _NOISE_REL)
                 & (rel > 0.25 * parent_rel))
        stuck = (mid == a) | (mid == b) | ~np.isfinite(err)
        if depth == _MAX_DEPTH or a.size > _MAX_PENDING:
            stuck = np.ones(a.size, dtype=bool)
        stuck &= ~converged & ~noise
        accept = converged | noise | stuck
        n_noise += int(np.sum(noise))
        n_unresolved += int(np.sum(stuck))
        done.append((np.concatenate([a[accept], mid[accept]]),
                     np.concatenate([mid[accept], b[accept]]),
                     np.concatenate([left[accept], right[accept]]),
                     np.concatenate([abs_left[accept], abs_right[accept]]),
                     np.tile(0.5 * err[accept], 2)))
        split = ~accept
        if not split.any():
            break
        a, b = (np.concatenate([a[split], mid[split]]),
                np.concatenate([mid[split], b[split]]))
        frac = np.tile(0.5 * frac[split], 2)
        ref = np.tile(ref[split], 2)
        parent_rel = np.tile(rel[split], 2)

    a, b, integral, abs_integral, error = (
        np.concatenate(parts) for parts in zip(*done))
    keep = a != b
    a, b, integral, abs_integral, error = (
        arr[keep] for arr in (a, b, integral, abs_integral, error))
    direction = 1.0 if edges[-1] > edges[0] else -1.0
    order = np.argsort(direction * a, kind="stable")
    new_edges = np.concatenate([a[order][:1], b[order]])
    return (new_edges, integral[order], abs_integral[order], error[order],
            n_noise, n_unresolved)


### ---------------------------------------------------------------------------
### Integral from one end of the support
### ---------------------------------------------------------------------------

class _TailIntegral:
    """
    Integral of f = h p between one end of the support and a point.

    For the lower side this is T(x) = int_{lower}^{x} f, for the upper side
    T(x) = int_{x}^{upper} f. It is tabulated at the edges of an adaptive
    mesh between a far quantile and the median, and completed at a point by
    one Gauss-Legendre rule from the neighbouring edge.

    Attributes
    ----------
    sign : float
        ``1.0`` for the lower side, ``-1.0`` for the upper side.
    edges : numpy.ndarray
        Mesh edges ordered from the tail to the median, length c + 1.
    values : numpy.ndarray
        T at the mesh edges, length c + 1.
    abs_values : numpy.ndarray
        Integral of ``|f|`` between ``edges[0]`` and each mesh edge,
        length c + 1.
    remainder : float
        T at ``edges[0]``, the part of the integral beyond the mesh.
    error_estimate : float
        Largest ratio, over the mesh edges, of the accumulated error estimate
        to the accumulated integral of ``|f|``.
    n_noise : int
        Number of mesh cells accepted as rounding-limited.
    n_unresolved : int
        Number of mesh cells accepted without meeting any criterion.
    """

    def __init__(self, family, f, median, side, tol):
        """
        Build the mesh and tabulate the integral at its edges.

        Parameters
        ----------
        family : Family
            The density p.
        f : callable
            The integrand h p: maps a numpy.ndarray of points, length k, to
            an array of length k.
        median : float
            Median of p, the inner end of the mesh.
        side : str
            ``"lower"`` or ``"upper"``.
        tol : float
            Relative tolerance of the cell integrals.
        """
        self.sign = 1.0 if side == "lower" else -1.0
        self._f = f
        self._support = family.support()
        self._tol = tol

        q = 0.5 ** np.arange(1, _N_LEVELS + 1)
        lower, upper = self._support
        end = lower if side == "lower" else upper
        with warnings.catch_warnings(), np.errstate(all="ignore"):
            warnings.simplefilter("ignore")
            pts = np.array(family.ppf(q) if side == "lower"
                           else family.isf(q), dtype=float)
            pts[0] = median
            dens = np.asarray(family.pdf(pts), dtype=float)
            # keep the edges where floating point still resolves the
            # distance to the end of the support, and nothing overflows
            if np.isfinite(end):
                resolved = np.abs(pts - end) > max(
                    _TINY, _MIN_GAP_ULPS * np.spacing(abs(end)))
            else:
                resolved = np.abs(pts) < 1.0 / _TINY
            good = (np.isfinite(pts) & (pts > lower) & (pts < upper)
                    & np.isfinite(dens) & (dens > 0) & resolved)
            good[1:] &= np.diff(self.sign * pts) < 0
        good[0] = True
        n_good = pts.size if good.all() else int(np.argmin(good))
        edges = pts[:n_good][::-1]

        self.remainder = self._quad(edges[0])
        if edges.size > 1:
            (edges, integral, abs_integral, error,
             self.n_noise, self.n_unresolved) = _refine(f, edges, tol)
        else:
            integral = abs_integral = error = np.empty(0)
            self.n_noise = self.n_unresolved = 0
        self.edges = edges
        self.values = self.remainder + np.concatenate(
            [[0.0], np.cumsum(integral)])
        self.abs_values = np.concatenate([[0.0], np.cumsum(abs_integral)])
        cum_error = np.cumsum(error)
        cum_abs = self.abs_values[1:]
        ratio = cum_error[cum_abs > 0] / cum_abs[cum_abs > 0]
        self.error_estimate = float(ratio.max()) if ratio.size else 0.0
        # increasing copy of the edges for the cell search
        self._search_edges = self.sign * self.edges

    def _quad(self, x):
        """
        Integral between the end of the support and one point, by QUADPACK.

        Slow path, used only for the part of the tail beyond the mesh.

        Parameters
        ----------
        x : float
            A point of the support.

        Returns
        -------
        float
            T(x); ``0.0`` if the quadrature does not return a finite number.
        """
        lower, upper = self._support
        a, b = (lower, x) if self.sign > 0 else (x, upper)

        def scalar_f(y):
            return float(self._f(np.array([y]))[0])

        with warnings.catch_warnings(), np.errstate(all="ignore"):
            warnings.simplefilter("ignore")
            try:
                value = integrate.quad(scalar_f, a, b, epsabs=0.0,
                                       epsrel=max(self._tol, 1e-13),
                                       limit=100)[0]
            except Exception:
                return 0.0
        return float(value) if np.isfinite(value) else 0.0

    def __call__(self, x):
        """
        Evaluate the integral at points on this side of the median.

        Parameters
        ----------
        x : numpy.ndarray
            Points in the support, on this side of the median (the median
            included), length k, in any order.

        Returns
        -------
        numpy.ndarray
            T(x), length k.
        """
        j = np.searchsorted(self._search_edges, self.sign * x,
                            side="right") - 1
        out = np.empty(x.shape)
        inside = j >= 0
        if inside.any():
            part, _ = _gauss_legendre(self._f, self.edges[j[inside]],
                                      x[inside])
            out[inside] = self.values[j[inside]] + part
        for i in np.flatnonzero(~inside):
            out[i] = self._quad(float(x[i]))
        return out


### ---------------------------------------------------------------------------
### Solver
### ---------------------------------------------------------------------------

def solve_exact(problem, rtol=1e-12, check_centred=True):
    """
    Solve the weighted Poisson problem by quadrature of its closed form.

    Parameters
    ----------
    problem : Problem
        The problem (p phi')' = h p.
    rtol : float, optional
        Tolerance of the integrals of h p, relative to the integral of
        ``|h| p`` from the nearer end of the support. Default is 1e-12.
    check_centred : bool, optional
        Whether to raise an error when E_p[h] is not zero. Default is True.

    Returns
    -------
    solution : Solution
        The solution with ``method="exact"`` and ``domain`` the support of
        p. Its ``dphi`` maps a numpy.ndarray of points of any shape, in any
        order, to phi' at those points, same shape (a scalar gives a
        scalar); it is ``nan`` outside the open support. Its ``info`` holds:

        - ``"mean_h"``: the computed E_p[h];
        - ``"mean_abs_h"``: the computed E_p[|h|];
        - ``"centring_ratio"``: ``|mean_h| / mean_abs_h``;
        - ``"median"``: the median of p, where the two branches meet;
        - ``"median_jump"``: ``mean_h / p(median)``, the jump of ``dphi``
          at the median caused by a non-zero E_p[h];
        - ``"rtol"`` and ``"order"``: the tolerance and the number of
          Gauss-Legendre nodes per cell;
        - and for ``side`` in ``"lower"``, ``"upper"``:
          ``"edges_<side>"`` (mesh edges from the tail to the median, a
          numpy.ndarray of length c + 1), ``"n_cells_<side>"`` (c),
          ``"tail_remainder_<side>"`` (integral of h p beyond the mesh),
          ``"error_estimate_<side>"`` (largest estimated error of the
          tabulated integrals, relative to the integral of ``|h| p`` from
          the tail), ``"n_noise_limited_<side>"`` (cells where rounding
          stopped the refinement) and ``"n_unresolved_<side>"`` (cells
          where bisection was exhausted, as at a jump of h).

    Raises
    ------
    ValueError
        If ``check_centred`` is True and ``|E_p[h]| > 1e-8 * E_p[|h|]``, or
        the computed E_p[h] is not finite.
    """
    family = problem.family
    h = problem.h
    lower, upper = family.support()
    median = float(family.ppf(0.5))
    tol = max(float(rtol), 1e-15)

    def integrand(y):
        with np.errstate(all="ignore"):
            hy = np.broadcast_to(np.asarray(h(y), dtype=float), y.shape)
            return hy * family.pdf(y)

    sides = {side: _TailIntegral(family, integrand, median, side, tol)
             for side in ("lower", "upper")}

    mean_h = float(sides["lower"].values[-1] + sides["upper"].values[-1])
    mean_abs_h = float(sides["lower"].abs_values[-1]
                       + sides["upper"].abs_values[-1])
    ratio = abs(mean_h) / mean_abs_h if mean_abs_h > 0 else 0.0
    if check_centred and not np.isfinite(ratio):
        raise ValueError(
            f"the integral of h p is not finite for problem "
            f"{problem.name!r}: E_p[h] = {mean_h}, E_p[|h|] = {mean_abs_h}")
    if check_centred and ratio > _CENTRED_TOL:
        raise ValueError(
            f"h is not centred for problem {problem.name!r}: "
            f"E_p[h] = {mean_h:.3e}, E_p[|h|] = {mean_abs_h:.3e}")

    def dphi(x):
        x = np.asarray(x, dtype=float)
        flat = x.ravel()
        out = np.full(flat.shape, np.nan)
        inside = np.isfinite(flat) & (flat > lower) & (flat < upper)
        masks = {"lower": inside & (flat <= median),
                 "upper": inside & (flat > median)}
        for side, mask in masks.items():
            if mask.any():
                tail = sides[side]
                with np.errstate(all="ignore"):
                    out[mask] = (tail.sign * tail(flat[mask])
                                 / family.pdf(flat[mask]))
        return out.reshape(x.shape)[()]

    info = {
        "mean_h": mean_h,
        "mean_abs_h": mean_abs_h,
        "centring_ratio": float(ratio),
        "median": median,
        "median_jump": float(mean_h / family.pdf(median)),
        "rtol": float(rtol),
        "order": _ORDER,
    }
    for side, tail in sides.items():
        info[f"edges_{side}"] = tail.edges
        info[f"n_cells_{side}"] = int(tail.edges.size - 1)
        info[f"tail_remainder_{side}"] = float(tail.remainder)
        info[f"error_estimate_{side}"] = tail.error_estimate
        info[f"n_noise_limited_{side}"] = int(tail.n_noise)
        info[f"n_unresolved_{side}"] = int(tail.n_unresolved)

    return Solution(dphi=dphi, domain=(lower, upper), method="exact",
                    info=info)
