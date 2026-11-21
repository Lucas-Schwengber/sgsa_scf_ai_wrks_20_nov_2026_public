---
title: Pilot plan for FD and Galerkin against the 1D closed form
created: 2026-11-19
updated: 2026-11-19
authors: Lucas da Rocha Schwengber (L), CLAUDE (C)
---

# Pilot plan

Decisions from the design interview of 2026-11-19 on the goal in
[instructions.md](../instructions.md). C proposed each option and L chose; every item
below is a choice L confirmed.

## Problem (L+C)

Let $p$ be a probability density on $\mathbb{R}$ and $h$ a function with
$\mathbb{E}_p[h] = 0$. We solve for $\phi$ in

$$
\phi'' + \phi' \, (\log p)' = h ,
\qquad\text{equivalently}\qquad (p\,\phi')' = h\,p ,
$$

with zero flux $p\,\phi' \to 0$ at the ends of the support. The closed form is

$$
\phi'(x) = \frac{1}{p(x)} \int_{-\infty}^{x} h(y)\,p(y)\,dy .
$$

For a parametric family $p_\theta$ with CDF $F_\theta$ and
$h = -\partial_\theta \log p_\theta$, this gives
$\phi' = -\partial_\theta F_\theta / p_\theta = \partial_\theta F_\theta^{-1}(F_\theta(x))$,
the transport linearization $\Phi_\theta$ of Trillos, Jaffe and Sen (2025,
Definition 4.1 and Section 6.1). The thread note writes $h$ with the opposite
sign and without the derivative on $\log p$; the convention above is the one
we use.

- The backend accepts any centred $h$. The pilot uses $h = -$score plus one
  extra case.
- The compared quantity is $\phi'$, not $\phi$ (which is defined up to a
  constant).

## Pilot cases (L+C)

| Case | $p$ | $h$ | Exact $\phi'$ |
| --- | --- | --- | --- |
| `gauss_mu` | $N(0,1)$ | $-\partial_\mu \log p$ | $1$ |
| `gauss_sigma` | $N(0,1)$ | $-\partial_\sigma \log p$ | $x$ |
| `gauss_sin` | $N(0,1)$ | $\sin x$ | not polynomial |
| `gamma_shape` | Gamma(shape 2, scale 1) | $-\partial_{\text{shape}} \log p$ | not polynomial |
| `gamma_scale` | Gamma(shape 2, scale 1) | $-\partial_{\text{scale}} \log p$ | $x$ |

Three of the four score cases have $\phi'$ linear in $x$, so polynomial
Galerkin is exact for them up to Monte Carlo noise; `gauss_sin` and
`gamma_shape` are the informative cases.

## Methods (L+C)

**Ground truth.** One generic routine: adaptive quadrature of $h\,p$ from the
nearer tail, divided by $p$. Unit tests compare it with the exact formulas in
the table and with $\theta$-differences of the CDF for `gamma_shape`.

**Score $h$.** A `Family` wrapper around `scipy.stats`. The default score is a
central difference in $\theta$ of `logpdf`; a family can override it with the
exact formula. Gaussian and Gamma have exact overrides.

**Finite differences.** FD knows $p$ analytically.

- Domain $[a, b] = [F^{-1}(\varepsilon), F^{-1}(1-\varepsilon)]$, uniform grid
  of $N$ nodes in $x$.
- Conservative scheme for $(p\,\phi')' = h\,p$ with $p$ at half-nodes;
  unknown $\phi$; $\phi'$ read off as $(\phi_{i+1}-\phi_i)/\Delta x$.
- Boundary condition: zero flux at both ends, with $h$ recentred by its
  truncated mean so the system is solvable, and $\phi$ pinned at one node.
- Diagnostic variant: exact Neumann data from the closed form, to separate
  truncation error from discretisation error.

**Galerkin.** Galerkin sees $p$ only through $n$ i.i.d. draws $x_1,\dots,x_n$;
$h$ is evaluated exactly at the draws.

- Basis $\psi_1,\dots,\psi_K$: probabilists' Hermite polynomials of degree
  $1..K$ in $z = (x - \text{sample mean})/\text{sample sd}$, for every family.
  The basis is an injectable object.
- Weak form $\hat A c = \hat b$ with
  $\hat A = \frac1n \sum_i \psi'(x_i)\psi'(x_i)^\top$ and
  $\hat b = -\frac1n \sum_i h(x_i)\,\psi(x_i)$, the same draws for both.
- Least-squares solve, no regularisation; $\mathrm{cond}(\hat A)$ is recorded.
- Reference run "$n = \infty$" with deterministic quadrature, to separate
  basis error from Monte Carlo error.

## Experiment (L+C)

- **Error.** Relative $L^2(p)$ error of $\phi'$ on the common interval
  $[a, b]$ with $\varepsilon = 10^{-6}$, on a shared deterministic evaluation
  grid (not the Monte Carlo draws). Galerkin's full-line error is an extra
  column.
- **FD sweep.** $N = 25 \cdot 2^j$, $j = 0..7$; an $\varepsilon$ sweep
  ($10^{-2}$ to $10^{-8}$) at the finest grid.
- **Galerkin sweep.** $K \in \{1,2,3,4,6,8,12\}$,
  $n \in \{10^2, 10^3, 10^4, 10^5\}$, 100 seeded replications, plus the
  $n = \infty$ reference. Report the median and the 10–90% band.

## Code and files (L+C)

| Path | Contents |
| --- | --- |
| `src/global/ot_1d/` | Reusable package, installed editable (`import ot_1d`) |
| `ot_1d/families.py`, `problem.py`, `metrics.py` | Shared contract, written first by C |
| `ot_1d/ground_truth.py`, `fd.py`, `galerkin.py` | One sub-agent each, with its test file in `src/tests/` |
| `src/experiments/benchmark_gt/pilot/` | Sweep and figure scripts |
| `outputs/runs/benchmark_gt/pilot/YYYY-MM-DD_<slug>/` | Raw results and config (gitignored) |
| `outputs/summaries/benchmark_gt/pilot/` | Figures and summary table (tracked) |
| [theory.md](../theory.md) | Fourth sub-agent: derivations and predicted rates |
| [lit_review.md](../lit_review.md) | Fifth sub-agent: papers that solve or mention a similar equation |
| `report.md` | Pilot results |

- **Environment.** `.venv/` at the repo root with prompt `ot_1d`;
  `requirements.txt` exported with `pip freeze`.
- **Git.** Step commits on branch `test`, no push.

## Out of scope for the pilot (L+C)

Adaptive FD meshes, non-polynomial or family-matched bases, regularised
Galerkin, sample-only FD, and the other `scipy` families. They stay in the
thread goal.
