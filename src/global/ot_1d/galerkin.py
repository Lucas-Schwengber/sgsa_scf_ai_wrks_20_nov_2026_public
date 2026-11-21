"""
Galerkin solver for the weighted Poisson problem, with Monte Carlo quadrature.

The problem (p phi')' = h p is multiplied by a test function psi_k and
integrated by parts; with zero flux p phi' at the ends of the support this
gives the weak form

    E_p[phi' psi_k'] = -E_p[h psi_k],    k = 1, ..., K.

With phi = sum_k c_k psi_k the coefficients solve A c = b, where
A = E_p[psi' psi'^T] and b = -E_p[h psi]. The solver sees p only through the
two expectations. In Monte Carlo mode they are averages over n i.i.d. draws
from p, the same draws for A, b and the standardisation of the basis; in the
deterministic reference mode ("n = infinity") they are computed by quadrature.
The basis is injectable: any object with the interface of
:class:`HermiteBasis` can be used.
"""

import copy

import numpy as np
from numpy.polynomial import hermite_e

from .metrics import expectation
from .problem import Solution

# Probability mass left out in each tail by the quadrature of the reference
# mode. It is much smaller than the default of ``expectation`` because A
# integrates polynomials of degree up to 2K - 2 against p, whose mass sits far
# in the tails when K is large.
REFERENCE_TAIL = 1e-40


### ---------------------------------------------------------------------------
### Basis
### ---------------------------------------------------------------------------

class HermiteBasis:
    """
    Orthonormal probabilists' Hermite polynomials of degree 1 to K.

    The basis functions are psi_k(x) = He_k(z) / sqrt(k!), k = 1, ..., K,
    in the standardised variable z = (x - loc) / scale. They are orthonormal
    under N(loc, scale^2). The constant He_0 is left out because phi is
    defined up to a constant.

    Attributes
    ----------
    degree : int
        Highest polynomial degree K.
    size : int
        Number of basis functions, equal to K.
    loc : float
        Location of the standardisation. It is 0.0 until
        :meth:`standardise` or :meth:`fit` is called.
    scale : float
        Scale of the standardisation, positive. It is 1.0 until
        :meth:`standardise` or :meth:`fit` is called.
    """

    def __init__(self, degree):
        """
        Initialize the basis with the identity standardisation z = x.

        Parameters
        ----------
        degree : int
            Highest polynomial degree K, at least 1. The basis has K
            functions, of degree 1 to K.
        """
        if int(degree) != degree or degree < 1:
            raise ValueError(f"degree must be a positive integer, "
                             f"got {degree!r}")
        self.degree = int(degree)
        self.size = self.degree
        self.loc = 0.0
        self.scale = 1.0
        # sqrt(k!) for k = 1..K, the N(0, 1) norm of He_k
        self._norm = np.sqrt(np.cumprod(np.arange(1.0, self.degree + 1.0)))

    def __repr__(self):
        """
        Return the degree and the standardisation as a string.
        """
        return (f"HermiteBasis(degree={self.degree}, loc={self.loc:g}, "
                f"scale={self.scale:g})")

    def standardise(self, loc, scale):
        """
        Set the standardised variable z = (x - loc) / scale.

        Parameters
        ----------
        loc : float
            Location, usually the mean of p.
        scale : float
            Scale, positive, usually the standard deviation of p.

        Returns
        -------
        self : HermiteBasis
            The basis itself, modified in place.
        """
        loc, scale = float(loc), float(scale)
        if not (np.isfinite(loc) and np.isfinite(scale) and scale > 0.0):
            raise ValueError(f"need finite loc and positive finite scale, "
                             f"got loc={loc!r}, scale={scale!r}")
        self.loc, self.scale = loc, scale
        return self

    def fit(self, x):
        """
        Standardise with the sample mean and standard deviation of draws.

        The standard deviation uses the divisor n (not n - 1), so that the
        empirical measure of the draws has mean 0 and variance 1 in z, and
        psi_1 and psi_2 have sample mean exactly zero.

        Parameters
        ----------
        x : array_like
            Draws from p, length n with n at least 2.

        Returns
        -------
        self : HermiteBasis
            The basis itself, modified in place.
        """
        x = np.asarray(x, dtype=float).ravel()
        return self.standardise(np.mean(x), np.std(x))

    def _vander(self, x):
        """
        Evaluate He_0, ..., He_K at the standardised points.

        Parameters
        ----------
        x : array_like
            Evaluation points, length m.

        Returns
        -------
        numpy.ndarray
            Array of shape (m, K + 1) whose column j holds He_j(z).
        """
        z = (np.asarray(x, dtype=float).ravel() - self.loc) / self.scale
        return hermite_e.hermevander(z, self.degree)

    def psi(self, x):
        """
        Evaluate the basis functions.

        Parameters
        ----------
        x : array_like
            Evaluation points, length m.

        Returns
        -------
        numpy.ndarray
            Array of shape (m, K) whose column k - 1 holds psi_k(x).
        """
        return self._vander(x)[:, 1:] / self._norm

    def dpsi(self, x):
        """
        Evaluate the x-derivatives of the basis functions.

        Uses He_k' = k He_{k-1} and the chain rule dz/dx = 1 / scale.

        Parameters
        ----------
        x : array_like
            Evaluation points, length m.

        Returns
        -------
        numpy.ndarray
            Array of shape (m, K) whose column k - 1 holds psi_k'(x).
        """
        k = np.arange(1.0, self.degree + 1.0)
        return self._vander(x)[:, :-1] * (k / (self._norm * self.scale))


### ---------------------------------------------------------------------------
### Solver
### ---------------------------------------------------------------------------

def _monte_carlo_system(problem, basis, x, centre_h):
    """
    Assemble the Galerkin system from i.i.d. draws, fitting the basis.

    Parameters
    ----------
    problem : Problem
        The weighted Poisson problem; only ``problem.h`` is used.
    basis : object
        Basis with the interface of :class:`HermiteBasis`. Its ``fit`` method
        is called with the draws, so it is modified in place.
    x : numpy.ndarray
        Draws from p, length n.
    centre_h : bool
        Whether to subtract the sample mean of h before forming b.

    Returns
    -------
    A : numpy.ndarray
        Matrix (1/n) sum_i psi'(x_i) psi'(x_i)^T, of shape (K, K).
    b : numpy.ndarray
        Vector -(1/n) sum_i h(x_i) psi(x_i), length K, with h replaced by
        h minus its sample mean when ``centre_h`` is true.
    h_mean : float
        Sample mean of h at the draws (before any centring).
    """
    n = x.size
    basis.fit(x)
    h = np.asarray(problem.h(x), dtype=float)
    h_mean = float(np.mean(h))
    if centre_h:
        h = h - h_mean
    dpsi = basis.dpsi(x)
    A = dpsi.T @ dpsi / n
    b = -(basis.psi(x).T @ h) / n
    return A, b, h_mean


def _reference_system(problem, basis, tail):
    """
    Assemble the Galerkin system by quadrature, standardising the basis.

    Parameters
    ----------
    problem : Problem
        The weighted Poisson problem.
    basis : object
        Basis with the interface of :class:`HermiteBasis`. Its
        ``standardise`` method is called with the mean and standard deviation
        of p, so it is modified in place.
    tail : float
        Probability mass left out in each tail by the quadrature.

    Returns
    -------
    A : numpy.ndarray
        Matrix E_p[psi' psi'^T], of shape (K, K).
    b : numpy.ndarray
        Vector -E_p[h psi], length K.
    h_mean : float
        Quadrature value of E_p[h], zero up to quadrature error for a
        well-posed problem.
    """
    family = problem.family
    basis.standardise(family.mean(), family.std())

    def outer(x):
        dpsi = basis.dpsi(x)
        return dpsi[:, :, None] * dpsi[:, None, :]

    def load(x):
        return np.asarray(problem.h(x), dtype=float)[:, None] * basis.psi(x)

    A = expectation(family, outer, tail=tail)
    b = -expectation(family, load, tail=tail)
    h_mean = float(expectation(family, problem.h, tail=tail))
    return A, b, h_mean


def solve_galerkin(problem, basis, n=None, rng=None, samples=None,
                   centre_h=False, equilibrate=True):
    """
    Solve the weighted Poisson problem by the Galerkin method.

    The coefficients c of phi = sum_k c_k psi_k solve A c = b in the
    least-squares sense (``numpy.linalg.lstsq``, no regularisation), with
    A = E[psi' psi'^T] and b = -E[h psi]. There are two modes.

    - Monte Carlo: when ``samples`` or ``n`` is given, the expectations are
      averages over i.i.d. draws from p. The same draws standardise the basis
      (``basis.fit``) and give A and b; h is evaluated exactly at the draws.
    - Deterministic reference ("n = infinity"): when both ``n`` and
      ``samples`` are None, the expectations are computed with
      :func:`ot_1d.metrics.expectation` and the basis is standardised with
      the mean and standard deviation of p.

    By default the system is equilibrated before the solve: each basis
    function is rescaled so that A has unit diagonal. This changes neither
    the span nor the exact solution; it only removes the part of the
    ill-conditioning that comes from the scaling of the basis, so that the
    rank cut-off of the least-squares solve is not triggered by it.

    The basis passed in is not modified: the solver works on a deep copy,
    which the returned solution keeps.

    Parameters
    ----------
    problem : Problem
        The weighted Poisson problem (p phi')' = h p.
    basis : object
        Basis psi_1, ..., psi_K. Any object with the interface of
        :class:`HermiteBasis`: attribute ``size`` (K) and methods
        ``standardise(loc, scale)``, ``fit(x)``, ``psi(x)`` and ``dpsi(x)``,
        the last two returning arrays of shape (m, K) for m points.
        Attributes ``loc``, ``scale`` and ``degree``, when present, are
        copied to ``info``.
    n : int, optional
        Number of draws from p in Monte Carlo mode. Ignored when ``samples``
        is given. Default is None.
    rng : numpy.random.Generator, optional
        Random number generator for the draws. When None and draws are
        needed, an unseeded ``numpy.random.default_rng()`` is used.
        Default is None.
    samples : array_like, optional
        Draws from p to use instead of drawing, length n. Default is None.
    centre_h : bool, optional
        Whether to subtract the sample mean of h at the draws before forming
        b, in Monte Carlo mode. This makes b invariant to adding constants
        to the basis functions. The deterministic mode ignores it.
        Default is False.
    equilibrate : bool, optional
        Whether to rescale the basis functions to give A a unit diagonal
        before the least-squares solve. Default is True.

    Returns
    -------
    Solution
        Solution with ``dphi(x) = psi'(x) @ c`` (same shape as ``x``, ``nan``
        outside the support of p), ``domain`` the support of p and
        ``method = "galerkin"``. Its ``info`` dict has the keys

        - ``coef``: coefficients c, numpy.ndarray of length K;
        - ``cond``: 2-norm condition number of A (``inf`` if singular);
        - ``cond_solved``: condition number of the system actually solved
          (A with unit diagonal when ``equilibrate``, else equal to
          ``cond``);
        - ``rank``: numerical rank found by the least-squares solve;
        - ``loc``, ``scale``: standardisation of the basis (None when the
          basis does not expose them);
        - ``n``: number of draws, None in deterministic mode;
        - ``degree``: ``basis.degree`` if present, else ``basis.size``;
        - ``A``, ``b``: the system, of shape (K, K) and length K;
        - ``h_mean``: mean of h under the measure used (the draws, or the
          quadrature of p), before any centring;
        - ``centre_h``: whether h was centred (False in deterministic mode).
    """
    basis = copy.deepcopy(basis)
    if samples is None and n is None:
        n_used = None
        centred = False
        A, b, h_mean = _reference_system(problem, basis, REFERENCE_TAIL)
    else:
        if samples is None:
            if rng is None:
                rng = np.random.default_rng()
            samples = problem.family.sample(int(n), rng)
        x = np.asarray(samples, dtype=float).ravel()
        n_used = int(x.size)
        centred = bool(centre_h)
        A, b, h_mean = _monte_carlo_system(problem, basis, x, centred)

    diag = np.diag(A)
    if equilibrate and np.all(np.isfinite(diag)) and np.all(diag > 0):
        d = np.sqrt(diag)
    else:
        d = np.ones(len(b))
    coef, _, rank, sing = np.linalg.lstsq(A / np.outer(d, d), b / d,
                                          rcond=None)
    coef = coef / d
    with np.errstate(divide="ignore"):
        cond_solved = float(sing[0] / sing[-1])
    cond = float(np.linalg.cond(A)) if np.any(d != 1.0) else cond_solved

    lower, upper = problem.family.support()

    def dphi(x):
        x = np.asarray(x, dtype=float)
        flat = x.ravel()
        out = np.full(flat.shape, np.nan)
        inside = (flat >= lower) & (flat <= upper)
        if inside.any():
            out[inside] = basis.dpsi(flat[inside]) @ coef
        return out.reshape(x.shape)

    info = {
        "coef": coef,
        "cond": cond,
        "cond_solved": cond_solved,
        "rank": int(rank),
        "loc": getattr(basis, "loc", None),
        "scale": getattr(basis, "scale", None),
        "n": n_used,
        "degree": int(getattr(basis, "degree", basis.size)),
        "A": A,
        "b": b,
        "h_mean": h_mean,
        "centre_h": centred,
    }
    return Solution(dphi=dphi, domain=(lower, upper), method="galerkin",
                    info=info)
