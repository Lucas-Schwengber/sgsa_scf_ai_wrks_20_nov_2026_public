"""
The weighted Poisson problem and the common return type of its solvers.

The problem is: given a density p on the real line and a function h with
E_p[h] = 0, find phi with

    phi'' + phi' (log p)' = h,    equivalently    (p phi')' = h p,

and zero flux p phi' at the ends of the support. Every solver in this package
takes a :class:`Problem` and returns a :class:`Solution` whose ``dphi`` is an
approximation of phi'.
"""

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from .families import Family


@dataclass(frozen=True)
class Problem:
    """
    A weighted Poisson problem (p phi')' = h p on the real line.

    Attributes
    ----------
    family : Family
        The density p.
    h : callable
        Right-hand side: maps a numpy.ndarray of points to an array of the
        same shape. Must satisfy E_p[h] = 0.
    name : str
        Short label of the problem, used in tables and file names.
    param : str or None
        Name of the parameter when h = -score in that parameter, else None.
    """

    family: Family
    h: Callable
    name: str
    param: str | None = None

    @classmethod
    def from_score(cls, family, param, name=None):
        """
        Build the problem with h = -d/d(param) log p_theta.

        Its solution phi' is the transport linearization of the family in
        that parameter.

        Parameters
        ----------
        family : Family
            The density p_theta.
        param : str
            Name of the parameter to perturb.
        name : str, optional
            Label of the problem. Default is ``"<family name>_<param>"``.

        Returns
        -------
        Problem
            The problem with ``param`` set.
        """
        if param not in family.params:
            raise KeyError(f"unknown parameter {param!r}")

        def h(x):
            return -family.score(x, param)

        if name is None:
            name = f"{family.name}_{param}"
        return cls(family=family, h=h, name=name, param=param)

    def exact_dphi(self, x):
        """
        Exact phi' from an elementary formula, when the family has one.

        Parameters
        ----------
        x : array_like
            Evaluation points.

        Returns
        -------
        numpy.ndarray
            Values of phi'(x), same shape as ``x``.

        Raises
        ------
        NotImplementedError
            If the problem is not a score problem, or the family has no
            elementary formula for this parameter.
        """
        if self.param is None:
            raise NotImplementedError("not a score problem")
        return self.family.transport_linearization(x, self.param)


@dataclass
class Solution:
    """
    Output of a solver: an approximation of phi' and how it was obtained.

    Attributes
    ----------
    dphi : callable
        Maps a numpy.ndarray of points to the approximation of phi' there,
        same shape. Returns ``nan`` outside ``domain``.
    domain : tuple of float
        Interval (a, b) on which ``dphi`` is defined; ``(-inf, inf)`` or
        the support of p for solvers defined everywhere.
    method : str
        Solver label: ``"exact"``, ``"fd"`` or ``"galerkin"``.
    info : dict
        Solver-specific diagnostics (grid, coefficients, condition number,
        ...). Values should be floats, ints, strings or numpy arrays.
    """

    dphi: Callable
    domain: tuple
    method: str
    info: dict = field(default_factory=dict)

    def __call__(self, x):
        """
        Evaluate the approximation of phi'.

        Parameters
        ----------
        x : array_like
            Evaluation points.

        Returns
        -------
        numpy.ndarray
            Values of ``dphi``, same shape as ``x``.
        """
        return self.dphi(np.asarray(x, dtype=float))
