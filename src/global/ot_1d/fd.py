"""
Finite-difference solver for the 1D weighted Poisson equation.

The equation (p phi')' = h p is discretised in conservative (finite-volume)
form on a grid x_0 < ... < x_{N-1} of the truncated domain [a, b]. The
unknowns are the nodal values phi_i; the fluxes live on the edges between
nodes,

    F_{i+1/2} = p(x_{i+1/2}) (phi_{i+1} - phi_i) / (x_{i+1} - x_i),

and every node owns a control volume of width w_i: half the distance to each
neighbour, so the two boundary nodes own half cells. The balance over the
control volume of node i is

    F_{i+1/2} - F_{i-1/2} = (h_i - c) p_i w_i,

where F_{-1/2} = F_a and F_{N-1/2} = F_b are the prescribed boundary fluxes.
The constant c recentres h so that the sum of all balances, the discrete
compatibility condition, holds exactly. The linear system is then singular
but consistent, and phi is fixed by pinning it to zero at one node.

The assembly functions take an arbitrary increasing grid; :func:`solve_fd`
calls them with a uniform grid.
"""

import numpy as np
from scipy import sparse
from scipy.sparse import linalg as sparse_linalg

from .problem import Solution

BOUNDARY_CONDITIONS = ("zero_flux", "exact_neumann")


### ---------------------------------------------------------------------------
### Grid
### ---------------------------------------------------------------------------

def uniform_grid(a, b, n_nodes):
    """
    Uniform grid of nodes on [a, b], including both ends.

    Parameters
    ----------
    a : float
        Lower end of the domain.
    b : float
        Upper end of the domain.
    n_nodes : int
        Number of nodes N, at least 2.

    Returns
    -------
    numpy.ndarray
        Nodes x_i = a + i (b - a)/(N - 1), length N.
    """
    return np.linspace(a, b, n_nodes)


def cell_widths(x):
    """
    Widths of the control volumes owned by the nodes of a grid.

    The control volume of an interior node reaches halfway to each
    neighbour; the two boundary nodes own half cells.

    Parameters
    ----------
    x : numpy.ndarray
        Increasing nodes, length N.

    Returns
    -------
    numpy.ndarray
        Widths w_i, length N, summing to x[-1] - x[0].
    """
    edge = np.diff(x)
    w = np.zeros(len(x))
    w[:-1] += 0.5 * edge
    w[1:] += 0.5 * edge
    return w


### ---------------------------------------------------------------------------
### Assembly
### ---------------------------------------------------------------------------

def assemble_operator(x, p_half):
    """
    Assemble the flux-difference operator of the conservative scheme.

    Row i of the matrix applied to phi gives F_{i+1/2} - F_{i-1/2}, with
    F_{i+1/2} = p_half[i] (phi[i+1] - phi[i]) / (x[i+1] - x[i]) and the
    boundary fluxes left out (they go to the right-hand side). The matrix is
    symmetric, negative semi-definite, and annihilates constants.

    Parameters
    ----------
    x : numpy.ndarray
        Increasing nodes, length N.
    p_half : numpy.ndarray
        Density at the edge midpoints (x[i] + x[i+1])/2, length N - 1.

    Returns
    -------
    scipy.sparse.csr_matrix
        Tridiagonal matrix of shape (N, N).
    """
    conductance = np.asarray(p_half, dtype=float) / np.diff(x)
    diagonal = np.zeros(len(x))
    diagonal[:-1] -= conductance
    diagonal[1:] -= conductance
    return sparse.diags([conductance, diagonal, conductance], [-1, 0, 1],
                        format="csr")


def recentring_constant(h, p, w, flux_a, flux_b):
    """
    Constant c that makes the discrete compatibility condition exact.

    It solves sum_i (h_i - c) p_i w_i = flux_b - flux_a. With zero boundary
    fluxes, c is the mean of h under the truncated, discretised density.

    Parameters
    ----------
    h : numpy.ndarray
        Right-hand side h at the nodes, length N.
    p : numpy.ndarray
        Density at the nodes, length N.
    w : numpy.ndarray
        Control-volume widths, length N.
    flux_a : float
        Prescribed flux p phi' at the lower end.
    flux_b : float
        Prescribed flux p phi' at the upper end.

    Returns
    -------
    float
        The recentring constant c.
    """
    mass = p * w
    return float((np.sum(h * mass) - (flux_b - flux_a)) / np.sum(mass))


def assemble_rhs(h_centred, p, w, flux_a, flux_b):
    """
    Assemble the right-hand side of the conservative scheme.

    Entry i is h_centred[i] p[i] w[i]; the prescribed boundary fluxes are
    moved here, so the first entry gains ``flux_a`` and the last one loses
    ``flux_b``.

    Parameters
    ----------
    h_centred : numpy.ndarray
        Recentred right-hand side h - c at the nodes, length N.
    p : numpy.ndarray
        Density at the nodes, length N.
    w : numpy.ndarray
        Control-volume widths, length N.
    flux_a : float
        Prescribed flux p phi' at the lower end.
    flux_b : float
        Prescribed flux p phi' at the upper end.

    Returns
    -------
    numpy.ndarray
        Right-hand side, length N. Its entries sum to zero when
        ``h_centred`` uses the constant of :func:`recentring_constant`.
    """
    rhs = h_centred * p * w
    rhs[0] += flux_a
    rhs[-1] -= flux_b
    return rhs


### ---------------------------------------------------------------------------
### Linear solve
### ---------------------------------------------------------------------------

def solve_pinned(operator, rhs, pin):
    """
    Solve the singular system ``operator @ phi = rhs`` with phi[pin] = 0.

    The equation and the unknown of the pinned node are removed and the
    remaining non-singular sparse system is solved directly. When ``rhs``
    sums to zero, the removed equation holds as well.

    Parameters
    ----------
    operator : scipy.sparse.spmatrix
        Matrix of shape (N, N) whose null space is the constants.
    rhs : numpy.ndarray
        Right-hand side, length N.
    pin : int
        Index of the node where phi is set to zero.

    Returns
    -------
    numpy.ndarray
        Solution phi, length N, with ``phi[pin] == 0``.
    """
    n = operator.shape[0]
    keep = np.delete(np.arange(n), pin)
    reduced = operator.tocsr()[keep][:, keep].tocsc()
    phi = np.zeros(n)
    phi[keep] = sparse_linalg.spsolve(reduced, rhs[keep])
    return phi


def residual_norms(operator, phi, rhs):
    """
    Residual of the full (unpinned) linear system, absolute and relative.

    Parameters
    ----------
    operator : scipy.sparse.spmatrix
        Matrix of shape (N, N).
    phi : numpy.ndarray
        Computed solution, length N.
    rhs : numpy.ndarray
        Right-hand side, length N.

    Returns
    -------
    absolute : float
        Euclidean norm of ``operator @ phi - rhs`` over all N rows,
        including the row of the pinned node.
    relative : float
        The same residual in the maximum norm divided by
        ``max_i (|operator| |phi| + |rhs|)_i``: the normwise backward error,
        of the order of machine precision for a stable solve.
    """
    residual = operator @ phi - rhs
    scale = np.max(abs(operator) @ np.abs(phi) + np.abs(rhs))
    absolute = float(np.linalg.norm(residual))
    relative = float(np.max(np.abs(residual)) / scale) if scale > 0 else 0.0
    return absolute, relative


### ---------------------------------------------------------------------------
### Solver
### ---------------------------------------------------------------------------

def solve_fd(problem, n_nodes, eps=1e-6, bc="zero_flux", boundary_dphi=None):
    """
    Solve (p phi')' = h p by conservative finite differences.

    The domain is the quantile interval [a, b] = [F^{-1}(eps),
    F^{-1}(1 - eps)] with a uniform grid of ``n_nodes`` nodes. The density
    and h are evaluated analytically on the grid. See the module docstring
    for the discrete equations.

    Parameters
    ----------
    problem : Problem
        The weighted Poisson problem (density family and h).
    n_nodes : int
        Number of grid nodes N, at least 2.
    eps : float, optional
        Probability mass left out in each tail by the domain truncation,
        in (0, 0.5). Default is 1e-6.
    bc : str, optional
        Boundary condition. ``"zero_flux"`` sets the flux p phi' to zero at
        a and b. ``"exact_neumann"`` sets it to p(a) phi'(a) and
        p(b) phi'(b) with the exact phi' from ``boundary_dphi``, which
        removes the domain-truncation error. Default is ``"zero_flux"``.
    boundary_dphi : callable, optional
        Exact phi': maps a numpy.ndarray of points to an array of the same
        shape. Required for ``bc="exact_neumann"``, where it is called once
        with the array ``[a, b]``; ignored for ``bc="zero_flux"``.
        Default is None.

    Returns
    -------
    Solution
        ``dphi`` is the piecewise-linear interpolant of phi' through its
        values at the edge midpoints, (phi[i+1] - phi[i])/dx, and at the two
        ends, flux/p; it returns ``nan`` outside [a, b]. ``domain`` is
        (a, b) and ``method`` is ``"fd"``. ``info`` has the keys

        - ``x`` : nodes, length N;
        - ``phi`` : nodal solution, length N, zero at node ``pin``;
        - ``dx``, ``n_nodes``, ``eps``, ``bc`` : the discretisation;
        - ``recentring_constant`` : the constant c subtracted from h;
        - ``flux_a``, ``flux_b`` : the prescribed boundary fluxes;
        - ``residual_norm`` : Euclidean norm of the residual of all N
          equations;
        - ``residual_relative`` : normwise backward error of the solve;
        - ``compatibility_defect`` : sum of the right-hand side, zero up to
          round-off;
        - ``pin`` : index of the pinned node;
        - ``x_dphi``, ``dphi_knots`` : knots and values of the interpolant
          of phi', length N + 1.

    Raises
    ------
    ValueError
        If ``bc`` is unknown, ``n_nodes`` is less than 2, ``boundary_dphi``
        is missing for ``bc="exact_neumann"``, or it returns non-finite
        values at a or b.
    """
    if bc not in BOUNDARY_CONDITIONS:
        raise ValueError(
            f"unknown bc {bc!r}; expected one of {BOUNDARY_CONDITIONS}")
    if n_nodes < 2:
        raise ValueError("n_nodes must be at least 2")
    if bc == "exact_neumann" and boundary_dphi is None:
        raise ValueError('bc="exact_neumann" requires boundary_dphi')

    family = problem.family
    a, b = family.domain(eps)
    x = uniform_grid(a, b, n_nodes)
    x_half = 0.5 * (x[:-1] + x[1:])
    w = cell_widths(x)
    p = np.asarray(family.pdf(x), dtype=float)
    p_half = np.asarray(family.pdf(x_half), dtype=float)
    h = np.asarray(problem.h(x), dtype=float)

    if bc == "exact_neumann":
        dphi_ends = np.asarray(boundary_dphi(np.array([a, b])), dtype=float)
        if dphi_ends.shape != (2,) or not np.all(np.isfinite(dphi_ends)):
            raise ValueError(
                "boundary_dphi must return two finite values at [a, b]")
        flux_a = float(p[0] * dphi_ends[0])
        flux_b = float(p[-1] * dphi_ends[1])
    else:
        flux_a, flux_b = 0.0, 0.0

    c = recentring_constant(h, p, w, flux_a, flux_b)
    operator = assemble_operator(x, p_half)
    rhs = assemble_rhs(h - c, p, w, flux_a, flux_b)
    pin = int(np.argmax(p))
    phi = solve_pinned(operator, rhs, pin)
    residual_norm, residual_relative = residual_norms(operator, phi, rhs)

    x_dphi = np.concatenate([[a], x_half, [b]])
    dphi_knots = np.concatenate([[flux_a / p[0]],
                                 np.diff(phi) / np.diff(x),
                                 [flux_b / p[-1]]])

    def dphi(points):
        """
        Piecewise-linear interpolant of the finite-difference phi'.

        Parameters
        ----------
        points : array_like
            Evaluation points.

        Returns
        -------
        numpy.ndarray
            Values of phi', same shape as ``points``; ``nan`` outside
            [a, b].
        """
        points = np.asarray(points, dtype=float)
        return np.interp(points, x_dphi, dphi_knots,
                         left=np.nan, right=np.nan)

    info = {
        "x": x,
        "phi": phi,
        "dx": float((b - a) / (n_nodes - 1)),
        "n_nodes": int(n_nodes),
        "eps": float(eps),
        "bc": bc,
        "recentring_constant": c,
        "flux_a": flux_a,
        "flux_b": flux_b,
        "residual_norm": residual_norm,
        "residual_relative": residual_relative,
        "compatibility_defect": float(np.sum(rhs)),
        "pin": pin,
        "x_dphi": x_dphi,
        "dphi_knots": dphi_knots,
    }
    return Solution(dphi=dphi, domain=(a, b), method="fd", info=info)
