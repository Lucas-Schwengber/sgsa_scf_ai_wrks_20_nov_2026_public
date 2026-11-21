---
title: Description
created: 2026-11-19
updated: 2026-11-19
authors: Lucas da Rocha Schwengber (L)
---

# Thread goal description

The goal is to compare finite-difference and galerkin approaches, with MC to approximate quadratures, to solving a 1D weighted poisson equation of the form:

$$
h = \Delta \phi + \langle \nabla \phi, \log(p) \rangle
$$

for some probability density $p$ on $\R$. Following Trillos-Jaffe-Sen, this is known to have a closed form solution in terms of the CDF of $p$. 

The goal is to benchmark finite difference approaches and galerkin methods against this 1D closed form expression.

The comparison should be carried out for standard 1D families (e.g. for example some of the ones available on `scipy`). $h$ should be perturbations along the parameter directions.

The goal is to explore the behaviour of variantes of FD with adaptive meshes, and Galerkin methods based on MC quadrature approximations using different choices of basis functions and sample sizes. 

## Pilot

Let us focus on a standard Gaussian and a Gamma for a pilot and expand to the other choices later on.

Let us use standard FD with bounded domain, and Galerkin with a polynomial basis.

Try to implement the code's backend in a way that allows re-usability. 

To speed up the starting implementation, split the work among three sub-agents: one for the FD implementation, one for the Galerkin and one for the ground-truth closed formula. 

Spawn a fourth sub-agent to write a theory.md report at the root of the thread detailing the three methods (two approximate and one exact).

Spawn a fifth sub-agent to write a lit review on associated papers sovling or mentioning a similar 1D weighted poisson equation. Output its findings to lit_review at the root of the thread.

After each task completes, spawn a review agent to look for errors. After the agent report its findings, incorporate them in the targeted outputs.