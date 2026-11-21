"""
Parametric families of densities on the real line, wrapping ``scipy.stats``.

A :class:`Family` is one member p_theta of a parametric family, together with
the derivatives the weighted Poisson solvers need: the x-derivative of
log p_theta and the score (the theta-derivative of log p_theta). Both have
numerical defaults, so any ``scipy.stats`` distribution can be wrapped with
:class:`ScipyFamily`; :class:`Gaussian` and :class:`Gamma` override them with
exact formulas.
"""

import numpy as np
from scipy import special, stats


### ---------------------------------------------------------------------------
### Numerical differentiation
### ---------------------------------------------------------------------------

def _central_diff(f, t, step):
    """
    Fourth-order central difference of a function of one real variable.

    Parameters
    ----------
    f : callable
        Function of a float returning a float or a numpy.ndarray.
    t : float
        Point at which to differentiate.
    step : float or numpy.ndarray
        Step of the stencil; an array gives one step per evaluation point.

    Returns
    -------
    float or numpy.ndarray
        Approximation of f'(t), with error of order ``step**4``.
    """
    return (-f(t + 2 * step) + 8 * f(t + step)
            - 8 * f(t - step) + f(t - 2 * step)) / (12 * step)


### ---------------------------------------------------------------------------
### Base class
### ---------------------------------------------------------------------------

class Family:
    """
    One member p_theta of a parametric family of densities on the real line.

    Subclasses implement :meth:`_dist`. They may override :meth:`dlogpdf`,
    :meth:`score` and :meth:`transport_linearization` with exact formulas.

    Attributes
    ----------
    name : str
        Short name of the family, e.g. ``"gaussian"``.
    params : dict of str to float
        Parameter values theta, keyed by parameter name.
    """

    def __init__(self, name, params):
        """
        Initialize the family member.

        Parameters
        ----------
        name : str
            Short name of the family.
        params : dict of str to float
            Parameter values theta, keyed by parameter name.
        """
        self.name = name
        self.params = {k: float(v) for k, v in params.items()}

    def __repr__(self):
        """
        Return the name and parameter values as a string.
        """
        args = ", ".join(f"{k}={v:g}" for k, v in self.params.items())
        return f"{self.name}({args})"

    def _dist(self, params):
        """
        Build the frozen ``scipy.stats`` distribution for given parameters.

        Parameters
        ----------
        params : dict of str to float
            Parameter values, with the same keys as ``self.params``.

        Returns
        -------
        scipy.stats.rv_continuous_frozen
            The frozen distribution.
        """
        raise NotImplementedError

    def with_params(self, **changes):
        """
        Return a copy of the family member with some parameters changed.

        Parameters
        ----------
        **changes : float
            New values, keyed by parameter name.

        Returns
        -------
        Family
            A new object of the same class.
        """
        unknown = set(changes) - set(self.params)
        if unknown:
            raise KeyError(f"unknown parameters {sorted(unknown)}")
        new = object.__new__(type(self))
        new.__dict__.update(self.__dict__)
        new.params = {**self.params,
                      **{k: float(v) for k, v in changes.items()}}
        return new

    ### -----------------------------------------------------------------------
    ### Distribution functions
    ### -----------------------------------------------------------------------

    def pdf(self, x):
        """
        Density p_theta(x).

        Parameters
        ----------
        x : array_like
            Evaluation points.

        Returns
        -------
        numpy.ndarray
            Density values, same shape as ``x``.
        """
        return self._dist(self.params).pdf(x)

    def logpdf(self, x):
        """
        Log-density log p_theta(x).

        Parameters
        ----------
        x : array_like
            Evaluation points.

        Returns
        -------
        numpy.ndarray
            Log-density values, same shape as ``x``.
        """
        return self._dist(self.params).logpdf(x)

    def cdf(self, x):
        """
        Cumulative distribution function F_theta(x).

        Parameters
        ----------
        x : array_like
            Evaluation points.

        Returns
        -------
        numpy.ndarray
            CDF values, same shape as ``x``.
        """
        return self._dist(self.params).cdf(x)

    def sf(self, x):
        """
        Survival function 1 - F_theta(x), accurate in the upper tail.

        Parameters
        ----------
        x : array_like
            Evaluation points.

        Returns
        -------
        numpy.ndarray
            Survival function values, same shape as ``x``.
        """
        return self._dist(self.params).sf(x)

    def ppf(self, u):
        """
        Quantile function F_theta^{-1}(u).

        Parameters
        ----------
        u : array_like
            Probabilities in [0, 1].

        Returns
        -------
        numpy.ndarray
            Quantiles, same shape as ``u``.
        """
        return self._dist(self.params).ppf(u)

    def isf(self, u):
        """
        Inverse survival function, accurate for small ``u``.

        Parameters
        ----------
        u : array_like
            Upper-tail probabilities in [0, 1].

        Returns
        -------
        numpy.ndarray
            Points x with 1 - F_theta(x) = u, same shape as ``u``.
        """
        return self._dist(self.params).isf(u)

    def sample(self, n, rng):
        """
        Draw i.i.d. samples from p_theta.

        Parameters
        ----------
        n : int
            Number of samples.
        rng : numpy.random.Generator
            Random number generator.

        Returns
        -------
        numpy.ndarray
            Samples, length n.
        """
        return self._dist(self.params).rvs(size=n, random_state=rng)

    def mean(self):
        """
        Mean of p_theta.

        Returns
        -------
        float
            The mean.
        """
        return float(self._dist(self.params).mean())

    def std(self):
        """
        Standard deviation of p_theta.

        Returns
        -------
        float
            The standard deviation.
        """
        return float(self._dist(self.params).std())

    def support(self):
        """
        Support of p_theta.

        Returns
        -------
        lower : float
            Lower end of the support, possibly ``-inf``.
        upper : float
            Upper end of the support, possibly ``inf``.
        """
        lower, upper = self._dist(self.params).support()
        return float(lower), float(upper)

    def domain(self, eps):
        """
        Central quantile interval [F^{-1}(eps), F^{-1}(1 - eps)].

        Parameters
        ----------
        eps : float
            Probability mass left out in each tail, in (0, 0.5).

        Returns
        -------
        a : float
            Lower end of the interval.
        b : float
            Upper end of the interval.
        """
        return float(self.ppf(eps)), float(self.isf(eps))

    ### -----------------------------------------------------------------------
    ### Derivatives
    ### -----------------------------------------------------------------------

    def dlogpdf(self, x):
        """
        Derivative in x of the log-density, (log p_theta)'(x).

        The default is a fourth-order central difference in x.

        Parameters
        ----------
        x : array_like
            Evaluation points in the interior of the support.

        Returns
        -------
        numpy.ndarray
            Values of (log p_theta)'(x), same shape as ``x``.
        """
        x = np.asarray(x, dtype=float)
        lower, upper = self.support()
        # keep the 5-point stencil inside the support
        room = np.minimum(x - lower, upper - x)
        step = np.minimum(1e-3 * self.std(), 1e-2 * room)
        return _central_diff(self.logpdf, x, step)

    def score(self, x, param):
        """
        Score: derivative of log p_theta(x) in one parameter.

        The default is a fourth-order central difference in the parameter.

        Parameters
        ----------
        x : array_like
            Evaluation points.
        param : str
            Name of the parameter to differentiate in.

        Returns
        -------
        numpy.ndarray
            Values of d/d(param) log p_theta(x), same shape as ``x``.
        """
        if param not in self.params:
            raise KeyError(f"unknown parameter {param!r}")
        x = np.asarray(x, dtype=float)
        theta = self.params[param]
        step = 1e-3 * max(1.0, abs(theta))

        def logpdf_at(t):
            return self._dist({**self.params, param: t}).logpdf(x)

        return _central_diff(logpdf_at, theta, step)

    def transport_linearization(self, x, param):
        """
        Exact transport linearization in one parameter, when known.

        This is Phi_theta(x) = d/d(param) F_theta^{-1}(u) at u = F_theta(x),
        the solution phi' of the weighted Poisson equation with
        h = -score. Families override it where a formula in elementary
        functions exists; it is used to test the generic closed form.

        Parameters
        ----------
        x : array_like
            Evaluation points.
        param : str
            Name of the parameter.

        Returns
        -------
        numpy.ndarray
            Values of Phi_theta(x), same shape as ``x``.

        Raises
        ------
        NotImplementedError
            If no elementary formula is implemented for this parameter.
        """
        raise NotImplementedError(
            f"no elementary transport linearization for {self.name}/{param}")


### ---------------------------------------------------------------------------
### Generic scipy wrapper
### ---------------------------------------------------------------------------

class ScipyFamily(Family):
    """
    Family built from any ``scipy.stats`` continuous distribution.

    All derivatives use the numerical defaults of :class:`Family`.

    Attributes
    ----------
    name : str
        Short name of the family.
    params : dict of str to float
        Parameter values, keyed by the keyword names of ``dist``.
    dist : scipy.stats.rv_continuous
        The unfrozen distribution, e.g. ``scipy.stats.lognorm``.
    """

    def __init__(self, name, dist, **params):
        """
        Initialize the family member.

        Parameters
        ----------
        name : str
            Short name of the family.
        dist : scipy.stats.rv_continuous
            The unfrozen distribution, e.g. ``scipy.stats.lognorm``.
        **params : float
            Parameter values, passed to ``dist`` as keyword arguments
            (shape parameters, ``loc``, ``scale``).
        """
        super().__init__(name, params)
        self.dist = dist

    def _dist(self, params):
        """
        Build the frozen distribution ``self.dist(**params)``.

        Parameters
        ----------
        params : dict of str to float
            Parameter values.

        Returns
        -------
        scipy.stats.rv_continuous_frozen
            The frozen distribution.
        """
        return self.dist(**params)


### ---------------------------------------------------------------------------
### Families with exact derivatives
### ---------------------------------------------------------------------------

class Gaussian(Family):
    """
    Gaussian N(mu, sigma^2), parametrized by ``mu`` and ``sigma``.

    Attributes
    ----------
    name : str
        ``"gaussian"``.
    params : dict of str to float
        Keys ``"mu"`` (mean) and ``"sigma"`` (standard deviation).
    """

    def __init__(self, mu=0.0, sigma=1.0):
        """
        Initialize the Gaussian.

        Parameters
        ----------
        mu : float, optional
            Mean. Default is 0.0.
        sigma : float, optional
            Standard deviation, positive. Default is 1.0.
        """
        super().__init__("gaussian", {"mu": mu, "sigma": sigma})

    def _dist(self, params):
        """
        Build ``scipy.stats.norm`` for given parameters.

        Parameters
        ----------
        params : dict of str to float
            Keys ``"mu"`` and ``"sigma"``.

        Returns
        -------
        scipy.stats.rv_continuous_frozen
            The frozen distribution.
        """
        return stats.norm(loc=params["mu"], scale=params["sigma"])

    def dlogpdf(self, x):
        """
        Exact (log p)'(x) = -(x - mu) / sigma^2.

        Parameters
        ----------
        x : array_like
            Evaluation points.

        Returns
        -------
        numpy.ndarray
            Values of (log p)'(x), same shape as ``x``.
        """
        mu, sigma = self.params["mu"], self.params["sigma"]
        return -(np.asarray(x, dtype=float) - mu) / sigma**2

    def score(self, x, param):
        """
        Exact score in ``"mu"`` or ``"sigma"``.

        Parameters
        ----------
        x : array_like
            Evaluation points.
        param : str
            ``"mu"`` or ``"sigma"``.

        Returns
        -------
        numpy.ndarray
            Values of the score, same shape as ``x``.
        """
        mu, sigma = self.params["mu"], self.params["sigma"]
        z = (np.asarray(x, dtype=float) - mu) / sigma
        if param == "mu":
            return z / sigma
        if param == "sigma":
            return (z**2 - 1.0) / sigma
        raise KeyError(f"unknown parameter {param!r}")

    def transport_linearization(self, x, param):
        """
        Exact transport linearization: 1 for ``"mu"``, (x - mu)/sigma for
        ``"sigma"``.

        Parameters
        ----------
        x : array_like
            Evaluation points.
        param : str
            ``"mu"`` or ``"sigma"``.

        Returns
        -------
        numpy.ndarray
            Values of Phi_theta(x), same shape as ``x``.
        """
        mu, sigma = self.params["mu"], self.params["sigma"]
        x = np.asarray(x, dtype=float)
        if param == "mu":
            return np.ones_like(x)
        if param == "sigma":
            return (x - mu) / sigma
        raise KeyError(f"unknown parameter {param!r}")


class Gamma(Family):
    """
    Gamma distribution, parametrized by ``shape`` and ``scale``.

    The density is x^(shape-1) exp(-x/scale) / (Gamma(shape) scale^shape)
    on x > 0.

    Attributes
    ----------
    name : str
        ``"gamma"``.
    params : dict of str to float
        Keys ``"shape"`` and ``"scale"``.
    """

    def __init__(self, shape=2.0, scale=1.0):
        """
        Initialize the Gamma distribution.

        Parameters
        ----------
        shape : float, optional
            Shape parameter, positive. Default is 2.0.
        scale : float, optional
            Scale parameter, positive. Default is 1.0.
        """
        super().__init__("gamma", {"shape": shape, "scale": scale})

    def _dist(self, params):
        """
        Build ``scipy.stats.gamma`` for given parameters.

        Parameters
        ----------
        params : dict of str to float
            Keys ``"shape"`` and ``"scale"``.

        Returns
        -------
        scipy.stats.rv_continuous_frozen
            The frozen distribution.
        """
        return stats.gamma(a=params["shape"], scale=params["scale"])

    def dlogpdf(self, x):
        """
        Exact (log p)'(x) = (shape - 1)/x - 1/scale.

        Parameters
        ----------
        x : array_like
            Evaluation points, positive.

        Returns
        -------
        numpy.ndarray
            Values of (log p)'(x), same shape as ``x``.
        """
        shape, scale = self.params["shape"], self.params["scale"]
        return (shape - 1.0) / np.asarray(x, dtype=float) - 1.0 / scale

    def score(self, x, param):
        """
        Exact score in ``"shape"`` or ``"scale"``.

        Parameters
        ----------
        x : array_like
            Evaluation points, positive.
        param : str
            ``"shape"`` or ``"scale"``.

        Returns
        -------
        numpy.ndarray
            Values of the score, same shape as ``x``.
        """
        shape, scale = self.params["shape"], self.params["scale"]
        x = np.asarray(x, dtype=float)
        if param == "shape":
            return np.log(x / scale) - special.digamma(shape)
        if param == "scale":
            return x / scale**2 - shape / scale
        raise KeyError(f"unknown parameter {param!r}")

    def transport_linearization(self, x, param):
        """
        Exact transport linearization x/scale for ``"scale"``.

        Parameters
        ----------
        x : array_like
            Evaluation points.
        param : str
            ``"scale"``; ``"shape"`` has no elementary formula.

        Returns
        -------
        numpy.ndarray
            Values of Phi_theta(x), same shape as ``x``.
        """
        if param == "scale":
            return np.asarray(x, dtype=float) / self.params["scale"]
        return super().transport_linearization(x, param)
