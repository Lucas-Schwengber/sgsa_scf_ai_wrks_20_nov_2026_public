"""
The five pilot problems of the benchmark_gt thread.
"""

import numpy as np

from ot_1d.families import Gamma, Gaussian
from ot_1d.problem import Problem


def pilot_cases():
    """
    Build the pilot problems, keyed by their label.

    Returns
    -------
    dict of str to ot_1d.problem.Problem
        ``gauss_mu``, ``gauss_sigma`` and ``gauss_sin`` on N(0, 1);
        ``gamma_shape`` and ``gamma_scale`` on Gamma(shape 2, scale 1).
    """
    gauss = Gaussian(0.0, 1.0)
    gamma = Gamma(2.0, 1.0)
    return {
        "gauss_mu": Problem.from_score(gauss, "mu", "gauss_mu"),
        "gauss_sigma": Problem.from_score(gauss, "sigma", "gauss_sigma"),
        "gauss_sin": Problem(gauss, np.sin, "gauss_sin"),
        "gamma_shape": Problem.from_score(gamma, "shape", "gamma_shape"),
        "gamma_scale": Problem.from_score(gamma, "scale", "gamma_scale"),
    }
