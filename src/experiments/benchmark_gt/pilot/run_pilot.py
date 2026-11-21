"""
Run the pilot sweep: FD and Galerkin against the closed form.

For each pilot problem the script scores the finite-difference solver (sweep
in the number of nodes N for both boundary conditions, and a sweep in the
truncation level eps) and the Galerkin solver (sweep in the degree K and the
sample size n, with replications, plus the deterministic reference) by the
relative L2(p) error of phi' against the closed form.

Usage::

    .venv/bin/python src/experiments/benchmark_gt/pilot/run_pilot.py \
        [--slug NAME] [--reps 100] [--seed 0] [--smoke]

Results go to ``outputs/runs/benchmark_gt/pilot/YYYY-MM-DD_<slug>/`` as
``fd_nodes.csv``, ``fd_eps.csv``, ``galerkin.csv`` and ``config.json``.
"""

import argparse
import csv
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import scipy

from ot_1d.fd import solve_fd
from ot_1d.galerkin import HermiteBasis, solve_galerkin
from ot_1d.ground_truth import solve_exact
from ot_1d.metrics import evaluation_grid, relative_l2p_error

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cases import pilot_cases  # noqa: E402

REPO = Path(__file__).resolve().parents[4]
RUNS = REPO / "outputs" / "runs" / "benchmark_gt" / "pilot"

EPS = 1e-6            # truncation level of the common comparison interval
FULL_TAIL = 1e-12     # tail mass left out of the "full line" error


### ---------------------------------------------------------------------------
### Helpers
### ---------------------------------------------------------------------------

def scoring_grid(problem, truth, a, b):
    """
    Build a quadrature grid on [a, b] with the exact phi' evaluated on it.

    Parameters
    ----------
    problem : ot_1d.problem.Problem
        The problem.
    truth : ot_1d.problem.Solution
        The exact solution.
    a : float
        Lower end of the interval.
    b : float
        Upper end of the interval.

    Returns
    -------
    x : numpy.ndarray
        Grid nodes, length m.
    wp : numpy.ndarray
        Quadrature weights times the density, length m.
    exact : numpy.ndarray
        Exact phi' at the nodes, length m.
    """
    x, w = evaluation_grid(problem.family, a, b)
    return x, w * problem.family.pdf(x), truth(x)


def write_csv(path, rows):
    """
    Write a list of dicts with identical keys to a CSV file.

    Parameters
    ----------
    path : pathlib.Path
        Output file.
    rows : list of dict
        The rows; the keys of the first one give the header.
    """
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def git_commit():
    """
    Return the current git commit hash, with ``-dirty`` if there are changes.

    Returns
    -------
    str
        The hash, or ``"unknown"`` outside a git repository.
    """
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                              capture_output=True, text=True, check=True)
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                               capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return head.stdout.strip() + ("-dirty" if dirty.stdout.strip() else "")


### ---------------------------------------------------------------------------
### Sweeps
### ---------------------------------------------------------------------------

def fd_node_sweep(name, problem, truth, grid, nodes):
    """
    FD error against the number of nodes, for both boundary conditions.

    Parameters
    ----------
    name : str
        Label of the problem.
    problem : ot_1d.problem.Problem
        The problem.
    truth : ot_1d.problem.Solution
        The exact solution, used for the exact Neumann data.
    grid : tuple
        Output of :func:`scoring_grid` on the common interval.
    nodes : list of int
        Values of N.

    Returns
    -------
    list of dict
        One row per (boundary condition, N).
    """
    x, wp, exact = grid
    rows = []
    for bc in ("zero_flux", "exact_neumann"):
        for n_nodes in nodes:
            start = time.perf_counter()
            sol = solve_fd(problem, n_nodes, eps=EPS, bc=bc,
                           boundary_dphi=truth if bc == "exact_neumann"
                           else None)
            seconds = time.perf_counter() - start
            rows.append({"case": name, "bc": bc, "eps": EPS,
                         "n_nodes": n_nodes, "dx": sol.info["dx"],
                         "err_common": relative_l2p_error(sol(x), exact, wp),
                         "seconds": seconds})
    return rows


def fd_eps_sweep(name, problem, truth, eps_values, n_nodes):
    """
    Zero-flux FD error against the truncation level, at a fixed fine grid.

    The FD domain changes with eps, so the error is computed on the FD
    solution's own domain [F^{-1}(eps), F^{-1}(1 - eps)].

    Parameters
    ----------
    name : str
        Label of the problem.
    problem : ot_1d.problem.Problem
        The problem.
    truth : ot_1d.problem.Solution
        The exact solution.
    eps_values : list of float
        Truncation levels.
    n_nodes : int
        Number of FD nodes.

    Returns
    -------
    list of dict
        One row per eps.
    """
    rows = []
    for eps in eps_values:
        sol = solve_fd(problem, n_nodes, eps=eps, bc="zero_flux")
        a, b = sol.domain
        x, wp, exact = scoring_grid(problem, truth, a, b)
        rows.append({"case": name, "bc": "zero_flux", "eps": eps,
                     "n_nodes": n_nodes, "a": a, "b": b,
                     "err_own_domain": relative_l2p_error(sol(x), exact, wp)})
    return rows


def galerkin_sweep(name, problem, grid, grid_full, degrees, sizes, reps,
                   seed_seq):
    """
    Galerkin error against degree K and sample size n, with replications.

    Each (n, replication) pair draws one sample, reused for every K and for
    both variants of the right-hand side (h as it is, and h minus its sample
    mean), so all curves are compared on common random numbers.

    Parameters
    ----------
    name : str
        Label of the problem.
    problem : ot_1d.problem.Problem
        The problem.
    grid : tuple
        Output of :func:`scoring_grid` on the common interval.
    grid_full : tuple
        Output of :func:`scoring_grid` on the wide interval standing for
        the full line.
    degrees : list of int
        Values of K.
    sizes : list of int
        Values of n.
    reps : int
        Number of replications per n.
    seed_seq : numpy.random.SeedSequence
        Seed sequence of this problem.

    Returns
    -------
    list of dict
        One row per (n, replication, K, centre_h), plus one row per K for
        the deterministic reference, which has ``n = inf`` and ``rep = -1``.
    """
    x, wp, exact = grid
    xf, wpf, exactf = grid_full
    rows = []

    def record(sol, n, rep, degree, centre_h, seconds):
        rows.append({"case": name, "n": n, "rep": rep, "degree": degree,
                     "centre_h": int(centre_h),
                     "err_common": relative_l2p_error(sol(x), exact, wp),
                     "err_full": relative_l2p_error(sol(xf), exactf, wpf),
                     "cond": sol.info["cond"],
                     "cond_solved": sol.info["cond_solved"],
                     "rank": sol.info["rank"], "seconds": seconds})

    for degree in degrees:
        start = time.perf_counter()
        sol = solve_galerkin(problem, HermiteBasis(degree))
        record(sol, "inf", -1, degree, False, time.perf_counter() - start)

    for n, n_seq in zip(sizes, seed_seq.spawn(len(sizes))):
        for rep, rep_seq in enumerate(n_seq.spawn(reps)):
            samples = problem.family.sample(n, np.random.default_rng(rep_seq))
            for degree in degrees:
                for centre_h in (False, True):
                    start = time.perf_counter()
                    sol = solve_galerkin(problem, HermiteBasis(degree),
                                         samples=samples, centre_h=centre_h)
                    record(sol, n, rep, degree, centre_h,
                           time.perf_counter() - start)
    return rows


### ---------------------------------------------------------------------------
### Entry point
### ---------------------------------------------------------------------------

def main():
    """
    Parse the command line, run the three sweeps and save the results.
    """
    parser = argparse.ArgumentParser(description="Run the pilot sweep.")
    parser.add_argument("--slug", default="pilot")
    parser.add_argument("--reps", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--smoke", action="store_true",
                        help="tiny sweep to check the plumbing")
    args = parser.parse_args()

    config = {
        "eps": EPS, "full_tail": FULL_TAIL, "seed": args.seed,
        "reps": args.reps,
        "fd_nodes": [25 * 2**j for j in range(8)],
        "fd_eps": [1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8],
        "fd_eps_nodes": 3200,
        "degrees": [1, 2, 3, 4, 6, 8, 12],
        "sizes": [100, 1000, 10000, 100000],
    }
    if args.smoke:
        config.update(reps=3, fd_nodes=[25, 100, 400],
                      fd_eps=[1e-2, 1e-4, 1e-6], fd_eps_nodes=400,
                      degrees=[1, 2, 4, 8], sizes=[100, 1000])

    cases = pilot_cases()
    seeds = np.random.SeedSequence(config["seed"]).spawn(len(cases))
    fd_rows, eps_rows, gal_rows = [], [], []
    start = time.perf_counter()
    for (name, problem), seed_seq in zip(cases.items(), seeds):
        truth = solve_exact(problem)
        grid = scoring_grid(problem, truth, *problem.family.domain(EPS))
        grid_full = scoring_grid(problem, truth,
                                 *problem.family.domain(FULL_TAIL))
        fd_rows += fd_node_sweep(name, problem, truth, grid,
                                 config["fd_nodes"])
        eps_rows += fd_eps_sweep(name, problem, truth, config["fd_eps"],
                                 config["fd_eps_nodes"])
        gal_rows += galerkin_sweep(name, problem, grid, grid_full,
                                   config["degrees"], config["sizes"],
                                   config["reps"], seed_seq)
        print(f"{name}: done at {time.perf_counter() - start:.1f} s",
              flush=True)

    out = RUNS / f"{datetime.date.today().isoformat()}_{args.slug}"
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "fd_nodes.csv", fd_rows)
    write_csv(out / "fd_eps.csv", eps_rows)
    write_csv(out / "galerkin.csv", gal_rows)
    config.update(cases=list(cases), git_commit=git_commit(),
                  python=sys.version.split()[0], numpy=np.__version__,
                  scipy=scipy.__version__,
                  seconds=time.perf_counter() - start)
    (out / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    print(f"saved to {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
