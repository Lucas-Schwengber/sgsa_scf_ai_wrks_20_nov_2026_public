---
title: Theory for the pilot, closed form, finite differences and Galerkin
created: 2026-11-19
updated: 2026-11-20
authors: CLAUDE (C)
---

# Theory for the pilot

Derivations and predicted rates for the three methods of [plan.md](pilot/plan.md)
(goal in [instructions.md](instructions.md)). Claims are marked *derived* or
*heuristic*. The pilot has no results yet: every number below is a formula
evaluated by hand or by quadrature, not an output of the pilot code; the
derived formulas were cross-checked numerically in throwaway scripts. "TJS" is
Trillos, Jaffe and Sen (2025), "Wasserstein-Cramér-Rao Theory of Unbiased
Estimation". Appendix A has the derivations, Appendix B the open points of
the specification that affect the predictions.

## 1. Setup and notation (C)

$p$ is a probability density on $\mathbb{R}$, positive on its support
$(x_-, x_+)$, with CDF $F$; $\mathbb{E}_p$ is the expectation under $p$,
$\|f\|^2 = \mathbb{E}_p[f^2]$ the $L^2(p)$ norm and
$\|f\|_{[a,b]}^2 = \int_a^b f^2 p\,dx$ its restriction to an interval. $h$ is
the right-hand side, with $h \in L^2(p)$ and $\mathbb{E}_p[h] = 0$. $\phi$ is
the unknown and $q = p\,\phi'$ its flux. The problem is

$$
(p\,\phi')' = h\,p
\ \Longleftrightarrow\
\phi'' + \phi'\,(\log p)' = h
\ \text{ on } (x_-, x_+),
\qquad q(x) \to 0 \ \text{as } x \to x_\pm .
$$

- **Solvability and constant.** Integrating over the support,
  $\int h\,p\,dx = q(x_+) - q(x_-) = 0$, so $\mathbb{E}_p[h] = 0$ is
  necessary. Only $\phi'$ and $\phi''$ appear, so $\phi$ is defined up to a
  constant; all comparisons are on $\phi'$.
- **Weak form.** Multiplying by a test function $\psi$ and integrating by parts
  (the boundary term $[q\,\psi]$ vanishes):
  $\mathbb{E}_p[\phi'\psi'] = -\mathbb{E}_p[h\,\psi]$. Zero flux is the natural
  boundary condition.
- **Space.** $\{\phi : \phi' \in L^2(p)\}$ modulo constants, with energy norm
  $\|\phi'\|$. Under a Poincaré inequality
  $\mathrm{Var}_p(\psi) \le C_P\,\mathbb{E}_p[\psi'^2]$ the solution exists, is
  unique, and $\|\phi'\| \le \sqrt{C_P}\,\|h\|$ (Riesz representation). Both
  pilot densities satisfy one: $N(0,1)$ with $C_P = 1$, and Gamma(2, 1)
  because it is log-concave (standard facts).

Symbols of [plan.md](pilot/plan.md): $\varepsilon$ is the mass left out in each
tail, $[a, b] = [F^{-1}(\varepsilon), F^{-1}(1-\varepsilon)]$, $N$ the number
of grid nodes, $\Delta x = (b-a)/(N-1)$; $K$ the number of basis functions
$\psi_k$, $n$ the number of draws $X_1, \dots, X_n$ (capital; $x_j$ are grid
nodes), $\hat A$ and $\hat b$ the Monte Carlo matrix and vector. The
comparison interval $[a_0, b_0]$ uses $\varepsilon_0 = 10^{-6}$.

## 2. Closed form and transport linearization (C)

Integrating from $x_-$, and using $\mathbb{E}_p[h] = 0$ for the second form
(used on the upper half, to avoid cancellation):

$$
q(x) = \int_{x_-}^{x} h\,p\,dy = -\int_{x}^{x_+} h\,p\,dy ,
\qquad \phi'(x) = q(x)/p(x) .
$$

**Score case** (derived). Let $p_\theta$ have CDF $F_\theta$ and a support
that does not depend on $\theta$, and $h = -\partial_\theta \log p_\theta$.
Then $h\,p_\theta = -\partial_\theta p_\theta$, so
$q = -\partial_\theta F_\theta$. Differentiating
$F_\theta(F_\theta^{-1}(u)) = u$ in $\theta$ at $x = F_\theta^{-1}(u)$ gives

$$
\phi'(x) = -\frac{\partial_\theta F_\theta(x)}{p_\theta(x)}
= \partial_\theta F_\theta^{-1}(u)\big|_{u = F_\theta(x)} = \Phi_\theta(x) .
$$

$\Phi_\theta$ is the transport linearization of TJS: Definition 4.1 defines it
as the $L^2(P_\theta)$ derivative in $\theta$ of the optimal transport map
from $P_\theta$ to $P_{\theta+t}$, and in one dimension the proof of Lemma 6.8
(Section 6.1, proof in Appendix C.4) gives
$\Phi_\theta(x) = \nabla_\theta F_\theta^{-1}(F_\theta(x))$. The Wasserstein
information $J(\theta) = \mathbb{E}_\theta[\Phi_\theta^\top \Phi_\theta]$
(Definition 4.6, Lemma 6.8) is, for one parameter, the squared energy norm
$\|\Phi_\theta\|^2$ of our solution.

**Continuity equation** (derived). Differentiating
$p_\theta \Phi_\theta = -\partial_\theta F_\theta$ in $x$ gives
$\partial_\theta p_\theta + (p_\theta \Phi_\theta)' = 0$; dividing by
$p_\theta$ gives the weighted Poisson equation with $h = -$score. This is the
strong form of the continuity equation (12) of TJS with velocity $\Phi_\theta$
(their Lemma 4.5). The first arXiv version of TJS (v1, 10 Nov 2025), whose
numbering this note uses, does not state it as a Poisson problem. The current
version (v2, 26 Oct 2026) does: after Definition 4.1 it attributes the
"Poisson equation" relating the score and $\Phi_\theta$ to Li and Zhao (see
[lit_review.md](lit_review.md)). In v2 Lemma 4.5 has become Remark 4.7,
Definition 4.6 is Definition 4.5, Lemma 6.8 is Lemma 6.5, and the examples
cited below are in Appendix A.

**Pilot cases.** $(\log p)' = -x$ for $N(0,1)$ and $1/x - 1$ for Gamma(2, 1);
$\gamma$ is Euler's constant. The linear cases are checked by substitution in
$\phi'' + \phi'(\log p)' = h$.

| Case | $h$ | Exact $\phi'$ | Check |
| --- | --- | --- | --- |
| `gauss_mu` | $-x$ | $1$ | $0 + 1\cdot(-x) = -x$ |
| `gauss_sigma` | $1 - x^2$ | $x$ | $1 + x\cdot(-x) = 1 - x^2$ |
| `gamma_scale` | $2 - x$ | $x$ | $1 + x\,(1/x - 1) = 2 - x$ |
| `gauss_sin` | $\sin x$ | special function | below |
| `gamma_shape` | $1 - \gamma - \log x$ | special function | below |

They agree with TJS: $\Phi_\theta = 1$ for a location family (Examples 5.7,
6.10), $\Phi_\theta(x) = x/\theta$ for a scale family (Examples 5.8, 6.11),
$(1, x)$ for the Gaussian family (Example 5.10). Example 5.9 (Pareto,
$\Phi_\theta(x) = -x\log x/\theta$) is a further test case, outside the pilot.

**`gauss_sin`** (derived, [A.1](#a1-gauss_sin)). With $\mathrm{He}_k$ the
probabilists' Hermite polynomials,

$$
\phi'(x) = \frac{e^{-1/2}}{2\,p(x)}\,
\mathrm{Im}\,\mathrm{erfc}\!\Big(\frac{i - x}{\sqrt 2}\Big)
= -e^{-1/2} \sum_{j \ge 0} \frac{(-1)^j}{(2j+1)!}\,\mathrm{He}_{2j}(x) .
$$

It is even, bounded and not polynomial, with $\phi'(0) \approx -0.725$ and
$\phi'(x) = -\sin x/x - \cos x/x^2 + O(|x|^{-3})$ in the tails.

**`gamma_shape`** (derived, [A.2](#a2-gamma_shape)). For Gamma(2, 1), with
$E_1(x) = \int_x^\infty e^{-t}/t\,dt$ the exponential integral,

$$
\Phi_\alpha(x) = \frac{e^{x} E_1(x) + 1 - (1 + x)(1 - \gamma - \log x)}{x} .
$$

Near $0$, $\Phi_\alpha(x) = \tfrac{x}{2}(\tfrac32 - \gamma - \log x) + o(x)$:
it vanishes, but its derivative diverges like $-\tfrac12\log x$. At infinity,
$\Phi_\alpha(x) = \log x - (1-\gamma) + O(\log x / x)$. For other shapes we
only have the integral.

## 3. Finite differences (C)

**Scheme.** Nodes $x_j = a + j\,\Delta x$, $j = 0..N-1$, half-nodes
$x_{j+1/2}$, unknowns $\phi_j$, discrete flux
$q_{j+1/2} = p(x_{j+1/2})(\phi_{j+1} - \phi_j)/\Delta x$ (the task description
writes $F_{j+1/2}$; we keep $F$ for the CDF). With $\tilde h = h - \bar h$ the
recentred right-hand side and $g = \tilde h\,p$:

$$
\frac{q_{j+1/2} - q_{j-1/2}}{\Delta x} = g_j \ (0 < j < N-1), \qquad
\frac{q_{1/2} - q_a}{\Delta x/2} = g_0, \qquad
\frac{q_b - q_{N-3/2}}{\Delta x/2} = g_{N-1} .
$$

The boundary fluxes $q_a$, $q_b$ are $0$ by default, and $q(a)$, $q(b)$ from
the closed form in the diagnostic variant.

**Explicit solution** (derived). Summing the rows times their cell widths
gives $T[g] = q_b - q_a$, with $T$ the trapezoid rule on the grid. The
singular system is therefore solvable exactly when
$\bar h = (T[hp] - (q_b - q_a))/T[p]$, which is the trapezoid mean of $h$ on
$[a, b]$ in the default. Partial sums then give

$$
q_{j+1/2} = q_a + \tfrac{\Delta x}{2}\,g_0 + \Delta x \sum_{i=1}^{j} g_i ,
\qquad \phi'_{\Delta x}(x_{j+1/2}) = q_{j+1/2}/p(x_{j+1/2}) .
$$

In 1D the scheme is a quadrature rule for the closed form; the linear solve,
with $\phi$ pinned at one node, only reproduces this sum. Comparing with
$q(x) = q(a) + \int_a^x g\,dy + \bar h\,(F(x) - \varepsilon)$, the flux error
splits exactly into a truncation part
$(q_a - q(a)) - \bar h\,(F(x_{j+1/2}) - \varepsilon)$, which depends on
$\varepsilon$, and a discretisation part $E_j$, the error of the sum as a
quadrature of $\int_a^{x_{j+1/2}} g\,dy$, which depends on $\Delta x$. The
error of $\phi'$ is the flux error divided by $p$.

**Discretisation error** ([A.3](#a3-fd-quadrature-error)). For smooth $g$,
$E_j = -\frac{\Delta x^2}{24}(g'(x_{j+1/2}) + 2g'(a)) + O(\Delta x^3)$: the
scheme is second order (derived), and linear interpolation of $\phi'$ between
half-nodes keeps that order. For the Gaussian cases the $L^2(p)$ error at
half-nodes is $\frac{\Delta x^2}{24}\|g'/p\|$ to leading order, i.e. relative
errors $\frac{\sqrt2}{24}\Delta x^2$ for `gauss_mu` and
$\frac{\sqrt6}{24}\Delta x^2$ for `gauss_sigma` (derived). For the Gamma cases $p$ vanishes at the lower
end and the error is $\Delta x^2$ times a power of $\log(1/\Delta x)$: the
fitted slope should be slightly below 2 (heuristic).

**Truncation error with zero flux** (derived, [A.4](#a4-truncation-error)).
Let $\phi'_\varepsilon$ solve the truncated problem on $[a, b]$ exactly, with
zero flux and $h$ recentred by its mean on $[a, b]$. Then

$$
\phi'_\varepsilon(x) - \phi'(x) =
-\frac{q(a)\,(1 - u(x)) + q(b)\,u(x)}{p(x)} ,
\qquad u(x) = \frac{F(x) - \varepsilon}{1 - 2\varepsilon} \in [0, 1] .
$$

The flux error interpolates, linearly in the probability coordinate $u$, the
true boundary fluxes $q(a) = p(a)\phi'(a)$ and $q(b) = p(b)\phi'(b)$ that the
zero-flux condition discards. $\phi'_\varepsilon$ vanishes at $a$ and $b$: the
error is a boundary layer of width $1/\lambda$, $\lambda = |(\log p)'|$, in
which the relative error of $\phi'$ is of order one. To leading order, when
$p$ has light tails at both ends,

$$
\|\phi'_\varepsilon - \phi'\|_{[a,b]}^2
= \int_a^b \frac{[\,q(a)(1-u) + q(b)\,u\,]^2}{p}\,dx
\approx \varepsilon\,\big(\phi'(a)^2 + \phi'(b)^2\big) .
$$

**The truncation error scales as $\varepsilon^{1/2}$, not $\varepsilon$.**

- `gauss_mu`: $\phi'_\varepsilon = 1 - p(a)/p(x)$; relative error
  $\sqrt{2\varepsilon}\,(1 + b^{-2} + O(b^{-4}))$, i.e. $1.48 \times 10^{-3}$
  at $\varepsilon = 10^{-6}$.
- `gauss_sigma`: $b\sqrt{2\varepsilon}$, slope $\tfrac12$ with a logarithmic
  factor ($b \approx \sqrt{2\log(1/\varepsilon)}$). `gauss_sin`:
  $\phi'(b) \approx -\sin b/b$, so the error is modulated by
  $|\sin b(\varepsilon)|$ and is not a clean power law.
- Gamma cases: the lower end contributes $O(\varepsilon^2)$ up to logarithms
  ($p \approx x$ there); the upper end gives $\varepsilon\,\phi'(b)^2$, with
  $\phi'(b) = b$ (`gamma_scale`) or $\approx \log b - (1 - \gamma)$
  (`gamma_shape`).
- If the solver runs with $\varepsilon < \varepsilon_0$ but the error is taken
  on the fixed $[a_0, b_0]$, most of the layer lies outside and the error is
  $\approx \varepsilon\,\varepsilon_0^{-1/2}(\phi'(a)^2 + \phi'(b)^2)^{1/2}$
  up to ratios of $\lambda$: slope 1.

**Total.** The error is at most the sum of the two parts,
$O(\varepsilon^{1/2}) + O(\Delta x^2)$: with zero flux the $N$ sweep flattens
at the truncation floor (for `gauss_mu` from $N \approx 60$); with exact
Neumann data the truncation part vanishes.

## 4. Galerkin with Monte Carlo quadrature (C)

**Best approximation** (derived). With $\psi = (\psi_1, \dots, \psi_K)^\top$,
$\psi_k = \mathrm{He}_k(z)$ and $z$ the standardised variable, the Galerkin
solution with exact integrals is $\phi_K = c^\top\psi$ with $Ac = b$,
$A = \mathbb{E}_p[\psi'\psi'^\top]$, $b = -\mathbb{E}_p[h\,\psi]$. The exact
$\phi$ satisfies the weak form for each $\psi_k$, so
$\mathbb{E}_p[(\phi' - \phi_K')\,\psi_k'] = 0$: $\phi_K'$ is the
$L^2(p)$-orthogonal projection of $\phi'$ onto
$\mathrm{span}\{\psi_k'\} = \mathcal{P}_{K-1}$, the polynomials of degree at
most $K-1$, whatever the centring and scaling in $z$. This is Céa's lemma with
constant 1 (symmetric form, energy norm). The relative basis errors
$\|\phi' - \phi_K'\|/\|\phi'\|$ on the whole support follow
([A.1](#a1-gauss_sin), [A.2](#a2-gamma_shape)):

| Case | Relative basis error | At $K = 1, 2, 3, 4, 6, 8, 12$ |
| --- | --- | --- |
| `gauss_mu` | $0$ for $K \ge 1$ | $0$ |
| `gauss_sigma` | $0$ for $K \ge 2$ | $1,\ 0,\ \dots$ |
| `gamma_scale` | $0$ for $K \ge 2$ | $1/\sqrt3 \approx 0.577,\ 0,\ \dots$ |
| `gauss_sin` | $\big(\sum_{2j \ge K} w_j / \sum_{j \ge 0} w_j\big)^{1/2}$, $w_j = \frac{1}{(2j+1)(2j+1)!}$ | $0.233,\ 0.233,\ 0.040,\ 0.040,\ 5.2\times10^{-3},\ 5.4\times10^{-4},\ 3.4\times10^{-6}$ |
| `gamma_shape` | $\big(\sum_{m \ge K} v_m / (1 + \sum_{m \ge 1} v_m)\big)^{1/2}$, $v_m = \frac{1}{m^2(m+1)^3}$ | $0.347,\ 0.102,\ 0.048,\ 0.028,\ 0.0125,\ 0.0071,\ 0.0032$ |

- `gauss_sin` converges factorially, in steps of two ($\phi'$ is even);
  `gamma_shape` algebraically, $\approx 0.47\,K^{-2}$, because of the
  $x\log x$ behaviour at $0$.
- On $[a_0, b_0]$ the error is at most the whole-support value (up to a
  negligible factor) and visibly smaller at large $K$, where the projection
  error sits in the tails. The exact match is with the full-line column.
- Round-off limits the "$n = \infty$" run if the $\mathrm{He}_k$ are not
  normalised: for $N(0,1)$, $\mathrm{cond}(A) = K \cdot K!$ ($5.7\times10^9$
  at $K = 12$); for Gamma(2, 1),
  $\mathrm{cond}(A) \ge A_{KK}/A_{11} \approx 1.7\times10^{20}$ at $K = 12$
  (exact moments), beyond double precision (Appendix B).

**Monte Carlo error** (derived, first order at fixed $K$,
[A.5](#a5-monte-carlo-variance)). Write
$\hat{\mathbb{E}}_n[f] = \frac1n\sum_i f(X_i)$, so
$\hat A = \hat{\mathbb{E}}_n[\psi'\psi'^\top]$,
$\hat b = -\hat{\mathbb{E}}_n[h\psi]$, $\hat A\hat c = \hat b$ and
$\hat\phi_K' = \hat c^\top\psi'$. Then

$$
\hat c - c = A^{-1}\,\hat{\mathbb{E}}_n[\xi] + O_P(n^{-1}),
\qquad \xi = -(h\,\psi + \psi'\,\phi_K'), \quad \mathbb{E}_p[\xi] = 0 ,
$$

so $\sqrt n\,(\hat c - c) \to N(0, A^{-1}\Sigma A^{-1})$,
$\Sigma = \mathrm{Cov}_p(\xi)$. On the whole support the two errors are
orthogonal,
$\|\hat\phi_K' - \phi'\|^2 = \|\hat\phi_K' - \phi_K'\|^2 + \|\phi_K' - \phi'\|^2$,
and $n\,\|\hat\phi_K' - \phi_K'\|^2$ converges in law to a quadratic form with
mean $\mathrm{tr}(A^{-1}\Sigma)$. The error is
$\approx (\text{basis}^2 + \mathrm{tr}(A^{-1}\Sigma)/n)^{1/2}$: it decays as
$n^{-1/2}$ down to the basis floor. For the Gaussian linear cases
$\mathrm{tr}(A^{-1}\Sigma) = K + \sum_{k \le K}\frac1k$ (`gauss_mu`) and
$K^2 + 4K + 2\sum_{k \le K}\frac1k$ (`gauss_sigma`, $K \ge 2$): at first order
the Monte Carlo error grows only polynomially in $K$.

**Not exact at finite $n$** (derived). When the basis contains the solution,
$\xi = -\mathcal{D}(\phi'\psi)$ with $\mathcal{D}f = (pf)'/p$.
$\mathbb{E}_p[\mathcal{D}f] = 0$ is integration by parts under $p$, but
$\hat{\mathbb{E}}_n[\mathcal{D}f] \ne 0$: integration by parts does not hold
for the empirical measure, so the exact coefficients do not solve
$\hat A\hat c = \hat b$. Example: `gauss_mu` with $K = 1$ gives
$\hat\phi_1' = \frac1n\sum_i (X_i - \bar X)^2$, the sample variance, instead
of $1$; its error is $\approx \sqrt{2/n}\,|Z|$, $Z \sim N(0,1)$, with median
$0.95/\sqrt n$.

**Constant offsets** (derived). Replacing $\psi_k$ by $\psi_k + d_k$ leaves
$\hat A$ unchanged and shifts $\hat b_k$ by $-d_k\,\hat{\mathbb{E}}_n[h]$.
Since $\hat{\mathbb{E}}_n[h] = O_P(n^{-1/2})$ is not zero, $\hat c$ depends on
the offsets (the centring in $z$, the constants inside $\mathrm{He}_k$) at the
order of the Monte Carlo error itself: they change $\Sigma$, not the rate.
With exact integrals they have no effect.

**Growth with $K$ at fixed $n$** (heuristic). The expansion needs
$A^{-1/2}\hat A A^{-1/2} \approx I$. For $N(0,1)$ the relative variance of the
top diagonal entry of $\hat A$ is $(\kappa_{K-1} - 1)/n$, where
$\kappa_m = \mathbb{E}[\mathrm{He}_m^4]/(m!)^2$ grows like $9^m$
([A.5](#a5-monte-carlo-variance)). Once $\kappa_{K-1} \gg n$, the high-degree
block of $\hat A$ is set by a few extreme draws and is typically
underestimated, $\hat A^{-1}$ amplifies the noise of $\hat b$, and the error
leaves the first-order law by orders of magnitude, with heavy tails across
replications. The Gamma tail is heavier, so the onset should come at smaller
$K$.

## 5. Predictions (C)

Hypotheses for the pilot to check. Errors are relative $L^2(p)$ errors of
$\phi'$; "floor" is what remains as $\Delta x \to 0$.

| # | Hypothesis | Status |
| --- | --- | --- |
| P1 | FD, exact Neumann, Gaussian cases: error $\propto \Delta x^2$ over the whole $N$ sweep, with constants $\sqrt2/24$ (`gauss_mu`) and $\sqrt6/24$ (`gauss_sigma`) at half-nodes | derived |
| P2 | FD, exact Neumann, Gamma cases: $\Delta x^2$ times a power of $\log(1/\Delta x)$; fitted slope slightly below 2 | heuristic |
| P3 | FD, zero flux, $\varepsilon = 10^{-6}$: floors $1.5\times10^{-3}$ (`gauss_mu`), $7.0\times10^{-3}$ (`gauss_sigma`), $4.6\times10^{-4}$ (`gauss_sin`), $2.4\times10^{-3}$ (`gamma_shape`), $6.8\times10^{-3}$ (`gamma_scale`) | derived |
| P4 | Under zero flux, second order shows only on the coarsest grids ($N \lesssim 60$ for `gauss_mu`) | derived for `gauss_mu`, heuristic otherwise |
| P5 | $\varepsilon$ sweep, error on the solver's own $[a, b]$: slope $\tfrac12$; logarithmic factor for `gauss_sigma` and Gamma; `gauss_sin` modulated by $\lvert\sin b\rvert$ | derived (leading order) |
| P6 | $\varepsilon$ sweep, error on the fixed $[a_0, b_0]$, $\varepsilon < \varepsilon_0$: slope 1 | derived (leading order) |
| P7 | Galerkin, $n = \infty$: basis errors of the Section 4 table (full-line column); smaller on $[a_0, b_0]$ | derived |
| P8 | Galerkin, $n = \infty$, Gamma, $K = 12$, unnormalised $\mathrm{He}_k$: the solve is numerically rank-deficient unless the basis is rescaled | derived bound on $\mathrm{cond}(A)$, heuristic consequence |
| P9 | Galerkin, small $K$: error $\propto n^{-1/2}$ down to the basis floor; $n \times$ squared error converges in law to a variable with mean $K + \sum_{k \le K} 1/k$ (`gauss_mu`) and $K^2 + 4K + 2\sum_{k \le K} 1/k$ (`gauss_sigma`); medians lie below | derived (asymptotic in $n$) |
| P10 | Linear cases are not exact at finite $n$; `gauss_mu`, $K = 1$: median error $0.95/\sqrt n$ | derived |
| P11 | Instability in $K$ at small $n$ once $\kappa_{K-1} \gg n$: onset near $K = 6$ for $n = 10^2$, $K = 8$ for $n = 10^3$, between $K = 8$ and $12$ for $n \ge 10^4$ (Gaussian); earlier for Gamma | heuristic |
| P12 | `gauss_sin`, `gamma_shape`: the best $K$ increases with $n$ (basis floor against Monte Carlo term) | derived structure, heuristic location |

## Appendix A: derivations (C)

### A.1 gauss_sin

Completing the square,
$\int_{-\infty}^x e^{iy}p(y)\,dy = \tfrac12 e^{-1/2}\,
\mathrm{erfc}((i - x)/\sqrt2)$; its imaginary part is $q(x)$. For the series,
the generating function $e^{tx - t^2/2} = \sum_k \mathrm{He}_k(x)\,t^k/k!$ at
$t = i$ gives
$\sin x = e^{-1/2}\sum_j (-1)^j\,\mathrm{He}_{2j+1}(x)/(2j+1)!$. Under
$N(0,1)$, $\mathrm{He}_k'' - x\,\mathrm{He}_k' = -k\,\mathrm{He}_k$ and
$\mathrm{He}_k' = k\,\mathrm{He}_{k-1}$, so a coefficient $s_k$ of $h$ on
$\mathrm{He}_k$ gives the coefficient $-s_k$ of $\phi'$ on $\mathrm{He}_{k-1}$.
With $\|\mathrm{He}_m\|^2 = m!$, the squared components of $\phi'$ are
$e^{-1}w_j$, so $\|\phi'\|^2 = e^{-1}\sum_j w_j \approx 0.389$, and the
projection on $\mathcal{P}_{K-1}$ keeps the terms with $2j \le K-1$. The tail
expansion follows from $\phi'(x) = -\frac1p\int_x^\infty \sin y\;p\,dy$ and
two integrations by parts with $p' = -x\,p$.

### A.2 gamma_shape

Here $F(y) = 1 - (1+y)e^{-y}$ and $h = 1 - \gamma - \log y$. Integrating by
parts against $dF$,
$q(x) = (1 - \gamma - \log x)\,F(x) + \int_0^x F(y)/y\,dy$, and
$\int_0^x F(y)/y\,dy = E_1(x) + \log x + \gamma - 1 + e^{-x}$. Dividing by
$p = xe^{-x}$ gives the formula of Section 2; the expansions follow from
$E_1(x) = -\gamma - \log x + x - x^2/4 + \dots$ and $e^xE_1(x) \sim 1/x$.

The orthogonal polynomials of $p = xe^{-x}$ are the Laguerre polynomials
$L_m^{(1)}$, with $\|L_m^{(1)}\|^2 = m+1$. Since
$(L_{m+1}^{(0)})' = -L_m^{(1)}$ and $q$ vanishes at both ends,
$\mathbb{E}_p[\Phi_\alpha L_m^{(1)}] = \int q\,L_m^{(1)}\,dx
= \mathbb{E}_p[h\,L_{m+1}^{(0)}]$. Differentiating
$\int_0^\infty x^{s-1}e^{-x}L_j^{(0)}\,dx = \Gamma(s)\,(1-s)_j/j!$ in $s$ at
$s = 2$ gives $\int_0^\infty \log x \cdot xe^{-x}L_j^{(0)}\,dx = 1/(j(j-1))$
for $j \ge 2$. Hence $\mathbb{E}_p[\Phi_\alpha L_m^{(1)}] = -1/(m(m+1))$ for
$m \ge 1$, and $\mathbb{E}_p[\Phi_\alpha] = \partial_\alpha(\text{mean}) = 1$
for $m = 0$. The squared components are $v_m = 1/(m^2(m+1)^3)$, so
$\|\Phi_\alpha\|^2 = 1 + \sum_{m \ge 1} v_m \approx 1.137$ and
$\sum_{m \ge K} v_m \approx 1/(4K^4)$.

### A.3 FD quadrature error

The sum is the trapezoid rule on $[a, x_j]$ plus a left-endpoint rectangle on
$[x_j, x_{j+1/2}]$. The Euler-Maclaurin formula gives the error
$\frac{\Delta x^2}{12}(g'(x_j) - g'(a)) + O(\Delta x^4)$ for the first, and a
Taylor expansion gives $-\frac{\Delta x^2}{8}g'(x_j) + O(\Delta x^3)$ for the
second; their sum is $E_j$. For `gauss_mu`, $g'/p = x^2 - 1$ with norm
$\sqrt2$; for `gauss_sigma`, $g'/p = x^3 - 3x$ with norm $\sqrt6$; the term in
$g'(a)$ is $O(p(a))$ and is dropped. For the Gamma cases $p(x) \approx x$ at
the lower end while $g'(0) \ne 0$, so $E_j/p \sim \Delta x^2/x$ there and
$\int E^2/p\,dx$ picks up $\int dx/x$: a factor $\log(1/\Delta x)$ for
`gamma_scale`, and more for `gamma_shape`, where $g' \sim -\log x$. These
logarithms are not tracked rigorously.

### A.4 Truncation error

With $\bar h_\varepsilon = \int_a^b hp\,dx/(1 - 2\varepsilon)$ the mean of $h$
on $[a, b]$: $\phi'_\varepsilon = \frac1p\int_a^x (h - \bar h_\varepsilon)p\,dy$
and $\phi' = \frac1p(q(a) + \int_a^x hp\,dy)$. Subtracting, with
$\bar h_\varepsilon(1 - 2\varepsilon) = q(b) - q(a)$, gives the formula.

For the norm, $1/p$ is concentrated near the ends. Where
$|(\log p)''| \ll \lambda^2$, $\int_a 1/p\,dx \approx 1/(p(a)\lambda(a))$ and
$\varepsilon \approx p(a)/\lambda(a)$, so the end $a$ contributes
$q(a)^2/(p(a)\lambda(a)) \approx \varepsilon\,\phi'(a)^2$; the cross term is of
higher order. This holds at both Gaussian ends and at the upper Gamma end. For
`gauss_mu` the integral is exact:
$\|\phi'_\varepsilon - 1\|_{[a,b]}^2 = 2\sqrt2\,p(b)\,D(b/\sqrt2)$, with $D$
the Dawson function.

On the fixed interval the integral starts at $a_0$ and the end contributes
$q(a)^2/(p(a_0)\lambda(a_0))$, with $q(a) \approx \phi'(a)\lambda(a)\varepsilon$
and $p(a_0) \approx \lambda(a_0)\varepsilon_0$:

$$
\|\phi'_\varepsilon - \phi'\|_{[a_0,b_0]} \approx
\frac{\varepsilon}{\sqrt{\varepsilon_0}}
\Big(\phi'(a)^2\,\tfrac{\lambda(a)^2}{\lambda(a_0)^2}
+ \phi'(b)^2\,\tfrac{\lambda(b)^2}{\lambda(b_0)^2}\Big)^{1/2} .
$$

### A.5 Monte Carlo variance

From $\hat A\hat c = \hat b$ and $Ac = b$:
$A(\hat c - c) = (\hat b - b) - (\hat A - A)c - (\hat A - A)(\hat c - c)$. The
first two terms are $\hat{\mathbb{E}}_n[\xi]$ and the last is $O_P(n^{-1})$.
Also $\|\hat\phi_K' - \phi_K'\|^2 = (\hat c - c)^\top A\,(\hat c - c)$.

$\mathrm{tr}(A^{-1}\Sigma)$ is invariant under invertible linear changes of
basis, so take $\psi_k = \mathrm{He}_k/\sqrt{k \cdot k!}$ under $N(0,1)$, for
which $A = I$ (in the unnormalised basis $A = \mathrm{diag}(k \cdot k!)$). The
sample standardisation moves the offsets of $\psi_k$ by $O_P(n^{-1/2})$, hence
$\hat c$ by $O_P(n^{-1})$ only, so $\xi$ may use the population mean and sd.
For `gauss_mu`,
$\xi_k = x\psi_k - \psi_k' = \mathrm{He}_{k+1}/\sqrt{k \cdot k!}$, with
variance $(k+1)/k$. For `gauss_sigma`,
$\xi_k = (\mathrm{He}_{k+2} + k\,\mathrm{He}_k)/\sqrt{k \cdot k!}$, with
variance $(k+1)(k+2)/k + k$. Summing over $k \le K$ gives the two traces.

For the fourth moment, $\mathrm{He}_m^2 = \sum_r \binom{m}{r}^2 r!\,
\mathrm{He}_{2m-2r}$ gives
$\kappa_m = \sum_{r=0}^m \binom{m}{r}^2\binom{2(m-r)}{m-r}$, which grows like
$9^m$ up to a polynomial factor: $\kappa_{K-1} = 93$, $4.7\times10^3$,
$2.7\times10^5$, $1.2\times10^9$ for $K = 4, 6, 8, 12$. The recorded
$\mathrm{cond}(\hat A)$ is dominated by the scaling $K \cdot K!$ of the
unnormalised basis; only its excess over $\mathrm{cond}(A)$ reflects sampling.

## Appendix B: open points in the specification (C)

These change how the predictions are read; none is decided here.

- **Interval of the $\varepsilon$ sweep.** P5 or P6 applies according to
  whether the error is taken on the solver's $[a, b]$ or on $[a_0, b_0]$; for
  $\varepsilon > \varepsilon_0$ only the former is possible.
- **Zero flux at $\varepsilon = \varepsilon_0$.** The default FD run has a
  floor of $10^{-3}$ to $10^{-2}$ (P3). On $[a_0, b_0]$, a floor of $10^{-6}$
  needs $\varepsilon \approx 10^{-9}$, or exact Neumann data.
- **Neumann variant.** $T[hp]$ differs from $q(b) - q(a)$ by $O(\Delta x^2)$,
  so the system stays incompatible; Section 3 assumes the same recentring
  absorbs the defect.
- **End half-cells.** How $\phi'$ is defined on $[a, x_{1/2}]$ and
  $[x_{N-3/2}, b]$ (extrapolation, or the boundary value $q_a/p(a)$) is not
  specified.
- **Scaling of the basis.** With unnormalised $\mathrm{He}_k$ and Gamma, an
  SVD-based least-squares solve at $K = 12$ truncates singular values, a
  regularisation the plan excludes. Rescaling to $\mathrm{diag}(\hat A) = 1$
  leaves the Galerkin solution unchanged in exact arithmetic.
