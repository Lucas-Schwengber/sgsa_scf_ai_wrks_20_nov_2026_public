---
title: Literature on the 1D weighted Poisson equation
created: 2026-11-19
updated: 2026-11-20
authors: CLAUDE (C)
---

# Literature on the 1D weighted Poisson equation

Papers that solve, use or mention the equation of this thread
([instructions.md](instructions.md)) or a close relative. Notation and sign convention are
those of [theory.md](theory.md); the open problems are those of
[report.md](pilot/report.md).

## Scope and method (C)

**Equation.** For a density $p$ on $\mathbb{R}$ with CDF $F$ and $h$ with
$\mathbb{E}_p[h] = 0$, find $\phi$ with $(p\,\phi')' = h\,p$ and zero flux
$p\,\phi'$ at the ends of the support. Closed form:
$\phi'(x) = \frac{1}{p(x)}\int_{x_-}^{x} h\,p\,dy$. For
$h = -\partial_\theta \log p_\theta$, $\phi' = \Phi_\theta =
-\partial_\theta F_\theta / p_\theta$, the transport linearization of Trillos,
Jaffe and Sen. In every table the paper's own symbols are mapped to
$p, h, \phi, \Phi_\theta, F_\theta$.

**Search.** Done on 2026-11-19 and 2026-11-20. Seeds: the reference list of
the reference paper and the six communities named in the task. Sources: the
arXiv API, Crossref, OpenAlex, Semantic Scholar and a web search engine.

**Second pass.** Done on 2026-11-20, starting from the section
[Leads not substantiated](#leads-not-substantiated-c) and from the rows marked
*abstract only* or *secondary*. Same sources and same verification rule.

- **Covered.** (i) The leads named but not read in the first pass. (ii) A
  search for accessible full texts of [PV01], [LK80], [Tan93], [SW09] and
  [Rei11]. (iii) New searches on domain truncation, conservative finite
  differences, explicit 1D formulas and Galerkin methods with Monte Carlo
  integrals. (iv) One-dimensional Poincaré and Hardy criteria, control variates
  trained by stochastic optimisation, and the papers that cite [LZ23] and
  [TJS25] (lists from OpenAlex).
- **Result.** 18 rows added (15 papers read, 3 known only through other
  papers) and 2 rows upgraded ([Tan93], [SW09]). The added rows are those
  after [AGLM20], [RS18], [Nus24] and [CM17] in their tables.
- **Full texts not on arXiv** were read from the journal's site ([SW09]), from
  an author's page ([Tan93], [BY09]) or from a manuscript copy on a university
  course page ([Ott01]); the evidence cell says so.
- **Zotero.** In the added rows the column "in Zotero" is `yes (KEY)` when a
  title search found the item on 2026-11-20 and `no` otherwise. The second
  pass added nothing to Zotero: its 18 references that are not in the library
  (15 rows marked `no` and 3 secondary sources of the appendix) were left
  out, because the instruction to add citations to Zotero was withdrawn
  before they were added.

**Verification rule.**

- Every paper below was checked against a bibliographic record fetched in this
  session (arXiv API for preprints, Crossref for DOIs): authors, title, year,
  venue, identifier.
- Every statement about a paper's content carries an evidence level in the
  tables: *paper* (read in the full text, with the section or equation number;
  for papers with an arXiv version the numbers are those of the arXiv version),
  *abstract only*, *secondary* (stated by another paper that was read) or
  *inferred* (our reading, not a statement of the paper).
- Mappings to our notation and all signs were worked out by us; where a paper's
  own signs are inconsistent this is said.

**Zotero.** The column "in Zotero" gives the state of the library on
2026-11-20, with item keys: `yes (KEY)` for the 15 papers a title search found
already there, `added (KEY)` for the 19 added by this review. The added items
carry the tag `benchmark_gt`, hold metadata only (no PDF) and are filed in the
existing topic collection that fits best. Sixteen were added by the DOI of the
published version and three ([NM25], [FMM18], [JO18]) from their arXiv page.

**Independent check.** On 2026-11-20 the 34 rows of the first pass were
checked against the papers by a separate reviewer (an Opus sub-agent that saw
only the note): the 29 rows with evidence level *paper* against the arXiv full
text, the others against their abstracts. No sign or mapping was found wrong;
25 statements were corrected, of which five contradicted the source ([TJS25]
for the current arXiv version, [MSI13], [OGC17], [AM24], and the explanation
of the pilot's exactness under "Choice of basis") and the rest were
overclaims, wrong locations or inferences presented as statements of a paper.
The rows and paragraphs added in the second pass have not had this check.

**Tables.** Rows are papers. Columns: reference (key of the
[appendix](#appendix-references-c)), identifier, form of the equation in our
notation, method (and whether integrals come from samples), evidence, in
Zotero.

## Summary (C)

1. **The equation is in the literature under the name "Poisson equation for
   the Wasserstein score function".** Li and Zhao state
   $\Delta\phi + \nabla\log p\cdot\nabla\phi = -\partial_\theta\log p$
   (Proposition 4) and its 1D solution $\phi' = -\partial_\theta F/p$
   (Proposition 6). The Poisson reading of [theory.md](theory.md) is therefore
   not new. The reference paper cites [LZ23]; its first arXiv version does not
   use the name, but the current one (v2) does, attributing the Poisson
   equation to [LZ23] [LZ23, CL20, TJS25].
2. **The closed form is the inverse Stein operator of the density approach.**
   $\mathcal{T}_p^{-1}h = \frac1p\int_{x_-}^{x} h\,p$ in Ley, Reinert and
   Swan; the Stein kernel is the case $h = \text{mean} - x$. Two further forms
   exist: one with the centring of $h$ built in, and a kernel form
   $\phi'(x) = -\frac{1}{p(x)}\int K(x,y)\,h'(y)\,dy$ with
   $K(x,y) = F(x\wedge y) - F(x)F(y)$ [LRS17, Sau19, ERS20].
3. **The feedback particle filter literature already runs a closely related
   experiment in 1D.** The gain function solves the same equation, with an
   observation function in place of a score. Its scalar closed form is turned
   into a sample-based solver in [YMM13] and is the reference for Galerkin,
   kernel and neural solvers that only see samples
   [YLMM12, TM16, TMM17, TMM20, OTM20].
4. **What those comparisons found is consistent with the pilot.** With the
   polynomial basis $\{x, \dots, x^M\}$ and 200 samples, the Galerkin gain
   oscillated and changed sign as $M$ grew [TM16], as large $K$ did in the
   pilot. A sample-based Galerkin matrix for a piecewise-constant gain became
   singular when a cell had no particles [YLMM12]; the pilot has no local
   basis, so this is a failure mode to expect, not one it observed. The
   one-function ("constant gain") solution is the baseline these papers
   compare against and the large-width limit of the kernel solver
   [YLMM12, TM16, TMM20]; that it is the safer choice at small $n$ is our
   reading (*inferred*).
5. **In machine learning the same object is the implicit reparameterization
   gradient** $dz/d\theta = -\partial_\theta F_\theta(z)/q_\theta(z)$, obtained
   by implicit differentiation of the CDF and tied to the continuity equation
   in [JO18]. These papers give tested ways to compute
   $\partial_\theta F$ when it is not elementary, e.g. the Gamma shape.
   [FMM18] differentiate the CDF code in forward mode (mean absolute error
   $5.4\times10^{-13}$ in double precision, Table 2), which would need a CDF
   implementation that supports automatic differentiation rather than `scipy`
   as is (*inferred*); [JO18] give fast approximations, not exact values
   [FMM18, JO18].
6. **Control variates solve the same equation from samples by least squares on
   the strong form, with an intercept**, not by Galerkin. The intercept absorbs
   the sample mean of $h$, which is the centring issue of the pilot; for
   Galerkin the analogous device is a Lagrange multiplier
   [MSI13, SOMD23, RS18].
7. **Stability of sample-based projections is governed by
   $K(m) = \sup_x\sum_{k\le m} L_k(x)^2$** for an orthonormal basis $L_k$: the
   empirical Gram matrix is well conditioned when $K(m) \lesssim n/\log n$.
   For Hermite polynomials under a Gaussian $K(m) = \infty$ already for
   $m \ge 2$, so the theory gives no guarantee with plain sampling; a weighted scheme restores
   $n \sim m\log m$ [CDL13, CM17]. This is stated for least squares; the
   transfer to our Galerkin matrix is *inferred*.
8. **Nothing found on zero-flux truncation of this equation.** In the papers
   read, truncation is used without analysis ([CL20] truncates a mixture
   density to $[-15, 15]$; [YLMM12] solves on $D = [-2, 2]$), and none
   analyses the truncation error or its $\sqrt{\varepsilon}$ scaling. The
   first pass did not go far into the artificial-boundary-condition
   literature (item 9 reports the second pass). The closest material is the
   theory of asymptotic boundary conditions for boundary value problems on
   infinite intervals [LK80, abstract only].
9. **Second pass: zero-flux truncation is still unanalysed, but its
   ingredients exist.** A more specific search again found no error estimate
   in the truncation level (queries in
   [Leads not substantiated](#leads-not-substantiated-c)). What exists:
   the Poincaré constant does not increase under restriction to a subinterval,
   so the truncated zero-flux problem is well posed uniformly in $\varepsilon$
   ([RBI17], Lemma 4; the application is *inferred*); schemes of the pilot's
   type are analysed on an infinite grid, with no truncation [BV18]; the
   survey [SW09] sets truncation aside; papers that compute truncate without
   analysis [CL20, NLY23].
10. **Second pass: the FD scheme of the pilot belongs to a known family**,
    the finite-volume discretisations of the Fokker-Planck operator written
    for the relative density $U = u/\pi$, with a mean of the stationary density
    on each edge. Scharfetter-Gummel is one member [HKS21], and Chang-Cooper
    with exact stationary weights gives the same flux ([PZ17]; the identity is
    *inferred*). The matrices are M-matrices with symmetric weights [HKS21]
    and generators of reversible Markov chains [BV18]. The convergence proofs
    assume a bounded domain and a bounded potential [HKS21].
11. **Second pass: one analysis of a Galerkin method with Monte Carlo
    integrals was found, and it does not transfer.** [KPW19] proves
    convergence for piecewise-linear finite elements with one random point per
    element. Stability is automatic there: gradients are constant on elements
    and the coefficient is bounded below. Nothing was found for a global basis
    with i.i.d. draws from a density on an unbounded domain. Related results
    bound empirical Ritz minimisers over bounded classes on a cube [LLW21] or
    give convergence with probability 1 only [BY09].
12. **Second pass: in 1D the equation is the Poisson equation of a scalar
    diffusion, with the same explicit solution** ([AWS21], eq. C.50). The
    asymptotic variance of $t^{-1/2}\int_0^t h(X_s)\,ds$ along the Langevin
    diffusion is $2\lVert\phi'\rVert^2$ ([vVvZ05], [CCG12]; the constant is our
    computation). For $h = -\partial_\theta\log p_\theta$ this is $2J(\theta)$
    (*inferred*).
13. **Second pass: the reference paper has a sequel that asks for numerical
    solvers.** [JYTS26] defines a "Hellinger-Kantorovich score" by
    $(1-\lambda)\big(\phi'' + \phi'(\log p)'\big) - \lambda\phi = h$; $\lambda = 0$
    is our equation. For $0 < \lambda < 1$ the closed form is lost already for
    the Pareto family, and the authors point to numerical methods for elliptic
    equations without implementing one.

## Wasserstein information geometry (C)

The equation is the definition of the tangent vector of a parametric model in
the Wasserstein (Otto) metric: the potential $\phi$ whose gradient moves
$p_\theta$ to $p_{\theta + d\theta}$. Those that treat 1D use the closed form.
None solves the equation numerically except [AGLM20], which estimates the
Wasserstein natural gradient (not the individual $\phi$) from samples of an
implicit model in any dimension, through a kernelised dual problem.

Rows after [AGLM20] were added in the second pass. Two of them qualify the
sentence above: [NLY23] solves the equation by finite differences on a
truncated domain, and [JYTS26], by the authors of the reference paper, embeds
it in a one-parameter family of equations for which a numerical solver is said
to be the missing piece.

| Reference | Identifier | Form in our notation | Method | Evidence | In Zotero |
| --- | --- | --- | --- | --- | --- |
| [TJS25] | [arXiv:2511.07414](https://arxiv.org/abs/2511.07414) | $\Phi_\theta$ is the velocity at $t = 0$ of the continuity equation along $\theta + t\,e$ (v1 Lemma 4.5). In 1D, $J(\theta) = \int_0^1 (\nabla_\theta F_\theta^{-1})^\top \nabla_\theta F_\theta^{-1}\,du$ (v1 Lemma 6.8, v2 Lemma 6.5), and its proof gives $\Phi_\theta = \nabla_\theta F_\theta^{-1}\circ F_\theta$. v1 does not name a Poisson equation. v2 (Sec. 4, after Def. 4.1) says that the approach of [LZ23] requires solving the "Poisson equation" relating the score and $\Phi_\theta$, and v2 Remark 4.7 characterises $\Phi_\theta$ as the solution of a linearised Monge-Ampère equation. | Closed form in 1D. | paper (arXiv v1): Def. 4.1, Lemma 4.5, Def. 4.6, Lemma 6.8 and its proof (App. C.4); v2: Sec. 4 after Def. 4.1, Def. 4.5, Remark 4.7, Lemma 6.5 | yes (UHK92XWJ; duplicates X4L9DBPK, DEA46SSI) |
| [LZ23] | [doi:10.1007/s41884-023-00099-9](https://doi.org/10.1007/s41884-023-00099-9), [arXiv:1910.11248](https://arxiv.org/abs/1910.11248) | "Wasserstein score function" $\Phi^W_i$: $-\nabla\cdot(p\,\nabla\Phi^W_i) = \partial_{\theta_i} p$, $\mathbb{E}_p\Phi^W_i = 0$ (Def. 3). Prop. 4, named "Poisson equation": $\nabla\log p\cdot\nabla\Phi^W_i + \Delta\Phi^W_i = -\partial_{\theta_i}\log p$. This is our equation with $\phi = \Phi^W_i$, $h = -\partial_{\theta_i}\log p$. Prop. 6 (1D): $\Phi^W_i(x) = -\int^x \partial_{\theta_i}F/p\,dz$, so $\phi' = \Phi_\theta$. | Closed form; analytic 1D examples (Gaussian, exponential, Laplace, uniform, semicircle). No numerical solver. | paper: Def. 3, Prop. 4, Prop. 6, Sec. 2.3 | yes (GHNGYVNC preprint, 7FPY4YDC journal) |
| [CL20] | [doi:10.1007/s41884-020-00028-0](https://doi.org/10.1007/s41884-020-00028-0), [arXiv:1805.08380](https://arxiv.org/abs/1805.08380) | $-\nabla\cdot(\rho\,\nabla\Phi) = \langle\nabla_\theta\rho, \xi\rangle$ (Assumption 1: Neumann condition if $\Omega$ is compact; for $\Omega = \mathbb{R}^n$ instead $\int\rho\lvert\nabla\Phi\rvert^2 < \infty$ and $\int\rho\,\Phi^2 < \infty$, eq. 6): ours with $h = -\langle\nabla_\theta\log\rho, \xi\rangle$. Prop. 5 ($\Omega = \mathbb{R}$, the second case): $G_W(\theta) = \int\frac1\rho(\nabla_\theta F)^\top\nabla_\theta F\,dx$. Its proof writes $\langle\nabla_\theta\rho,\xi\rangle = (\rho\Phi_\xi')'$, the opposite sign to Assumption 1 and Def. 2, and gets $\Phi_\xi' = \langle\nabla_\theta F,\xi\rangle/\rho$; with the sign of Assumption 1, $\Phi_\xi' = -\langle\nabla_\theta F,\xi\rangle/\rho$, our $\Phi_\theta$ in direction $\xi$. $G_W$ does not depend on the sign. | Closed form, used for natural-gradient descent; one experiment truncates the density to $[-15, 15]$. | paper: Sec. 1, Assumption 1 (eq. 6), Def. 2, Sec. 3.3 Prop. 5, Sec. 4.2 | added (DNPAMQKA) |
| [AM24] | [doi:10.1007/s41884-024-00139-y](https://doi.org/10.1007/s41884-024-00139-y), [arXiv:2307.12508](https://arxiv.org/abs/2307.12508) | Eq. (11), called "Poisson equation": $\nabla\log p\cdot\nabla S^W_i + \Delta S^W_i + \partial_i\log p = 0$; $\phi = S^W_i$. $x\mapsto x + \delta\,\nabla S^W_i$ is the infinitesimal optimal map. | Closed form only for elliptically symmetric deformation models, $p = \lvert\Lambda\rvert\,g(\lVert\Lambda(x-\mu)\rVert)$ with $\Lambda$ symmetric positive definite (Theorem 1: $S^W$ quadratic in $x$); the general affine deformation model is left open (Sec. 5). The conclusion asks for "approximation techniques for the Wasserstein score". | paper: Sec. 3 eq. (9), (11)-(12), Sec. 5 Theorem 1, Sec. 7 | yes (J3RMD7DT) |
| [NM25] | [arXiv:2506.12732](https://arxiv.org/abs/2506.12732) | Eq. (1): $\partial_{\theta_i}p + \nabla\cdot(p\,\nabla\Phi_i) = 0$, $\mathbb{E}\Phi_i = 0$; $\phi = \Phi_i$. Location family: $\Phi = x - \theta$ ($\phi' = 1$); scale family: $\Phi = x^2/(2\theta) - \theta/2$ ($\phi' = x/\theta$). | Closed forms. | paper: Sec. 2 eq. (1), Sec. 3, Sec. 4 eq. (9) | added (47ERC736) |
| [AGLM20] | [arXiv:1910.09652](https://arxiv.org/abs/1910.09652) | Def. 2: $\partial_i\rho_\theta = -\mathrm{div}(\rho_\theta\,\varphi_i)$ with $\varphi_i = \nabla f_i$; $\phi = f_i$, same $h$ as [LZ23]. | Legendre-dual (saddle-point) form of the metric, restricted to a reproducing kernel Hilbert space; Nyström projection on $M$ basis points; expectations from $N$ samples; regularisation and damping. Rate in Theorem 7. | paper: Def. 2, Sec. 2.3, Sec. 3.2-3.4 | yes (8ELGIL4K, 6PVGQKWR) |
| [Ott01] | [doi:10.1081/PDE-100002243](https://doi.org/10.1081/PDE-100002243) | Sec. 1.3: a tangent vector $s$ at the density $\rho$ (a function with $\int s = 0$) is identified with a potential $p_O$, defined up to a constant, by the elliptic equation $-\nabla\cdot(\rho\,\nabla p_O) = s$ (eq. 8); the metric is $g_\rho(s_1, s_2) = \int\rho\,\nabla p_{O,1}\cdot\nabla p_{O,2}$ (eq. 9). Ours with $p = \rho$, $\phi = p_O$, $h = -s/\rho$. For $s = \partial_\theta p_\theta$: $h = -\partial_\theta\log p_\theta$ and $g_\rho(s, s) = \lVert\phi'\rVert^2 = J(\theta)$ (mapping by us). | Formal Riemannian calculus for the porous medium equation. No solver. | paper: Sec. 1.3 eq. (6)-(10), Sec. 4.1 eq. (52)-(56); read in a manuscript copy of the article on a university course page, equation numbers of that copy | yes (QD774VIU) |
| [LR22] | [doi:10.1016/j.spl.2022.109645](https://doi.org/10.1016/j.spl.2022.109645), [arXiv:2202.03217](https://arxiv.org/abs/2202.03217) | Eq. (1): $W_{ij}(\theta) = \mathbb{E}\big[\partial_{\theta_i}F\,\partial_{\theta_j}F/f^2\big]$, the 1D formula of [LZ23]: $\mathbb{E}_p[\Phi_i\Phi_j]$ with $\Phi_i = -\partial_{\theta_i}F/f$. | Closed forms: location-scale family, $W = \mathrm{diag}(1, \int t^2 f_0\,dt)$ (Theorem 1); exponential scale family, $W = 2$ (eq. 12). Skew-normal shape $\alpha$: $W(\alpha)$ is a 1D integral with no closed form (Theorem 3), evaluated numerically. No equation is solved. | paper: Sec. 2 eq. (1), Sec. 4 Theorems 1 and 3, Appendix eq. (11)-(12) | no |
| [NLY23] | [doi:10.1137/22M1477805](https://doi.org/10.1137/22M1477805), [arXiv:2202.06236](https://arxiv.org/abs/2202.06236) | Eq. (2.23), (2.25): the Wasserstein tangent vector $v_i$ is the solution of minimal $L^2_\rho$ norm of $-\nabla\cdot(\rho\,v_i) = \partial_{\theta_i}\rho$: ours with $v_i = \phi'$, $h = -\partial_{\theta_i}\log\rho$. $G^W_{ij} = \int v_i\cdot v_j\,\rho\,dx$. | Finite differences. With $\tilde v = \sqrt\rho\,v$, the operator $B\tilde v = -\nabla\cdot(\sqrt\rho\,\tilde v)$ is discretised by central differences on a uniform grid of a compact rectangle, with zero flux on its boundary; the minimal-norm solution of $By = \partial_{\theta_i}\rho$ is computed by a sparse QR factorisation (Appendix B.1). Gaussian-mixture example on $[-2.75, 7.25]^2$ (Sec. 4.1). The truncation is not analysed. | paper: Sec. 2.5 eq. (2.16)-(2.27), Sec. 3.4, Sec. 4.1, Appendix B.1 | yes (BTACMVBY) |
| [JYTS26] | [arXiv:2610.35858](https://arxiv.org/abs/2610.35858) | Eq. (3), "transport-source equation": $\partial_\theta P_\theta + (1-\lambda)\,\mathrm{div}(\nabla\phi_{\theta,\lambda}\,P_\theta) = \lambda\,\phi_{\theta,\lambda}\,P_\theta$, $0\le\lambda\le1$. Divided by $p_\theta$ (by us): $(1-\lambda)\big(\phi'' + \phi'(\log p)'\big) - \lambda\,\phi = h$ with $h = -\partial_\theta\log p_\theta$. $\lambda = 0$ is our equation, $\phi_{\theta,0}' = \Phi_\theta$; $\lambda = 1$ gives the score; in between a zero-order term is added. | Closed forms: Laplace location family (a second-order ODE, Example 3.5), Gaussian models (Example 3.10, eq. 19), and the Pareto index for $\lambda\in\{0,1\}$ only (eq. 18; for $0<\lambda<1$ the ODE reduces to a modified Bessel equation). Uniqueness for one parameter (Prop. 3.3). Sec. 1.1 and 3.1 say that solving the equation is the only bottleneck and point to numerical methods for linear elliptic equations; none is implemented. | paper: Sec. 1.1 eq. (3), Def. 3.1 eq. (13), Prop. 3.3, Examples 3.9-3.10 | no |

## Pathwise gradients in machine learning (C)

A community not in the initial list. To differentiate
$\mathbb{E}_{q_\theta}[f]$ these papers need $dz/d\theta$ along samples, which
is $\Phi_\theta(z)$.

| Reference | Identifier | Form in our notation | Method | Evidence | In Zotero |
| --- | --- | --- | --- | --- | --- |
| [FMM18] | [arXiv:1805.08498](https://arxiv.org/abs/1805.08498) | Eq. (8): $\nabla_\theta z = -\nabla_\theta F(z\mid\theta)/q_\theta(z) = \Phi_\theta(z)$, by implicit differentiation of the CDF. No PDE is written; Sec. 5 notes that concurrent work views these gradients as solutions of a "transport equation", of which (8) is the unique univariate solution. | $\partial_\theta F$ by forward-mode automatic differentiation of the code that evaluates the CDF. Table 2, Gamma shape: mean absolute error $5.4\times10^{-13}$ in double precision, against $3.2\times10^{-9}$ for central finite differences. App. C eq. (15) gives a ${}_2F_2$ series for $\partial_\alpha$ of the Gamma CDF, usable for `gamma_shape`; the sign printed before the ${}_2F_2$ term is "+" and should be "−" (our check against finite differences, agreement to $10^{-9}$). | paper: Sec. 3 eq. (8), Sec. 4.1 Table 2, Sec. 5, App. B, App. C eq. (15) | added (IBZ3KWP4) |
| [JO18] | [arXiv:1806.01851](https://arxiv.org/abs/1806.01851) | Eq. (10): $dz/d\theta = -\partial_\theta F_\theta(z)/q_\theta(z)$. Eq. (12), the "transport equation" $\partial_\theta q_\theta + \nabla_z\cdot(q_\theta v^\theta) = 0$: ours for $v^\theta = \phi'$. Notes that in 1D the solution is the optimal-transport one. | Approximations of $\partial_\alpha F$ for Gamma and Beta (Taylor expansions, Lugannani-Rice saddlepoint expansion, rational polynomial fits where these fail) and a Dirichlet velocity field built from them (eq. 20). | paper: Sec. 3 eq. (10), Sec. 4.1 eq. (12), Sec. 4.3 footnote 6, Sec. 5 | added (S6NERS27) |

## Stein's method (C)

In the density approach the Stein operator of $p$ is
$\mathcal{T}_p f = (f\,p)'/p$, so our equation is $\mathcal{T}_p\phi' = h$ and
the "Stein equation" is solved by the same integral.

| Reference | Identifier | Form in our notation | Method | Evidence | In Zotero |
| --- | --- | --- | --- | --- | --- |
| [LRS17] | [doi:10.1214/16-PS278](https://doi.org/10.1214/16-PS278), [arXiv:1408.2998](https://arxiv.org/abs/1408.2998) | Eq. (18), inverse Stein operator: $\mathcal{T}_p^{-1}h(x) = \frac{1}{p(x)}\int_a^x h\,p\,du$ for $h$ of mean zero: our closed form, same sign. Stein kernel $\tau_p = \mathcal{T}_p^{-1}(\nu - \mathrm{Id})$, $\nu$ the mean (eq. 10, 49): $\phi'$ for $h = \nu - x$. | Closed form; survey, no numerics. | paper: Sec. 2.1 eq. (6), Sec. 2.2 eq. (10), Sec. 2.4 eq. (17)-(18) and Example 6, Sec. 4.2 eq. (49) | added (XEVK5XLY) |
| [Sau19] | [doi:10.3150/19-BEJ1117](https://doi.org/10.3150/19-BEJ1117), [arXiv:1804.03926](https://arxiv.org/abs/1804.03926) | Eq. (13): $\bar{\mathcal{L}}h = \frac1p\int_x^\infty h\,d\nu - \frac{1-F}{p}\mathbb{E}[h]$; eq. (15): $\bar{\mathcal{L}}h(x) = \frac{1}{p(x)}\int k_\nu(x,y)\,h'(y)\,dy$ with $k_\nu(x,y) = F(x\wedge y) - F(x)F(y)$. In our notation $\phi' = -\bar{\mathcal{L}}h$ (sign worked out by us from eq. 13), with no centring of $h$ needed. The paper's text before (15) calls $\mathcal{T}_\nu f = (fp)'/p$ the inverse of $\bar{\mathcal{L}}$, but (13) gives $\mathcal{T}_\nu\bar{\mathcal{L}}h = -(h - \mathbb{E}h)$, so $\bar{\mathcal{L}} = -\mathcal{T}_\nu^{-1}$ on mean-zero functions: the paper's signs are inconsistent there. Our $\phi' = -\bar{\mathcal{L}}h$ follows (13) and (15) (checked numerically). | Closed forms; weighted Poincaré inequalities with the Stein kernel as weight. | paper: Sec. 2 eq. (6)-(15), Sec. 3.1 | added (VU2X8PGN) |
| [CFP19] | [doi:10.1214/18-AIHP898](https://doi.org/10.1214/18-AIHP898), [arXiv:1703.07707](https://arxiv.org/abs/1703.07707) | Eq. (4), 1D Stein kernel of a centred $\nu$: $\tau_\nu = \frac1p\int_x^\infty y\,p\,dy$: $\phi'$ for $h = -x$. In $\mathbb{R}^d$: $\tau_\nu = \nabla g$ with $\int\langle\nabla g,\nabla f\rangle d\nu = \int x\cdot f\,d\nu$ for all $f$: our weak form. | Existence by Lax-Milgram under a Poincaré inequality, with $\int\lvert\tau_\nu\rvert^2 d\nu \le C_P\int\lvert x\rvert^2 d\nu$; $g$ minimises a Ritz functional. | paper: Sec. 1 eq. (4), Theorem 2.4 and its proof | yes (6IUDW54D) |
| [ERS20] | [doi:10.3150/19-BEJ1182](https://doi.org/10.3150/19-BEJ1182), [arXiv:1906.08372](https://arxiv.org/abs/1906.08372) | Def. 2.4: $\mathcal{L}_p h(x) = \frac{1}{p(x)}\int_a^x (h - \mathbb{E}h)\,p$: our closed form with the centring built in. Lemma 2.19: $-\mathcal{L}_p h(x) = \mathbb{E}\big[K_p(X,x)\,h'(X)/(p(X)\,p(x))\big]$, the same kernel as [Sau19] written as an expectation under $p$. | Closed forms ("probabilistic representations"). | paper: Def. 2.4 eq. (2.6), Lemma 2.19 eq. (2.20), continuous case | yes (BJWLK4RM) |

## Poisson equation for diffusions and control variates (C)

$\phi'' + \phi'(\log p)'$ is the generator of the overdamped Langevin diffusion
$dX = (\log p)'(X)\,dt + \sqrt2\,dW$, whose invariant density is $p$ ([YLMM12],
Sec. I, eq. (7)-(8); [LMMR15], Sec. 2.1, gives the generator and the Poisson
reading). Its Poisson equation gives asymptotic variances and
zero-variance control variates.

Rows after [RS18] were added in the second pass: the explicit one-dimensional
formulas for the solution and for the asymptotic variance, a solver by
stochastic optimisation, and the one-dimensional Poincaré constant, which is
the inverse of the spectral gap of this generator ([RBI17], Theorem 2).

| Reference | Identifier | Form in our notation | Method | Evidence | In Zotero |
| --- | --- | --- | --- | --- | --- |
| [PV01] | [doi:10.1214/aop/1015345596](https://doi.org/10.1214/aop/1015345596) | Poisson equation in $\mathbb{R}^d$ for the generator of an ergodic diffusion; existence, uniqueness and growth bounds in Sobolev classes. That our equation is a special case is *inferred*. | Theory. | abstract only | yes (MHBVMZWL) |
| [MSI13] | [doi:10.1007/s11222-012-9344-6](https://doi.org/10.1007/s11222-012-9344-6), [arXiv:1012.2983](https://arxiv.org/abs/1012.2983) | Eq. (4), "fundamental equation": $H\psi = -\sqrt{\pi}\,(f - \mu_f)$. With their operator (7) and $\psi = P\sqrt\pi$, eq. (8) is $\tilde f = f - \tfrac12(\Delta P + \nabla P\cdot\nabla\ln\pi)$; zero variance means our equation with $p = \pi$, $\phi = P/2$, $h = f - \mu_f$ (rewriting by us). | $P$ a low-degree polynomial; coefficients by variance minimisation (a regression) on MCMC samples. Sufficient conditions for unbiasedness: $\pi\,\partial P/\partial x_j = 0$ on $\partial\Omega$ for bounded $\Omega$ (Prop. 1); vanishing flux $\int_{\partial B_r}\pi\nabla P\cdot n \to 0$ for unbounded support (Prop. 2); in 1D, equal flux $P'\pi$ at the two ends (eq. 10). Example 1 (exponential density, $f = x$): degree 1 violates (10); degree 2 with $a_1 = 0$ gives zero variance. The optimum printed there, $a_2 = 1/(2\lambda)$, does not give zero variance under eq. (8); $a_2 = -1/\lambda$ does, and then $\phi' = P'/2 = -x/\lambda$ is our closed form for $p = \lambda e^{-\lambda x}$, $h = x - 1/\lambda$ (our check). | paper: eq. (4), (7), (8), Sec. 3-4, Sec. 5 Prop. 1-2, eq. (10), Example 1 | yes (E7VZ3ZMJ) |
| [OGC17] | [doi:10.1111/rssb.12185](https://doi.org/10.1111/rssb.12185), [arXiv:1410.2392](https://arxiv.org/abs/1410.2392) | Remark 3: $\nabla_x\cdot[\pi\,\varphi] = (f - \mu(f))\,\pi$ for a vector field $\varphi$ (the "fundamental equation" of [MSI13], eq. 4). In 1D, $\varphi = \phi'$ and $h = f - \mu(f)$. Zero flux $\pi\,\varphi\cdot n = 0$ on $\partial\Omega$ is assumption (A2), a tail condition on unbounded $\Omega$, needed for the control functional to have mean zero (Prop. 2); (A2') builds it into the kernel. Remark 3 notes that the equation alone has infinitely many solutions. That zero flux makes the solution unique in 1D but not for $d > 1$ is *inferred*. | Regularised least squares in a reproducing kernel Hilbert space, from samples. | paper: Sec. 2.2.2 eq. (1), (A2), Prop. 2, (A2'), Lemma 1, Remark 3 | yes (SUHN9S8X) |
| [SOMD23] | [doi:10.1214/22-BA1328](https://doi.org/10.1214/22-BA1328), [arXiv:1811.05073](https://arxiv.org/abs/1811.05073) | Eq. (3): $Lg = \nabla\cdot(p\nabla g)/p = \Delta g + \nabla g\cdot\nabla\log p$, exactly our operator. Eq. (4): minimise $\frac1N\sum_i[\varphi(\theta_i) - c + Lg(\theta_i)]^2 + \lambda\,\mathrm{PEN}(g)$ over $g$ and an intercept $c$: our equation with $\phi = g$, $h = -(\varphi - \mathbb{E}\varphi)$, $c$ estimating the mean. | Polynomial $g$; ordinary, ridge and lasso least squares on the strong form, from samples. Flux condition (5) for unbiasedness. Penalties allow a higher degree when samples are few. | paper: Sec. 2 eq. (3)-(5), Sec. 3.1 | added (637PBKM9) |
| [APV17] | [doi:10.1137/16M1094117](https://doi.org/10.1137/16M1094117), [arXiv:1609.05097](https://arxiv.org/abs/1609.05097) | Eq. (19): $\int\nabla\phi\cdot\nabla v\,e^{-V} = \int f\,v\,e^{-V}$ with centring (20): our weak form with $p\propto e^{-V}$, $h = -f$. | Galerkin in Hermite functions after the transform $\psi = e^{-V/2}\phi$ (Schrödinger form); basis centred at the mean of $p$ and scaled by its covariance times a free factor; Gauss-Hermite quadrature, not samples. Spectral convergence (Theorem 4.2). | paper: Sec. 3 eq. (19)-(22), (31)-(32), Remark 3.1, Theorem 4.2, Sec. 6 | added (84EQK5UV) |
| [RS18] | [doi:10.1051/m2an/2017044](https://doi.org/10.1051/m2an/2017044), [arXiv:1702.04718](https://arxiv.org/abs/1702.04718) | A relative: Galerkin for $-\mathcal{L}\Phi = R$ with $\mathcal{L}$ the generator of underdamped Langevin dynamics. The paper notes that for the overdamped generator (ours) well-posedness of the discrete problem follows from Lax-Milgram and a Poincaré inequality. | Sec. 3.2: when the basis functions do not have mean zero, a saddle-point system with a Lagrange multiplier is well posed, and $R$ need not be centred (Prop. 2); it is well conditioned (Sec. 3.4, eq. 50). Fourier and Hermite bases. Matrix entries from the algebra of the basis (eq. 54-55) and quadrature (Remark 4), not from samples. | paper: Sec. 1, Sec. 3 eq. (19), Prop. 2 eq. (32), Sec. 3.4 eq. (50), Remark 4, Sec. 4.1 | added (T9DDLTUD) |
| [vVvZ05] | [doi:10.1214/009117905000000152](https://doi.org/10.1214/009117905000000152), [arXiv:math/0507412](https://arxiv.org/abs/math/0507412) | Scalar diffusion on an interval $I = (l, r)$ with scale function $s$ and finite speed measure $m$; $\mu = m/m(I)$ is invariant, with CDF $F$. Eq. (1.1): $\sqrt t\,\big(\frac1t\int_0^t f(X_u)\,du - \int f\,d\mu\big)\Rightarrow N(0, \Gamma(f,f))$ with $\Gamma(f,f) = 4\,m(I)\int_I\big[\int_l^x f\,d\mu - F(x)\int_I f\,d\mu\big]^2\,ds(x)$. The bracket is our flux $q(x)$ for $h = f - \int f\,d\mu$. For the Langevin diffusion $ds\propto dx/p$, so $\Gamma = c\,\lVert\phi'\rVert^2$; the paper takes the normalisation of $s$ and $m$ from its references, and Itô's formula gives $c = 2$ (*inferred*, our computation). | Explicit formula, quoted as known. The paper is about uniform (Donsker) versions of this central limit theorem. | paper: Sec. 1 eq. (1.1)-(1.2) | no |
| [AWS21] | [doi:10.1214/20-AIHP1144](https://doi.org/10.1214/20-AIHP1144), [arXiv:1807.11331](https://arxiv.org/abs/1807.11331) | Scalar diffusion $dX = b\,dt + \sigma\,dW$ with invariant density $\rho_b$ and CDF $F_b$. Eq. (C.50): $h_g(u) = \frac{2}{\sigma^2(u)\rho_b(u)}\int g(y)\,\rho_b(y)\,\big(\mathbf{1}\{u>y\} - F_b(u)\big)\,dy$. Itô's formula for $G_g = \int_0^{\cdot}h_g$ gives $\int_0^t\big(g(X_s) - \mathbb{E}_b g\big)\,ds$ plus a martingale: $G_g$ solves the Poisson equation of the diffusion. For $\sigma^2 = 2$, $b = (\log p)'$: $h_g(u) = \frac{1}{p(u)}\int_{-\infty}^u(g - \mathbb{E}_p g)\,p\,dy$, our closed form with $\phi = G_g$, $h = g - \mathbb{E}_p g$, centring built in as in [ERS20] (specialisation by us). | Explicit formula, used for a martingale approximation of additive functionals and for concentration inequalities. | paper: Sec. 4.2 Prop. 8, Appendix C eq. (C.50) and the proof of Prop. 8 | no |
| [CCG12] | [arXiv:1104.2198](https://arxiv.org/abs/1104.2198) | Poisson equation $Lg = f$ with $\int f\,d\mu = 0$ for the generator $L$ of an ergodic Markov diffusion (eq. 3.1): ours for the Langevin generator, $\phi = g$, $h = f$. Theorem 3.7: if $g$ is in the domain of $L$, $\mathrm{Var}_\mu\big(\int_0^t f(X_s)\,ds\big)\sim t\,\mathcal{E}(g)$, with $\mathcal{E}(g) = \int\Gamma(g)\,d\mu = -2\int g\,Lg\,d\mu$ (eq. 2.3). For our generator $\mathcal{E}(\phi) = 2\lVert\phi'\rVert^2$ (evaluation by us). | Theory: $g = -\int_0^\infty P_s f\,ds$ (eq. 3.8); existence in $L^q$ from decay rates of the semigroup (Prop. 3.19-3.20); Kipnis-Varadhan theorem in the reversible case (Theorem 3.13). No explicit 1D formula for the solution: Sec. 5.3 treats dimension one through weak Poincaré inequalities. | paper: Sec. 2 eq. (2.3), Sec. 3 eq. (3.1), (3.8), Theorems 3.7 and 3.13, Sec. 5.3 | no |
| [SODCB22] | [doi:10.1007/978-3-030-98319-2_10](https://doi.org/10.1007/978-3-030-98319-2_10), [arXiv:2006.07487](https://arxiv.org/abs/2006.07487) | Sec. 3.1, "scalar-valued Langevin Stein operator": $\mathcal{L}_{SL}u = \Delta u + \nabla u\cdot\nabla\log\pi$, our operator. Sec. 3.2, "Stein's equation": $\mathcal{L}u^* = f - \Pi[f]$: ours with $\phi = u^*$, $h = f - \Pi[f]$. | $u$ a polynomial, a kernel expansion or a neural network. The parameters minimise an empirical version of $\mathrm{Var}_\Pi[f - \mathcal{L}u]$ (eq. 1) or its least-squares form with an intercept $c$ (eq. 2), plus a penalty, by mini-batch stochastic gradient descent on samples. Prop. 2: conditions on the tails of $\pi$ and the growth of $f$ under which the equation has a solution in $W^{2,2}(\Pi)\cap W^{1,4}(\Pi)$. A fit of the strong form, not Galerkin. | paper: Sec. 2, Sec. 3.1-3.2 eq. (1)-(2), Sec. 4 Prop. 1-2 | no |
| [RBI17] | [doi:10.1214/17-EJS1310](https://doi.org/10.1214/17-EJS1310), [arXiv:1612.03689](https://arxiv.org/abs/1612.03689) | Poincaré constant $C_P(\mu)$ of $\mu(dt) = \rho(t)\,dt$ on an interval: the constant of our energy estimate. Theorem 2 (bounded interval $[a, b]$, $\rho = e^{-V}$ continuous and positive): $C_P = 1/\lambda_1$ for the eigenvalue problem $f'' - V'f' = -\lambda f$, $f'(a) = f'(b) = 0$, our operator with zero flux. Eq. (2.6): $u_k'(x) = \frac{\lambda_k}{\rho(x)}\int_x^b u_k\,\rho\,dt$, our closed form for $h = -\lambda_k u_k$. | Theorem 1, the Muckenhoupt criterion (quoted from Muckenhoupt 1972): $\mu$ has a Poincaré inequality iff $A_-$ and $A_+$ are finite, and $\tfrac12\max(A_-, A_+)\le C_P\le4\max(A_-, A_+)$, where $A_+ = \sup_{x>m}\mu(x,b)\int_m^x\frac{dt}{\rho(t)}$, $m$ a median, and $A_-$ is symmetric. Lemma 4: $C_P$ does not increase under restriction to a subinterval. Prop. 7-8: Neumann spectral gap of the truncated normal, equal to $n+1$ between consecutive roots of $\mathrm{He}_n$ and in general the first zero of a combination of Kummer functions. Sec. 4.2: piecewise-linear finite elements for the weighted eigenvalue problem. | paper: Sec. 2.2 Theorem 1, Sec. 2.4 Theorem 2 eq. (2.6), Sec. 3.1 Lemma 4, Sec. 4.1 Prop. 7-8, Sec. 4.2 | no |

## Nonlinear filtering: the feedback particle filter (C)

The gain function $K$ of the feedback particle filter is $\phi'$ for the
observation function. This is the community closest to the thread: the solvers
see only particles, and the scalar closed form is the benchmark.

| Reference | Identifier | Form in our notation | Method | Evidence | In Zotero |
| --- | --- | --- | --- | --- | --- |
| [YMM13] | [doi:10.1109/TAC.2013.2258825](https://doi.org/10.1109/TAC.2013.2258825), [arXiv:1302.6563](https://arxiv.org/abs/1302.6563) | Eq. (9): $-\partial_x\big(\frac1p\partial_x(pK)\big) = h_o'/\sigma_W^2$ with $pK\to0$ at $\pm\infty$, $h_o$ the observation function: $K = \phi'$ with $h = -(h_o - \hat h_o)/\sigma_W^2$. Closed form (76). | Sec. IV-A, "direct numerical approximation": $K(x) \approx \frac{1}{\tilde p(x)\,\sigma_W^2}\frac1N\sum_j(\hat h_o - h_o(X^j))\,\mathbf{1}\{X^j \le x\}$, with $\tilde p$ a Gaussian kernel density estimate of $p$ (one Gaussian of width $\epsilon$ per particle, eq. 43). Samples only. | paper: eq. (9), Sec. IV-A eq. (43)-(45), eq. (76) | added (C5AWMGDA) |
| [YLMM12] | [doi:10.1109/CDC.2012.6425937](https://doi.org/10.1109/CDC.2012.6425937), [arXiv:1303.1205](https://arxiv.org/abs/1303.1205) | Weak form $\mathbb{E}[K\cdot\nabla\psi] = \mathbb{E}[(h_o - \hat h_o)\psi]$: ours with $h = -(h_o - \hat h_o)$. | Galerkin $A\kappa = b$ with $A$, $b$ from particles; "constant gain" is the case of one basis function. Scalar example: closed form as reference against a piecewise-constant $K$ on $L = 1, 5, 15$ cells with $N = 1000$; at $L = 15$ the particle-based $A$ is singular (a cell has no particles). | paper (conference version): Sec. III-IV. The journal version, [doi:10.1016/j.automatica.2016.04.019](https://doi.org/10.1016/j.automatica.2016.04.019), was not read. | yes (MV4IQUIW; journal version NEZUPP7A) |
| [LMMR15] | [doi:10.1137/13094743X](https://doi.org/10.1137/13094743X), [arXiv:1412.5845](https://arxiv.org/abs/1412.5845) | Eq. (2.6): $\nabla\cdot(\rho\nabla\phi) = -(g - \hat g)\rho$, $\int\phi\rho = 0$: ours with $h = -(g - \hat g)$. Notes that with $U = -\ln\rho$ this is the Poisson equation of the diffusion $d\Phi_t = -\nabla U\,dt + \sqrt2\,dW_t$. | Theorem 2.2: unique weak solution under a Poincaré inequality with constant $\lambda$, and $\int\lvert\nabla\phi\rvert^2\rho \le \frac1\lambda\int\lvert g - \hat g\rvert^2\rho$. | paper: Sec. 2.1 | added (PBYSADBC) |
| [TM16] | [doi:10.1109/CDC.2016.7799105](https://doi.org/10.1109/CDC.2016.7799105), [arXiv:1603.05496](https://arxiv.org/abs/1603.05496) | $-\Delta_\rho\phi = h_o - \hat h_o$, $\Delta_\rho\phi = \frac1\rho\nabla\cdot(\rho\nabla\phi)$: ours with $h = -(h_o - \hat h_o)$. Scalar closed form as reference (Example 2). | (i) Galerkin from samples, with $A$ and $b$ as sample averages (eq. 13-14). Prop. 1: with the first $M$ eigenfunctions of $\Delta_\rho$ as basis, the $L^2$ error in $\phi$ (not in the gain) is at most $\lVert h\rVert_2/\lambda_M$ plus $\varepsilon_N \to 0$ a.s., with no rate in $N$ (eq. 17 as printed squares the right side only; the proof bounds $\lVert\phi - \phi^{(M)}\rVert_2^2$ by $\lVert h\rVert_2^2/\lambda_M^2$). Example 3: $N(\pm1, 0.4^2)$ mixture, $h = x$, basis $\{x, \dots, x^M\}$, $N = 200$: for $M = 3, 5$ the gain oscillates and changes sign, although the exact gain is positive. (ii) Kernel method: fixed point of a Markov matrix built from the samples (diffusion map), no basis. | paper: Sec. II eq. (8), Sec. III eq. (13)-(14), Prop. 1 eq. (17), Remark 1, App. A, Examples 1-3, Sec. IV | yes (UFQR77NR) |
| [TMM17] | [doi:10.23919/ACC.2017.7963661](https://doi.org/10.23919/ACC.2017.7963661), [arXiv:1612.05606](https://arxiv.org/abs/1612.05606) | Sec. II-C, eq. (5): $K(x) = -\frac{1}{\rho(x)}\int_{-\infty}^x\rho\,(h_o - \hat h_o)\,dz$: our closed form. | Bias and variance of the kernel gain as functions of the kernel width $\epsilon$ and $N$. | paper: Sec. II-C, Sec. IV | added (43V73S25) |
| [TMM20] | [doi:10.1137/19M124513X](https://doi.org/10.1137/19M124513X), [arXiv:1902.07263](https://arxiv.org/abs/1902.07263) | Eq. (4.6): same closed form, used as $K_{\text{exact}}$ in the scalar example. | Diffusion-map algorithm: bias from the kernel width (Theorem 4.3), variance from finite $N$ (Theorem 4.4, compact support). Remark 4.6: the variance analysis for unbounded support is open. | paper: Sec. 1, Sec. 4.1-4.3, Sec. 5 | yes (Z27D2EUG, XWTRQ2PW; both items lack authors and date) |
| [OTM20] | [doi:10.1109/CDC42340.2020.9304260](https://doi.org/10.1109/CDC42340.2020.9304260), [arXiv:2010.01183](https://arxiv.org/abs/2010.01183) | $\phi$ minimises $\int(\tfrac12\lvert\nabla f\rvert^2 - (h_o - \hat h_o)f)\,\rho\,dx$ (Ritz form of the same equation). | $f$ a neural network, objective from particles, stochastic gradient descent; compared with the scalar closed form (eq. 15). A linear parametrisation gives back Galerkin. Sec. III-A notes that minimising the empirical Ritz functional over all functions is unbounded below, because the empirical measure has no Poincaré inequality. | paper: Sec. I-IV eq. (3)-(5), (9), (12)-(13), (15), Sec. III-A | added (RQNFS2MQ) |

## Sampling and data assimilation by transport (C)

To move samples along a path of densities $\pi_t$ one needs a velocity $v_t$
with $\partial_t\pi_t + \nabla\cdot(\pi_t v_t) = 0$; with $v_t = \nabla\phi$
this is our equation with $h = -\partial_t\log\pi_t$, to be solved at every
time step from the current samples.

Rows after [Nus24] were added in the second pass.

| Reference | Identifier | Form in our notation | Method | Evidence | In Zotero |
| --- | --- | --- | --- | --- | --- |
| [Rei11] | [doi:10.1007/s10543-010-0302-4](https://doi.org/10.1007/s10543-010-0302-4) | Cited by [MM24] for the result that the minimal-cost velocity is $\nabla u$ with $-\nabla\cdot(\pi_t\nabla u) = \pi_t(\ell - \mathbb{E}_{\pi_t}\ell)$, and by [Nus24], with Daum et al. (2010) and [HDP21], for a proof of [Nus24]'s own Proposition 1, and in Sec. 4.1 among the particle-flow uses of (17). | Not checked. | secondary ([MM24] Sec. 3, [Nus24] Sec. 2 and 4.1); full text and abstract not accessible | added (3MFNF6PD) |
| [HDP21] | [doi:10.1111/rssb.12404](https://doi.org/10.1111/rssb.12404), [arXiv:1509.08787](https://arxiv.org/abs/1509.08787) | Prop. 1, eq. (10): $f(t,x) = -\int_{-\infty}^x\partial_t\pi_t\,du/\pi_t(x)$ solves $\partial_t\pi_t = -(\pi_t f)'$: our closed form with $h = -\partial_t\log\pi_t$ (the score case with $\theta = t$). Shown to be the minimal kinetic energy solution. | 1D integrals of the unnormalised density by composite Newton-Cotes rules (trapezoid with 100 points in Sec. 5.1); in $d > 1$ the 1D formula is applied to full conditionals ("Gibbs flow"). | paper: Sec. 3.1 Prop. 1 eq. (10)-(11), Sec. 3.3 eq. (19), Sec. 4.1 eq. (23)-(25), Sec. 5.1 | added (X3KRUKS5) |
| [MM24] | [arXiv:2401.03892](https://arxiv.org/abs/2401.03892) | Eq. (4): $-\nabla\cdot(\pi_t\nabla u_t) = \pi_t(\ell - \mathbb{E}_{\pi_t}\ell)$, $\ell = \log(\pi_1/\pi_0)$: ours with $\phi = u_t$, $h = -(\ell - \mathbb{E}\ell)$. The right-hand side is the Fisher-Rao gradient flow of $-\mathbb{E}_\mu\ell$, turned into a transport. | $u_t$ in a reproducing kernel Hilbert space; weak form tested against kernel sections (eq. 5); expectations from particles; Tikhonov regularisation of the resulting matrix. | paper: Sec. 3 eq. (3)-(5), Sec. 5.1 | yes (A78KL5UF) |
| [Nus24] | [arXiv:2409.01464](https://arxiv.org/abs/2409.01464) | Eq. (3), "Stein equation": $S_\pi v = \frac1\pi\nabla\cdot(\pi v) = h_\ell - \int h_\ell\,d\pi$: ours for $v = \phi'$. Eq. (17): the "conventional" Poisson equation $-\nabla\cdot(\pi\nabla\phi_N) = \pi(h_\ell - \int h_\ell\,d\pi)$, where the paper's potential gives $v = -\nabla\phi_N$ (Prop. 3), so $\phi_N = -\phi$. | Kernel ridge regression for $v$ from samples (Problem 1, Prop. 2). Remark 4: the kernelised equation (16) is ill posed without regularisation, while (17) is well posed. Sec. 4.1 lists where (17) appears: central limit theorems for Markov processes, nonlinear filtering, particle flows; it notes that the kernelised equation (16) was used implicitly for control variates by [OGC17]. Problem 1 (eq. 5) centres $h$ by its sample mean, as the centred variant of the pilot does. The abstract links the method to birth-death dynamics and Fisher-Rao gradient flows. | paper: Sec. 2 eq. (3), Sec. 3, Sec. 4.1 eq. (16)-(17), Remark 4 | yes (QTSVHSN7) |
| [RC13] | [doi:10.1515/9783110282269.91](https://doi.org/10.1515/9783110282269.91), [arXiv:1208.6572](https://arxiv.org/abs/1208.6572) | Sec. 3.6: Bayes' formula as an evolution in a fictitious time $s\in[0,1]$, $\partial_s\pi = -\pi\,(L - \bar L)$ with $L$ the negative log-likelihood (eq. 54), realised by a continuity equation $\partial_s\pi = -\nabla\cdot(\pi g)$ (eq. 56). Proposition, eq. (57): the velocity of minimal kinetic energy $\frac12\int\pi\,v^\top M^{-1}v\,dx$ comes from a potential $\psi$ with $\nabla\cdot(\pi M\nabla\psi) = \pi\,(L - \bar L)$. Ours with $M = 1$, $\phi = \psi$, $h = L - \bar L$. The survey writes the velocity once as $g = M\nabla\psi$ and once as $-M\nabla\psi$; eq. (54) and (56) give the former (sign check by us). | Solved analytically for a Gaussian $\pi$ (ensemble transform Kalman-Bucy filter) and for Gaussian mixtures with a linear observation operator. Otherwise a mean-field reduction: a scalar equation in the observed variable, $\partial_y(\pi_Y f_y) = \pi_Y\,(L - \bar L)$, and scalar equations for each state component (eq. 58-59). The formulation is attributed to [Rei11]. | paper: Sec. 3.6 eq. (51)-(59) | no |
| [DH08] | [doi:10.1117/12.764909](https://doi.org/10.1117/12.764909) | Particle flow $dx/d\lambda = \mu(x,\lambda)$, $\lambda\in[0,1]$, that moves samples of the prior to the posterior, with $\partial_\lambda p = -\nabla\cdot(\mu\,p)$: ours for $\mu = \phi'$, $h = -\partial_\lambda\log p$. In 1D the zero-flux solution is unique, so any such flow is the closed form (*inferred*). | As reported by the secondary sources, which cite [DH08] among other papers of the same authors: the flows come from simplifying assumptions on $\mu$, not from the elliptic equation $\nabla\cdot(p\,M^{-1}\nabla\psi) = -\partial_\lambda p$; the "exact" flow is affine, $\mu = A(\lambda)\,x + b(\lambda)$, for a Gaussian prior and a linear-Gaussian likelihood. | secondary ([dMMFD15] Sec. 3 eq. (3.1)-(3.3), co-authored by Daum; [LC17] Sec. III eq. (4)-(8)); the original was not accessible | yes (7U8LQNQZ) |

## Numerical analysis (C)

Little here is about the equation itself. These papers concern the two
numerical questions of the pilot: what to do at infinity, and when a basis fed
with random samples is stable.

Rows after [CM17] were added in the second pass. Three of them are about the
operator itself: [HKS21] and [BV18] analyse the family of conservative schemes
to which the FD scheme of the pilot belongs, and [KPW19] is the one analysis
found of a Galerkin method whose matrix is computed from random points.

| Reference | Identifier | Form in our notation | Method | Evidence | In Zotero |
| --- | --- | --- | --- | --- | --- |
| [LK80] | [doi:10.1137/0717049](https://doi.org/10.1137/0717049) | General boundary value problems on semi-infinite intervals; our equation is such a problem for $\phi'$ (*inferred*). | Replace the infinite interval by a finite one with "asymptotic boundary conditions", projections onto the bounded solutions, instead of an ad hoc condition. | abstract only | added (J6SX4RWZ) |
| [Tan93] | [doi:10.1137/0914038](https://doi.org/10.1137/0914038) | Not about our equation. | Hermite functions need a scaling factor $\alpha$, basis $\psi_n(\alpha v)$. Sec. 3, eq. (3.1)-(3.3): for a function of Gaussian type that is negligible outside $[-M, M]$, choose $\alpha$ so that all collocation points $\gamma_j/\alpha$ lie in $[-M, M]$, i.e. $\alpha_N = \max_j\gamma_j/M\approx\sqrt{2N}/M$, $\gamma_j$ the roots of $H_{N+1}$. The paper says that the theory of an optimal scaling factor is incomplete, and recalls that resolving $p$ wavelengths of a sine takes $O(p^2)$ Hermite polynomials (Gottlieb and Orszag). The choice is supported by numerical examples. | paper: Sec. 1-3, eq. (3.1)-(3.3), read in the scan on the author's page (Greek letters are lost in its text layer); second pass. Also described in [APV17], Remark 3.1 | added (GSL62GG6) |
| [SW09] | [doi:10.4208/cicp.2009.v5.p195](https://doi.org/10.4208/cicp.2009.v5.p195) | Not about our equation. The generic model problem is $\gamma u - \partial_x(a\,\partial_x u) = f$ on the line (eq. 2.46), which contains our divergence form for $\gamma = 0$, $a = p$, $f = -hp$ (*inferred*); the error estimates are for $\gamma u - \partial_x^2u = f$ with $\gamma > 0$ (eq. 2.51 and 4.27, Theorems 2.3 and 4.8), and the paper notes that well-posedness is not guaranteed for all $\gamma\ge0$. | Unified analysis and comparison of mapped Jacobi, Laguerre and Hermite spectral methods on unbounded domains, by decay of the solution. Sec. 1: domain truncation "is only a viable option" for exponentially decaying solutions or with accurate boundary conditions at the truncated boundary, and is not treated. Theorem 4.1: the Hermite projection error in the Gaussian-weighted norm is $\lesssim N^{(k-m)/2}\lVert\partial_x^m u\rVert_\omega$ for the $k$-th derivative, an algebraic rate set by the weighted regularity $m$. Sec. 6.3: scaling $y = \beta x$ with $\beta_N = x_N/M$, $x_N$ the largest node and $\lvert u\rvert\le\varepsilon$ beyond $M$. | paper: Sec. 1, Sec. 2.5, Theorem 4.1, Sec. 4.3, Sec. 6.3, read on the journal's site; second pass | added (QJPNMCSF) |
| [CDL13] | [doi:10.1007/s10208-013-9142-3](https://doi.org/10.1007/s10208-013-9142-3), [arXiv:1111.4422](https://arxiv.org/abs/1111.4422) | Least-squares projection onto an $m$-dimensional space from $n$ i.i.d. draws; $G$ the empirical Gram matrix of an orthonormal basis $L_j$. | Theorem 1: $\Pr\{\lVert G - I\rVert > \delta\} \le 2m\exp(-c_\delta n/K(m))$ with $K(m) = \sup_x\sum_j L_j(x)^2 \ge m$. Stable if $K(m) \le \kappa\,n/\log n$ (eq. 1.4). Legendre polynomials under the uniform law: $K(m) = m^2$. | paper: Sec. 1 Theorem 1, eq. (1.2)-(1.4), Sec. 3 | yes (ZW6RZTL9) |
| [CM17] | [doi:10.5802/smai-jcm.24](https://doi.org/10.5802/smai-jcm.24), [arXiv:1608.00512](https://arxiv.org/abs/1608.00512) | Same setting, weighted. | States that for the Gaussian measure on $\mathbb{R}$ the orthonormal polynomials are unbounded, so $K(m) = \infty$ for $m \ge 2$ and [CDL13] does not apply. Draw from $d\mu_m = \frac1m\sum_j L_j^2\,d\rho$ and weight by its inverse density: stability under $n \gtrsim m\log m$ (Theorem 2 and its corollary). | paper: Sec. 1-2, Sec. 6.1 Fig. 2 | added (9W9AD35C) |
| [KPW19] | [doi:10.1007/s10543-026-01126-8](https://doi.org/10.1007/s10543-026-01126-8), [arXiv:1908.08901](https://arxiv.org/abs/1908.08901) | $-\mathrm{div}(\sigma\nabla u) = f$ on a bounded convex polygon $D\subset\mathbb{R}^2$ with $u = 0$ on $\partial D$ and $0 < \sigma_0\le\sigma\in L^\infty(D)$ (eq. 1). It has the divergence form of our equation ($\sigma = p$, $u = \phi$, $f = -hp$), but with a coefficient bounded away from zero, a bounded domain and Dirichlet data. | Piecewise-linear finite elements on a quasi-uniform triangulation of size $h$. Stiffness matrix and load vector by a stratified Monte Carlo rule with one uniform point $Z_T$ per triangle, $Q_{MC}[v] = \sum_T\lvert T\rvert\,v(Z_T)$ (eq. 18): unbiased, mean-square error $\le\frac{\sqrt3}{2}h^2\lVert v\rVert_{L^2}^2$ (Lemma 3.1). The random bilinear form is almost surely bounded and coercive with the constants of the exact one, because gradients are constant on each triangle (Lemma 3.2). Hence a unique discrete solution (Theorem 3.3) and, for $u\in H^2$, $\sigma\in W^{s,q}$, $f\in L^p$: $\lVert u - u_h^{MC}\rVert_{L^2(\Omega;H^1_0(D))}\le C\,(h + h^s\lvert\sigma\rvert_{W^{s,q}})\,\lVert u\rVert_{H^2} + C\,h^{1-2/p}\lVert f\rVert_{L^p}$ (Theorem 3.5). Sec. 4: importance sampling of the load vector with density proportional to the basis function, for $\sigma\equiv1$ (Theorems 4.4-4.5). An unbounded domain, a weight that vanishes, a global basis and i.i.d. draws from $p$ are all outside the assumptions (*inferred*, discussed below). | paper: Sec. 1-4, arXiv version 1; the journal version of 2026 was not compared | no |
| [LLW21] | [arXiv:2101.01708](https://arxiv.org/abs/2101.01708) | $-\Delta u = f$ on $[0,1]^d$ with a Neumann condition (eq. 2.1), and $-\Delta u + Vu = f$ (eq. 2.2): the unweighted, bounded-domain analogue of our zero-flux problem. | Deep Ritz method: minimise over a two-layer network of width $m$ the Ritz energy $\frac12\int\lvert\nabla u\rvert^2 + \frac12\big(\int u\big)^2 - \int fu$ (eq. 2.3; the squared mean fixes the additive constant), with integrals replaced by averages over $n$ i.i.d. uniform draws (eq. 2.7). Theorem 2.3: expected excess energy $\le C_1\sqrt m\,(\sqrt{\log m} + 1)/\sqrt n + C_2(\log m + 1)^2/m$ when the solution lies in a spectral Barron space. Proof: split into generalisation error, Monte Carlo bias and approximation error (eq. 3.2), with Rademacher complexities of bounded function classes. | paper: Sec. 2 eq. (2.1)-(2.8), Theorem 2.3, Sec. 3 eq. (3.1)-(3.2) | no |
| [BY09] | [doi:10.1016/j.cam.2008.07.037](https://doi.org/10.1016/j.cam.2008.07.037) | Not about our equation. Finite linear systems $x = Ax + b$ and their projection on a subspace $\{\Phi r\}$ in a weighted Euclidean norm, $\Phi r = \Pi(A\Phi r + b)$ (eq. 1.2): a Galerkin projection (*inferred*; the paper does not use the word). | "Equation approximation": the low-dimensional system is replaced by sample averages along a simulated sequence of indices (eq. 2.5-2.6); least-squares temporal-difference learning, LSTD(0), is the special case of a discounted Markov chain. Convergence with probability 1 by the law of large numbers, and unique solvability of the sampled system "for all $t$ sufficiently large" (Sec. 2); no finite-sample stability bound. Error of the exact projection: $\lVert x^* - \Phi r^*\rVert\le\lVert(I - \Pi A)^{-1}\rVert\,\lVert x^* - \Pi x^*\rVert$ (eq. 1.4). | paper: Sec. 1 eq. (1.1)-(1.8), Sec. 2 eq. (2.1)-(2.6), read in the copy on an author's page | no |
| [HKS21] | [doi:10.1051/m2an/2021078](https://doi.org/10.1051/m2an/2021078), [arXiv:2002.09385](https://arxiv.org/abs/2002.09385) | Stationary Fokker-Planck equation $-\nabla\cdot(\kappa\nabla u) - \nabla\cdot(\kappa u\nabla V) = f$ (eq. 1.1), with $\pi = e^{-V}$. For the relative density $U = u/\pi$ it reads $-\nabla\cdot(\kappa\pi\nabla U) = f$ (eq. 2.6): ours with $\kappa = 1$, $p = \pi$, $\phi = U$ and their $f$ equal to $-hp$. | Family of finite-volume schemes $-\sum_{j\sim i}\frac{m_{ij}}{h_{ij}}\kappa_{ij}S_{ij}(U_j - U_i) = f_i$ (eq. 1.6, 2.7), $S_{ij}$ a mean of $\pi_i$ and $\pi_j$: the Scharfetter-Gummel scheme for $S = \pi_i\pi_j/\Lambda(\pi_i,\pi_j)$, $\Lambda$ the logarithmic mean; the "square-root approximation" for the geometric mean. The matrix is an M-matrix (Sec. 1.2), and in the variable $U$ its weights are symmetric in $i$ and $j$. In 1D with constant flux on a cell the exact weight is the harmonic average $\big(\frac1h\int_0^h\pi^{-1}\big)^{-1}$ (Sec. 3.2). Error in a discrete energy norm bounded by the consistency of the mesh plus $O(h)$ (Theorem 5.4); consistency error $O(h^2)$ on cubic meshes (Theorem 5.7). Assumptions: bounded polygonal domain, bounded $V$, Dirichlet data. 1D experiments: second order for all means; the most accurate mean differs for $u$ and for the flux (Example 6.1). | paper: Sec. 1.1-1.2 eq. (1.1)-(1.6), Sec. 2.2 eq. (2.6)-(2.7), Sec. 3.1-3.2, Theorems 5.4 and 5.7, Sec. 6 (arXiv version) | no |
| [SG69] | [doi:10.1109/T-ED.1969.16566](https://doi.org/10.1109/T-ED.1969.16566) | Flux of a drift-diffusion equation between two nodes. | Exponentially fitted flux, obtained by solving the two-point problem with constant flux, drift and diffusion on the cell: $J = -\frac{\kappa}{h}\,\frac{\pi_0\pi_h}{\Lambda(\pi_0,\pi_h)}\big(\frac{u_h}{\pi_h} - \frac{u_0}{\pi_0}\big)$ in the notation of [HKS21] (their eq. 3.2-3.3 and 3.6). It tends to the central scheme for small drift and to the upwind scheme for large drift. | secondary ([HKS21] Sec. 1.1 and 3.1); the original was not accessible | no |
| [CC70] | [doi:10.1016/0021-9991(70)90001-X](https://doi.org/10.1016/0021-9991(70)90001-X) | Flux $F = (B + D')f + D\,\partial_w f$ of a 1D Fokker-Planck equation $\partial_t f = \partial_w F$ with no-flux boundary conditions (notation of [PZ17]). | Conservative scheme with $F_{i+1/2} = \tilde C_{i+1/2}\big((1-\delta_{i+1/2})f_{i+1} + \delta_{i+1/2}f_i\big) + D_{i+1/2}\frac{f_{i+1} - f_i}{\Delta w}$ and $\delta = \frac1\lambda + \frac{1}{1 - e^\lambda}$, so that the numerical flux vanishes on the stationary state. With weights computed from the exact stationary state $f^\infty$ ([PZ17], eq. 19-20) the flux equals $\frac{D}{\Delta w}\frac{f^\infty_i f^\infty_{i+1}}{\Lambda(f^\infty_i, f^\infty_{i+1})}\big(\frac{f_{i+1}}{f^\infty_{i+1}} - \frac{f_i}{f^\infty_i}\big)$, the Scharfetter-Gummel flux (*inferred*, our computation, checked numerically). | secondary ([PZ17] Sec. 2.1 eq. (7)-(20), which restates and generalises the scheme); the original was not accessible | no |
| [BV18] | [doi:10.1090/memo/1228](https://doi.org/10.1090/memo/1228), [arXiv:1502.05034](https://arxiv.org/abs/1502.05034) | Generator of a scalar diffusion in conservative form, $(Lf)(x) = \frac{1}{\nu(x)}\big(M(x)\,\nu(x)\,f'(x)\big)'$ (eq. 2.3.1): with $M = 1$, $\nu = p$ our equation is $L\phi = h$. | Space discretisations of $L$ that are generators of Markov jump processes ("realizable"). Finite-volume version (eq. 2.3.7-2.3.8): $(Qf)_i = \frac{1}{\delta x_i\,\nu_i}\big[\nu_{i+1/2}M_{i+1/2}\frac{f_{i+1} - f_i}{\delta x_i^+} - \nu_{i-1/2}M_{i-1/2}\frac{f_i - f_{i-1}}{\delta x_i^-}\big]$, with $\nu_{i+1/2}$ the arithmetic mean, the minimum or the geometric mean of $\nu_i$, $\nu_{i+1}$; second order for the arithmetic mean (the minimum lowers the order), and reversible with respect to $\delta x_i\,\nu_i$. The grid need not be finite: stability by a Lyapunov function, geometric ergodicity and accuracy of equilibrium expectations are stated for an unbounded domain (Sec. 1.2, proved in Ch. 4). Ch. 6: on the infinite tridiagonal matrix the invariant density has an explicit product formula. | paper: Sec. 1.2, Sec. 2.3 eq. (2.3.1)-(2.3.9), Ch. 6 Prop. 6.1.1-6.1.2 (arXiv version); Ch. 4 only through its summary in Sec. 1.2 | no |

## What the literature offers for the open problems (C)

**Truncation and boundary conditions (open choice 1 of
[report.md](pilot/report.md)).**

- No paper found treats the zero-flux truncation of this equation or its
  $\sqrt\varepsilon$ error; this rests on a bounded search (Summary 8 and 9).
  The derivation in [theory.md](theory.md) stands on its own.
- [LK80] says the right replacement for an ad hoc condition is an asymptotic
  one. For our equation a candidate (derived by us, not taken from the paper)
  is to drop $\phi''$ at the boundary: $\phi'(b) = h(b)/(\log p)'(b)$. It is
  exact for `gauss_mu` and gives $b - 1/b$ against the exact $b$ for
  `gauss_sigma`. This is "a boundary condition that models the tail flux" and
  needs only $h$ and $p$ at the end node. It is the leading term of the tail
  flux $-\int_b^\infty h\,p$ after integration by parts, so it assumes
  exponential-type tails. At a finite end point where $p \sim x^{\alpha-1}$
  the dropped $\phi''$ is of the same order: at the lower end
  $a = 1.4\cdot10^{-3}$ of Gamma(2, 1) it gives twice the exact $\phi'$ for
  `gamma_scale` and 1.87 times for `gamma_shape` (0.94 and 0.98 at the upper
  end); for `gauss_sin` it gives 0.210 against the exact 0.193.
- Where a paper needs values of the 1D solution itself, it integrates the
  closed form rather than solving the boundary value problem: composite
  trapezoid rule on the unnormalised density, applied to one-dimensional full
  conditionals [HDP21, Sec. 4.1, 5.1]; quadrature of the closed form as the
  reference in the filtering papers [YLMM12, TMM17, TMM20, OTM20]; partial
  sums over samples as a solver [YMM13, Sec. IV-A]. The sample-based filtering
  solvers do solve the weak form, and [YLMM12] does so on a truncated interval
  $D = [-2, 2]$ without discussing the truncation. This agrees with the remark
  of [theory.md](theory.md) that the FD scheme is a quadrature rule for the
  closed form.
- Zero flux is also a sufficient condition for unbiasedness of these control
  variates ([MSI13] Prop. 1-2, eq. 10, where in 1D equal flux at the two ends
  suffices; [SOMD23] eq. 5). A solver that fits the strong form needs trial functions
  that satisfy it; the weak form does not (it is the natural condition). This
  matters for densities that do not vanish at a finite end point
  ([MSI13], Example 1).
- Mapped, Laguerre or Hermite spectral bases live on the unbounded domain and
  need no truncation (*inferred*; [SW09] compares their convergence rates by
  decay of the solution and sets domain truncation aside in its Sec. 1).

**Monte Carlo Galerkin: stability and sample size.**

- [CDL13] gives the form of the answer: a condition $K(m) \lesssim n/\log n$,
  with $K$ depending on basis and density. For polynomials under a Gaussian
  $K = \infty$ for $m \ge 2$, so the theory gives no guarantee
  [CM17, Sec. 1]; numerically, standard least squares under the Gaussian
  needed $n/\ln n$ growing roughly like $e^{m/3}$ for a well-conditioned Gram
  matrix [CM17, Sec. 6.1, Fig. 2], consistent with the instability at large
  degree in the pilot. For our stiffness matrix the relevant functions are the
  $\psi_k'$, orthonormalised in $L^2(p)$ (*inferred*: $\hat A$ is the
  empirical Gram matrix of the $\psi_k'$ in $L^2(p)$, so Theorem 1 of [CDL13]
  applies to it unchanged; its accuracy results, Theorems 2-3, concern
  least-squares projection and do not transfer; no paper found states this
  for a Galerkin matrix).
- Remedies in the literature: (i) weighted sampling [CM17], possible in a
  benchmark where we choose how to draw; (ii) penalised regression, which
  allowed higher polynomial degree for control variates [SOMD23]; (iii)
  Tikhonov regularisation of the kernel matrix: required in [Nus24]
  ($\lambda > 0$, Problem 1, Remark 4); an optional fix for ill-conditioning
  in [MM24] (Sec. 5.1.1, with added noise as an alternative in Sec. 5.1.2); in
  [AGLM20] part of the formulation and of Theorem 7 ($\lambda > 0$), but the
  experiments use $\lambda = 0$, stabilised by damping and a pseudo-inverse
  (Prop. 6);
  (iv) a basis-free kernel solver, with its own bias-variance trade-off in the
  kernel width [TM16, TMM20].
- Known failure modes to look for: empty cells for local bases [YLMM12],
  oscillation and sign change for polynomials [TM16].
- For the diffusion-map solver the variance analysis on unbounded support is
  left open: collective compactness of the empirical operators could not be
  verified on $L^2(\rho)$ [TMM20, Remark 4.6]. The paper's numerics already
  use an unbounded (Gaussian-mixture) density, so a 1D benchmark with a closed
  form adds measured error rates, not the missing analysis.

**Choice of basis.**

- For the ill-conditioning of Hermite polynomials under the Gamma, a possible
  remedy (*inferred*): [APV17] centres the Hermite basis at the mean of $p$
  and scales it by a free factor times its covariance (eq. 32; motivated there
  by approximation quality and invariance under rescaling, not by
  conditioning, and not for the Gamma), works with $\sqrt p\,\phi$ (eq. 22),
  and cites [Tan93] in Remark 3.1 for a degree-dependent scaling that needs
  $O(p)$ rather than $O(p^2)$ Hermite functions to resolve $p$ wavelengths.
  The general principle is a basis adapted to $p$; for the Gamma this
  is the Laguerre family already used in Appendix A.2 of
  [theory.md](theory.md).
- Constant offsets of the basis (open choice 2): [SOMD23] fits an intercept
  together with the solution, and [RS18] adds a Lagrange multiplier for a
  basis that does not have mean zero; both make the right-hand side
  insensitive to the mean of $h$. Centring $h$ by its sample mean, as in the
  pilot, is the same device: with sample averages, a constant added to the
  basis together with a multiplier as in [RS18] gives a multiplier equal to
  minus the sample mean of $h$, hence exactly the centred right-hand side
  (*inferred*, our computation). [ERS20] and [Sau19] give closed forms in
  which the centring is built in.
- [TM16] (Prop. 1) bounds the sample-based Galerkin error when the basis is
  the first $M$ eigenfunctions of the operator; its Remark 1 notes that these
  are generally unknown. For $N(0,1)$ they are the Hermite polynomials,
  $\mathrm{He}_k'' - x\,\mathrm{He}_k' = -k\,\mathrm{He}_k$ ([TM16] Example 1;
  [APV17] Remark 3.1 in Schrödinger form), so with exact integrals the pilot's
  stiffness matrix is diagonal,
  $\mathbb{E}_p[\mathrm{He}_k'\mathrm{He}_l'] = k\,k!\,\delta_{kl}$. The
  exactness of the pilot at low degree has a different cause: the exact $\phi$
  ($x$ for `gauss_mu`, $x^2/2$ for `gauss_sigma` and `gamma_scale`) lies in
  the span, which also gives exactness under the Gamma.

**Other solvers worth benchmarking against the closed form.**

| Solver | Needs | Source |
| --- | --- | --- |
| Empirical closed form: partial sums of centred $h$ over sorted samples, divided by a density estimate | samples and $p(x)$ or a density estimate ([YMM13] eq. 43) | [YMM13], eq. (44); the kernel form of [Sau19], [ERS20] with the empirical CDF reduces to the same estimator (*inferred*, [Sau19] eq. 9 applied to the empirical measure; checked numerically) |
| Least squares on the strong form with an intercept, with or without ridge | samples, $(\log p)'$ | [MSI13], [SOMD23] |
| Diffusion-map (Markov matrix) fixed point | samples | [TM16], [TMM20] |
| Kernel Galerkin or kernel ridge regression with Tikhonov regularisation | samples (and $(\log p)'$ in [Nus24]; in [AGLM20] also the Jacobian $\nabla_\theta h_\theta$ of the generator at each sample, eq. (7), (14), which in 1D with $h_\theta = F_\theta^{-1}$ is $\Phi_\theta$ itself, *inferred*) | [AGLM20], [MM24], [Nus24] |
| Ritz functional minimised over a neural network | samples | [OTM20] |
| Hermite-function Galerkin with Gauss-Hermite quadrature | analytic $p$ with $(\log p)'$ and $(\log p)''$ | [APV17] |

For the reference itself, $\partial_\theta F$ of families without an
elementary formula can be obtained by automatic differentiation of a CDF
code that supports it [FMM18], an alternative to the quadrature used in the
pilot.

**Additions of the second pass: truncation and boundary conditions.**

- Still no estimate in the truncation level for this equation. [SW09]
  (Sec. 1) calls truncation viable only for exponentially decaying solutions
  or with accurate boundary conditions, and does not treat it. The theory of
  asymptotic boundary conditions ([LK80], de Hoog and Weiss, Markowich) is
  general and not specialised to a weight; a review describes it as a
  projection of the solution onto the manifold of bounded solutions (Fazio,
  see [Leads not substantiated](#leads-not-substantiated-c)).
- Stability under truncation. By [RBI17], Lemma 4, the Poincaré constant of
  $p$ restricted to $[a, b]$ is at most that of $p$. Applied to our problem
  (*inferred*): the truncated zero-flux solution satisfies the energy estimate
  of [theory.md](theory.md), Section 1, with the constant $C_P$ of the full
  problem, for every $\varepsilon$. The truncation error is then a consistency
  error, the boundary flux that is discarded, and not a loss of stability.
- The constant itself. The Muckenhoupt criterion ([RBI17], Theorem 1) gives
  $C_P$ within a factor 8 from $A_\pm$, two suprema of a tail mass times
  $\int dt/\rho$: computable by quadrature for any benchmark density. The
  estimate $\lVert\phi'\rVert\le\sqrt{C_P}\,\lVert h\rVert$ is a weighted Hardy
  inequality for the operator $h\mapsto\frac1p\int_x^{x_+}h\,p$ of the closed
  form (*inferred*; the paper states the criterion for the Poincaré
  inequality).
- Exact zero-flux problems on a finite interval. By [RBI17], Prop. 7, between
  two consecutive roots of $\mathrm{He}_n$ the polynomial $\mathrm{He}_{n+1}$
  is a Neumann eigenfunction of $\phi'' - x\phi'$ with eigenvalue $n+1$. So
  $\phi = \mathrm{He}_{n+1}$, $h = -(n+1)\,\mathrm{He}_{n+1}$ solves the
  zero-flux problem for the normal density truncated to that interval; for
  $n = 2$ the interval is $[-1, 1]$ and $\phi' = 3(x^2 - 1)$. This gives a
  test of the FD scheme with no truncation error (*inferred* use; the case
  $n = 2$ was checked by substitution).
- No truncation. The schemes of [BV18] are defined and analysed on an
  infinite grid. In 1D the discrete flux of such a scheme is the partial sum
  $\Delta x\sum_{i\le j}h_i\,p_i$ (Section 3 of [theory.md](theory.md)), so
  cutting the grid amounts to cutting a convergent series, whose tail can be
  bounded from the analytic tail of $h\,p$ (*inferred*).

**Additions of the second pass: the FD scheme.**

- In the notation of [HKS21] the pilot's scheme uses the weight
  $S_{j+1/2} = p(x_{j+1/2})$ in place of a mean of $p_j$ and $p_{j+1}$
  (*inferred*). Alternatives to try: the Scharfetter-Gummel mean
  $p_j\,p_{j+1}/\Lambda(p_j, p_{j+1})$, exact when $\log p$ is linear on the
  cell and the flux is constant ([HKS21], Sec. 3.1-3.2); and the harmonic
  mean, the most accurate for the flux in Example 6.1 of [HKS21]. The flux
  is what our error measures, since $\phi' = q/p$.
- The convergence theory of [HKS21] needs a bounded potential. It does not
  cover the lower end of the Gamma density, where $p\to0$; this is where the
  pilot observes an order below 2.

**Additions of the second pass: Monte Carlo Galerkin.**

- What makes the randomised Galerkin matrix of [KPW19] stable with no
  condition on the sample size is the pairing of one random point per element
  with gradients that are constant on elements. A transfer to our problem
  (*inferred*, not in the paper): piecewise-linear elements on a partition
  into $n$ cells of equal probability $1/n$, with one draw per cell. The
  stiffness matrix $\hat{\mathbb{E}}_n[\psi'\psi'^\top]$ is then exact, and
  only the load vector is random. The empty-cell failure of [YLMM12] cannot
  occur.
- For a global polynomial basis no result was found. The bound of [CDL13] on
  the empirical Gram matrix stays the only tool, and it gives nothing for
  Hermite polynomials (summary item 7).
- [LLW21] shows the shape of a finite-sample bound for a sample-based Ritz
  method (statistical error plus approximation error, eq. 3.2), but for
  bounded function classes on a cube. Its Ritz energy contains the term
  $\frac12(\int u)^2$, which fixes the additive constant: a third device for
  open choice 2, next to the intercept of [SOMD23] and the multiplier of
  [RS18].
- In approximate dynamic programming the same construction, a projected
  equation with sampled coefficients, has convergence with probability 1 and
  no finite-sample bound [BY09].

**Additions of the second pass: reference solutions, test cases, solvers.**

- The closed form is also the standard solution of the Poisson equation of a
  scalar diffusion ([AWS21], eq. C.50), with any diffusion coefficient
  $\sigma$.
- $2J(\theta)$ is the asymptotic variance of the time average of the score
  along the Langevin diffusion with invariant density $p_\theta$ (*inferred*
  from [vVvZ05], [CCG12] and the identity $J = \lVert\Phi_\theta\rVert^2$):
  a probabilistic reading of the Wasserstein information, and an independent
  Monte Carlo check of $\lVert\phi'\rVert$.
- Test cases without an elementary closed form: the skew-normal shape
  parameter, with $J(\alpha)$ given as a 1D integral in [LR22], Theorem 3;
  the Pareto index, for which [JYTS26], eq. (18), gives the potential
  $\phi = -\frac{x^2\log x}{2\theta} + \frac{x^2}{4\theta} + \text{const}$,
  in agreement with $\Phi_\theta = -x\log x/\theta$ of
  [theory.md](theory.md) (checked by differentiation).
- Two more solvers to benchmark: residual minimisation by stochastic gradient
  descent with a polynomial, kernel or network ansatz [SODCB22]; the
  minimal-norm finite-difference solution of the continuity equation
  [NLY23].
- An extension of the benchmark: the equation of [JYTS26] with
  $0 < \lambda < 1$. The Gaussian family has a closed form for every
  $\lambda$ (their eq. 19), so FD and Galerkin can be tested with the
  zero-order term; the Galerkin system then gains the mass matrix
  $\lambda\,\mathbb{E}_p[\psi\psi^\top]$ and the constant is no longer free
  (*inferred*).

## Leads not substantiated (C)

Bibliographic data below were verified; the content was not, or it did not
contain the equation. None of these is in the tables, and none was added to
Zotero by this review.

- **Wasserstein statistics in 1D location-scale models.** Amari and Matsuda
  (2022), [doi:10.1007/s10463-021-00788-1](https://doi.org/10.1007/s10463-021-00788-1),
  [arXiv:2007.11401](https://arxiv.org/abs/2007.11401): read. No PDE is
  written, but Sec. 5 derives the 1D solution in metric form:
  $(P+\delta P)^{-1}(u) = P^{-1}(u) - \delta P(x(u))/p(x(u))$ and eq. (11),
  $C(p,p+\delta p) = \int\frac1p\big(\int_{-\infty}^x\delta p\big)^2dx$, i.e.
  $\Phi_\theta = -\partial_\theta F/p$ and $J = \lVert\Phi_\theta\rVert^2$,
  with $\Phi_\mu = 1$ and $\Phi_\sigma = (x-\mu)/\sigma$ in the proof of
  Theorem 4. The W-estimator uses the quantile formula (1); the Wasserstein
  score of Li et al. appears only as a contrast. It could be moved to the
  Wasserstein table.
- **Wasserstein natural gradient (discrete).** Li and Montúfar (2018),
  [doi:10.1007/s41884-018-0015-3](https://doi.org/10.1007/s41884-018-0015-3):
  works on a discrete sample space; the continuous operator appears only in the
  review section.
- **Domain truncation and artificial boundary conditions for this equation.**
  Nothing specific found. Tsynkov (1998),
  [doi:10.1016/S0168-9274(98)00025-7](https://doi.org/10.1016/S0168-9274(98)00025-7),
  and Markowich (1982), [doi:10.1137/0513033](https://doi.org/10.1137/0513033),
  are general (the latter read in abstract only, same message as [LK80]).
  Second pass, again nothing specific. What the searches returned:
  - Fazio (2020), "Free boundary formulation for boundary value problems on
    semi-infinite intervals: an up to date review",
    [arXiv:2011.07723](https://arxiv.org/abs/2011.07723),
    [doi:10.1002/mma.70233](https://doi.org/10.1002/mma.70233): Sec. 1 read.
    It summarises the asymptotic boundary conditions of de Hoog and Weiss,
    [LK80] and Markowich (derived from the behaviour of the equation at
    infinity, they project the solution onto the manifold of bounded
    solutions) and proposes to treat the truncation point as an unknown free
    boundary. Neither is specialised to a weighted equation.
  - Mahdian, Glynn and Liu (2025),
    [doi:10.1007/s11009-025-10158-6](https://doi.org/10.1007/s11009-025-10158-6),
    [arXiv:2401.15905](https://arxiv.org/abs/2401.15905): abstract and Sec. 1
    read. Truncation of the state space for Poisson's equation of Markov
    chains and jump processes on a discrete state space, with a posteriori
    error bounds; the abstract calls it the first truncation approximation
    with provable and computable bounds. Not a diffusion.
  - Truncation of singular Sturm-Liouville problems to regular ones: the hits
    are about convergence of eigenvalues, with no source term, e.g. Brown and
    Marletta (2000), [arXiv:math/0006218](https://arxiv.org/abs/math/0006218)
    (title only).
- **Birth-death dynamics.** Lu, Lu and Nolen (2019),
  [arXiv:1905.09863](https://arxiv.org/abs/1905.09863): read in the second
  pass (Sec. 1-2, Sec. 5, Appendix A). The equation of the thread does not
  appear. The dynamics adds to the Fokker-Planck equation a reaction term
  $-\rho_t\,\alpha_t$ with $\alpha_t = \log(\rho_t/\pi) - \mathbb{E}_{\rho_t}\log(\rho_t/\pi)$
  (eq. 5-6), implemented by killing and duplicating particles (Sec. 5), not by
  a transport. Appendix A parametrises the tangent space of the
  Wasserstein-Fisher-Rao metric by
  $\zeta = -\nabla\cdot(\rho\nabla u) + \rho\,(u - \int u\rho)$. For
  $\zeta = \partial_\theta p_\theta$ this is
  $\phi'' + \phi'(\log p)' - (\phi - \mathbb{E}_p\phi) = h$ (rewriting by us):
  our equation with a zero-order term, the case $\lambda = \tfrac12$ of
  [JYTS26] up to a factor 2 in $h$. Kept out of the tables because the paper
  uses the relation only to define the metric. The link from Fisher-Rao and
  birth-death dynamics to a transport equation is substantiated by [MM24] and
  [Nus24] instead.
- **Linearised Monge-Ampère equation.** González-Sanz and Sheng (2024),
  [arXiv:2408.06534](https://arxiv.org/abs/2408.06534), cited by the reference
  paper: from its abstract, the linearisation of the Monge-Ampère equation for
  the transport map from a fixed reference measure. Linearised at the identity
  map (reference $= p_\theta$) it reduces to our equation (*inferred*: from
  $p_{\theta+t}(T_t x)\det DT_t(x) = p_\theta(x)$ with
  $T_t = x + t\nabla\phi + o(t)$); [TJS25] v2, Remark 4.7, characterises
  $\Phi_\theta$ this way.
- **Journal version of [YLMM12].** Yang, Laugesen, Mehta and Meyn (2016),
  [doi:10.1016/j.automatica.2016.04.019](https://doi.org/10.1016/j.automatica.2016.04.019):
  no accessible version found in the second pass (web search; arXiv holds
  only the conference version, 1303.1205v1). Not read.
- **Full texts sought and not obtained in the second pass.** [PV01]: the
  publisher's page did not serve the file to an automated request. [LK80]: no
  open copy; the 1978 Caltech thesis of the first author with the same title
  was located, its server did not respond. [Rei11]: no open copy; a manuscript
  on the author's page did not respond. The three rows are unchanged; the
  framework of [Rei11] is restated in [RC13].
- **Hardy's inequality with weights.** Muckenhoupt (1972),
  [doi:10.4064/sm-44-1-31-38](https://doi.org/10.4064/sm-44-1-31-38): not
  accessible; known only through [RBI17], Theorem 1. Miclo (2008),
  [doi:10.5802/afst.1179](https://doi.org/10.5802/afst.1179), on exact
  Poincaré constants on the line from Hardy bounds: title only.
- **Temporal-difference learning of the gradient.** Devraj and Meyn (2016),
  [doi:10.1109/CDC.2016.7799246](https://doi.org/10.1109/CDC.2016.7799246),
  [arXiv:1604.01828](https://arxiv.org/abs/1604.01828): Sec. 1 and 4 read,
  Sec. 3 skimmed.
  It approximates the gradient of a value function, or of the solution of
  Poisson's equation, of a Markov chain or scalar diffusion by minimising
  $\mathbb{E}_\pi\lVert\nabla h^\theta - \nabla h\rVert^2$. For a linear
  parametrisation this is $M\theta = b$ with
  $M = \mathbb{E}_\pi[\nabla\psi^\top\nabla\psi]$ (eq. 28-29), the matrix of
  our Galerkin system. Kept out of the tables because $b$ is estimated along
  one trajectory with an auxiliary process driven by the derivative of the
  dynamics (eq. 22, 43), not from i.i.d. draws by integration by parts.
- **Papers citing [LZ23] and [TJS25].** OpenAlex listed 52 and 9 on
  2026-11-20. Added to the tables: [LR22], [NLY23], [JYTS26]. Opened and not
  added: Li and Zhao (2023), [arXiv:2309.12997](https://arxiv.org/abs/2309.12997)
  (uses the 1D closed form for Gaussian mixtures, notes that the integral has
  no explicit value and studies a scaling limit; abstract and Sec. 2); Zuo,
  Zhao, Liu, Osher and Li (2024),
  [arXiv:2402.16821](https://arxiv.org/abs/2402.16821) (1D Wasserstein
  gradient flows through parametrised transport maps; the equation is not
  solved; abstract and a keyword search of the text). The other titles did not
  point to a numerical solution of the equation and were not opened.
- **Neural control variates.** Wan, Zhong, Xiong and Zhu (2018),
  [arXiv:1806.00159](https://arxiv.org/abs/1806.00159): not read. [SODCB22],
  Sec. 2, describes it as a network vector field inserted in the Langevin
  Stein operator and fitted by least squares with a penalty.
- **Queries of the second pass that returned nothing relevant.** arXiv API,
  title fields: "artificial boundary" with "Fokker-Planck"; "unbounded
  domain" with "Fokker-Planck" and "finite"; "asymptotic variance" with
  "one-dimensional" and "diffusion"; "Poisson equation" with "one-dimensional"
  and "diffusion"; "Poisson equation" with "Langevin" and "neural"; "Stein"
  with "neural" and "control variates"; "structure-preserving" with
  "reversible"; "Hardy" with "Poincaré" and "one-dimensional". All fields:
  "Wasserstein score" with "numerical". Web search engine: a query on
  Galerkin stiffness matrices from Monte Carlo samples (empirical measure,
  stability, sample size) returned only work on equations with random
  coefficients, where the sampling is over coefficients and not over
  quadrature points; a query on truncation error for the Poisson equation of
  the Ornstein-Uhlenbeck or Fokker-Planck operator with weighted Sobolev
  spaces returned the items listed under domain truncation above.

## Appendix: References (C)

Keys are those used in the tables. "arXiv" is the version read where one
exists.

**Wasserstein information geometry**

- **[TJS25]** N. García Trillos, A. Q. Jaffe, B. Sen. Wasserstein-Cramér-Rao
  Theory of Unbiased Estimation. Preprint, 2025. arXiv:2511.07414. Read in
  v1 (10 Nov 2025), the version in Zotero; v2 (26 Oct 2026) was checked for
  the points given in the table.
- **[LZ23]** W. Li, J. Zhao. Wasserstein information matrix. *Information
  Geometry* 6 (2023), 203-255. doi:10.1007/s41884-023-00099-9.
  arXiv:1910.11248.
- **[CL20]** Y. Chen, W. Li. Optimal transport natural gradient for statistical
  manifolds with continuous sample space. *Information Geometry* 3 (2020),
  1-32. doi:10.1007/s41884-020-00028-0. arXiv:1805.08380.
- **[AM24]** S. Amari, T. Matsuda. Information geometry of Wasserstein
  statistics on shapes and affine deformations. *Information Geometry* 7
  (2024), 285-309. doi:10.1007/s41884-024-00139-y. arXiv:2307.12508.
- **[NM25]** H. Nishimori, T. Matsuda. On the attainment of the
  Wasserstein-Cramer-Rao lower bound. Preprint, 2025. arXiv:2506.12732.
- **[AGLM20]** M. Arbel, A. Gretton, W. Li, G. Montúfar. Kernelized Wasserstein
  Natural Gradient. International Conference on Learning Representations
  (ICLR), 2020. arXiv:1910.09652.
- **[Ott01]** F. Otto. The geometry of dissipative evolution equations: the
  porous medium equation. *Communications in Partial Differential Equations*
  26 (2001), 101-174. doi:10.1081/PDE-100002243.
- **[LR22]** W. Li, F. J. Rubio. On a prior based on the Wasserstein
  information matrix. *Statistics & Probability Letters* 190 (2022), 109645.
  doi:10.1016/j.spl.2022.109645. arXiv:2202.03217.
- **[NLY23]** L. Nurbekyan, W. Lei, Y. Yang. Efficient natural gradient descent
  methods for large-scale PDE-based optimization problems. *SIAM Journal on
  Scientific Computing* 45 (2023), A1621-A1655. doi:10.1137/22M1477805.
  arXiv:2202.06236.
- **[JYTS26]** A. Q. Jaffe, C. Yang, N. García Trillos, B. Sen. Optimal
  tradeoffs between variance and sensitivity, via Hellinger-Kantorovich
  geometry. Preprint, 2026. arXiv:2610.35858.

**Pathwise gradients**

- **[FMM18]** M. Figurnov, S. Mohamed, A. Mnih. Implicit Reparameterization
  Gradients. 32nd Conference on Neural Information Processing Systems
  (NeurIPS), 2018. arXiv:1805.08498.
- **[JO18]** M. Jankowiak, F. Obermeyer. Pathwise Derivatives Beyond the
  Reparameterization Trick. Proceedings of the 35th International Conference on
  Machine Learning, PMLR 80, 2018. arXiv:1806.01851.

**Stein's method**

- **[LRS17]** C. Ley, G. Reinert, Y. Swan. Stein's method for comparison of
  univariate distributions. *Probability Surveys* 14 (2017), 1-52.
  doi:10.1214/16-PS278. arXiv:1408.2998.
- **[Sau19]** A. Saumard. Weighted Poincaré inequalities, concentration
  inequalities and tail bounds related to Stein kernels in dimension one.
  *Bernoulli* 25 (2019), 3978-4006. doi:10.3150/19-BEJ1117. arXiv:1804.03926.
- **[CFP19]** T. A. Courtade, M. Fathi, A. Pananjady. Existence of Stein
  kernels under a spectral gap, and discrepancy bounds. *Annales de l'Institut
  Henri Poincaré, Probabilités et Statistiques* 55 (2019), 777-790.
  doi:10.1214/18-AIHP898. arXiv:1703.07707.
- **[ERS20]** M. Ernst, G. Reinert, Y. Swan. First-order covariance
  inequalities via Stein's method. *Bernoulli* 26 (2020), 2051-2081.
  doi:10.3150/19-BEJ1182. arXiv:1906.08372.

**Poisson equation for diffusions and control variates**

- **[PV01]** E. Pardoux, A. Yu. Veretennikov. On the Poisson equation and
  diffusion approximation. I. *The Annals of Probability* 29 (2001),
  1061-1085. doi:10.1214/aop/1015345596.
- **[MSI13]** A. Mira, R. Solgi, D. Imparato. Zero variance Markov chain Monte
  Carlo for Bayesian estimators. *Statistics and Computing* 23 (2013),
  653-662. doi:10.1007/s11222-012-9344-6. arXiv:1012.2983.
- **[OGC17]** C. J. Oates, M. Girolami, N. Chopin. Control functionals for
  Monte Carlo integration. *Journal of the Royal Statistical Society: Series
  B* 79 (2017), 695-718. doi:10.1111/rssb.12185. arXiv:1410.2392.
- **[SOMD23]** L. F. South, C. J. Oates, A. Mira, C. Drovandi. Regularized
  zero-variance control variates. *Bayesian Analysis* 18 (2023), 865-888.
  doi:10.1214/22-BA1328. arXiv:1811.05073.
- **[APV17]** A. Abdulle, G. A. Pavliotis, U. Vaes. Spectral methods for
  multiscale stochastic differential equations. *SIAM/ASA Journal on
  Uncertainty Quantification* 5 (2017), 720-761. doi:10.1137/16M1094117.
  arXiv:1609.05097.
- **[RS18]** J. Roussel, G. Stoltz. Spectral methods for Langevin dynamics and
  associated error estimates. *ESAIM: Mathematical Modelling and Numerical
  Analysis* 52 (2018), 1051-1083. doi:10.1051/m2an/2017044. arXiv:1702.04718.
- **[vVvZ05]** A. van der Vaart, H. van Zanten. Donsker theorems for
  diffusions: necessary and sufficient conditions. *The Annals of Probability*
  33 (2005), 1422-1451. doi:10.1214/009117905000000152. arXiv:math/0507412.
- **[AWS21]** C. Aeckerle-Willems, C. Strauch. Concentration of scalar ergodic
  diffusions and some statistical implications. *Annales de l'Institut Henri
  Poincaré, Probabilités et Statistiques* 57 (2021), 1857-1887.
  doi:10.1214/20-AIHP1144. arXiv:1807.11331.
- **[CCG12]** P. Cattiaux, D. Chafaï, A. Guillin. Central limit theorems for
  additive functionals of ergodic Markov diffusions processes. *ALEA, Latin
  American Journal of Probability and Mathematical Statistics* 9 (2012),
  337-382 (journal reference from the arXiv record). arXiv:1104.2198.
- **[SODCB22]** S. Si, C. J. Oates, A. B. Duncan, L. Carin, F.-X. Briol.
  Scalable control variates for Monte Carlo methods via stochastic
  optimization. In *Monte Carlo and Quasi-Monte Carlo Methods*, Springer
  Proceedings in Mathematics & Statistics, 2022, 205-221.
  doi:10.1007/978-3-030-98319-2_10. arXiv:2006.07487.
- **[RBI17]** O. Roustant, F. Barthe, B. Iooss. Poincaré inequalities on
  intervals - application to sensitivity analysis. *Electronic Journal of
  Statistics* 11 (2017), 3081-3119. doi:10.1214/17-EJS1310. arXiv:1612.03689.

**Nonlinear filtering**

- **[YMM13]** T. Yang, P. G. Mehta, S. P. Meyn. Feedback particle filter.
  *IEEE Transactions on Automatic Control* 58 (2013), 2465-2480.
  doi:10.1109/TAC.2013.2258825. arXiv:1302.6563.
- **[YLMM12]** T. Yang, R. S. Laugesen, P. G. Mehta, S. P. Meyn. Multivariable
  feedback particle filter. 51st IEEE Conference on Decision and Control
  (CDC), 2012, 4063-4070. doi:10.1109/CDC.2012.6425937. arXiv:1303.1205.
  Journal version: *Automatica* 71 (2016), 10-23.
  doi:10.1016/j.automatica.2016.04.019.
- **[LMMR15]** R. S. Laugesen, P. G. Mehta, S. P. Meyn, M. Raginsky. Poisson's
  equation in nonlinear filtering. *SIAM Journal on Control and Optimization*
  53 (2015), 501-525. doi:10.1137/13094743X. arXiv:1412.5845.
- **[TM16]** A. Taghvaei, P. G. Mehta. Gain function approximation in the
  feedback particle filter. 55th IEEE Conference on Decision and Control
  (CDC), 2016, 5446-5452. doi:10.1109/CDC.2016.7799105. arXiv:1603.05496.
- **[TMM17]** A. Taghvaei, P. G. Mehta, S. P. Meyn. Error estimates for the
  kernel gain function approximation in the feedback particle filter. American
  Control Conference (ACC), 2017, 4576-4582. doi:10.23919/ACC.2017.7963661.
  arXiv:1612.05606.
- **[TMM20]** A. Taghvaei, P. G. Mehta, S. P. Meyn. Diffusion map-based
  algorithm for gain function approximation in the feedback particle filter.
  *SIAM/ASA Journal on Uncertainty Quantification* 8 (2020), 1090-1117.
  doi:10.1137/19M124513X. arXiv:1902.07263.
- **[OTM20]** S. Y. Olmez, A. Taghvaei, P. G. Mehta. Deep FPF: Gain function
  approximation in high-dimensional setting. 59th IEEE Conference on Decision
  and Control (CDC), 2020, 4790-4795. doi:10.1109/CDC42340.2020.9304260.
  arXiv:2010.01183.

**Sampling and data assimilation by transport**

- **[Rei11]** S. Reich. A dynamical systems framework for intermittent data
  assimilation. *BIT Numerical Mathematics* 51 (2011), 235-249.
  doi:10.1007/s10543-010-0302-4.
- **[HDP21]** J. Heng, A. Doucet, Y. Pokern. Gibbs flow for approximate
  transport with applications to Bayesian computation. *Journal of the Royal
  Statistical Society: Series B* 83 (2021), 156-187. doi:10.1111/rssb.12404.
  arXiv:1509.08787.
- **[MM24]** A. Maurais, Y. Marzouk. Sampling in unit time with kernel
  Fisher-Rao flow. Proceedings of the 41st International Conference on Machine
  Learning, PMLR 235, 2024. arXiv:2401.03892.
- **[Nus24]** N. Nüsken. Stein transport for Bayesian inference. Preprint,
  2024. arXiv:2409.01464.
- **[RC13]** S. Reich, C. J. Cotter. Ensemble filter techniques for
  intermittent data assimilation. In *Large Scale Inverse Problems*, 2013,
  91-134. doi:10.1515/9783110282269.91. arXiv:1208.6572.
- **[DH08]** F. Daum, J. Huang. Particle flow for nonlinear filters with
  log-homotopy. Signal and Data Processing of Small Targets 2008, SPIE
  Proceedings 6969 (2008), 696918. doi:10.1117/12.764909.
- **[dMMFD15]** F. E. de Melo, S. Maskell, M. Fasiolo, F. Daum. Stochastic
  particle flow for nonlinear high-dimensional filtering problems. Preprint,
  2015. arXiv:1511.01448. Secondary source for [DH08].
- **[LC17]** Y. Li, M. Coates. Particle filtering with invertible particle
  flow. *IEEE Transactions on Signal Processing* 65 (2017), 4102-4116.
  doi:10.1109/TSP.2017.2703684. arXiv:1607.08799. Secondary source for [DH08].

**Numerical analysis**

- **[LK80]** M. Lentini, H. B. Keller. Boundary value problems on
  semi-infinite intervals and their numerical solution. *SIAM Journal on
  Numerical Analysis* 17 (1980), 577-604. doi:10.1137/0717049.
- **[Tan93]** T. Tang. The Hermite spectral method for Gaussian-type
  functions. *SIAM Journal on Scientific Computing* 14 (1993), 594-606.
  doi:10.1137/0914038.
- **[SW09]** J. Shen, L.-L. Wang. Some recent advances on spectral methods for
  unbounded domains. *Communications in Computational Physics* 5 (2009),
  195-241. doi:10.4208/cicp.2009.v5.p195.
- **[CDL13]** A. Cohen, M. A. Davenport, D. Leviatan. On the stability and
  accuracy of least squares approximations. *Foundations of Computational
  Mathematics* 13 (2013), 819-834. doi:10.1007/s10208-013-9142-3.
  arXiv:1111.4422.
- **[CM17]** A. Cohen, G. Migliorati. Optimal weighted least-squares methods.
  *The SMAI Journal of Computational Mathematics* 3 (2017), 181-203.
  doi:10.5802/smai-jcm.24. arXiv:1608.00512.
- **[KPW19]** R. Kruse, N. Polydorides, Y. Wu. Application of randomized
  quadrature formulas to the finite element method for elliptic equations.
  *BIT Numerical Mathematics* 66 (2026), article 31.
  doi:10.1007/s10543-026-01126-8. arXiv:1908.08901 (2019, the version read).
- **[LLW21]** J. Lu, Y. Lu, M. Wang. A priori generalization analysis of the
  Deep Ritz method for solving high dimensional elliptic equations. Preprint,
  2021. arXiv:2101.01708.
- **[BY09]** D. P. Bertsekas, H. Yu. Projected equation methods for
  approximate solution of large linear systems. *Journal of Computational and
  Applied Mathematics* 227 (2009), 27-50. doi:10.1016/j.cam.2008.07.037.
- **[HKS21]** M. Heida, M. Kantner, A. Stephan. Consistency and convergence for
  a family of finite volume discretizations of the Fokker-Planck operator.
  *ESAIM: Mathematical Modelling and Numerical Analysis* 55 (2021), 3017-3042.
  doi:10.1051/m2an/2021078. arXiv:2002.09385.
- **[SG69]** D. L. Scharfetter, H. K. Gummel. Large-signal analysis of a
  silicon Read diode oscillator. *IEEE Transactions on Electron Devices* 16
  (1969), 64-77. doi:10.1109/T-ED.1969.16566.
- **[CC70]** J. S. Chang, G. Cooper. A practical difference scheme for
  Fokker-Planck equations. *Journal of Computational Physics* 6 (1970), 1-16.
  doi:10.1016/0021-9991(70)90001-X.
- **[PZ17]** L. Pareschi, M. Zanella. Structure preserving schemes for
  nonlinear Fokker-Planck equations and applications. *Journal of Scientific
  Computing* 74 (3), 1575-1600, published online 2017.
  doi:10.1007/s10915-017-0510-z. arXiv:1702.00088. Secondary source for
  [CC70].
- **[BV18]** N. Bou-Rabee, E. Vanden-Eijnden. Continuous-time random walks for
  the numerical solution of stochastic differential equations. *Memoirs of the
  American Mathematical Society* 256 (2018), no. 1228. doi:10.1090/memo/1228.
  arXiv:1502.05034.
