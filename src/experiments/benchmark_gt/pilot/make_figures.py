"""
Make the pilot figures and summary table from a saved run.

Usage::

    .venv/bin/python src/experiments/benchmark_gt/pilot/make_figures.py \
        [RUN_DIR]

``RUN_DIR`` defaults to the most recent directory in
``outputs/runs/benchmark_gt/pilot/``. Figures (PNG) and ``summary.csv`` go to
``outputs/summaries/benchmark_gt/pilot/``.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO = Path(__file__).resolve().parents[4]
RUNS = REPO / "outputs" / "runs" / "benchmark_gt" / "pilot"
SUMMARIES = REPO / "outputs" / "summaries" / "benchmark_gt" / "pilot"

CASES = ["gauss_mu", "gauss_sigma", "gauss_sin", "gamma_shape", "gamma_scale"]
TITLES = {
    "gauss_mu": "N(0,1), μ score",
    "gauss_sigma": "N(0,1), σ score",
    "gauss_sin": "N(0,1), h = sin x",
    "gamma_shape": "Gamma(2,1), shape score",
    "gamma_scale": "Gamma(2,1), scale score",
}

# colours: categorical slots 1-2 and a one-hue ordinal ramp, both checked
# with the dataviz palette validator on the light surface
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
BLUE, ORANGE = "#2a78d6", "#eb6834"
RAMP = ["#86b6ef", "#5598e7", "#256abf", "#0d366b"]


### ---------------------------------------------------------------------------
### Reading and styling
### ---------------------------------------------------------------------------

def read_csv(path):
    """
    Read a CSV file into a list of dicts, converting numbers to float.

    Parameters
    ----------
    path : pathlib.Path
        The file to read.

    Returns
    -------
    list of dict
        One dict per row; values that parse as numbers are floats
        (``"inf"`` becomes ``numpy.inf``), the others stay strings.
    """
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            for key, value in row.items():
                try:
                    row[key] = float(value)
                except ValueError:
                    pass
            rows.append(row)
    return rows


def panels(ylabel, xlabel):
    """
    Create one row of five small multiples, one per pilot case.

    Parameters
    ----------
    ylabel : str
        Label of the y axis, shown on the first panel.
    xlabel : str
        Label of the x axis, shown on every panel.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure.
    axes : dict of str to matplotlib.axes.Axes
        The panels, keyed by case label.
    """
    fig, axs = plt.subplots(1, 5, figsize=(16, 3.6), facecolor=SURFACE)
    for ax, case in zip(axs, CASES):
        ax.set_facecolor(SURFACE)
        ax.set_title(TITLES[case], fontsize=10, color=INK, loc="left")
        ax.set_xlabel(xlabel, fontsize=9, color=INK_2)
        ax.grid(True, which="major", color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(AXIS)
        ax.tick_params(colors=MUTED, labelsize=8, length=3)
        ax.tick_params(which="minor", length=0)
    axs[0].set_ylabel(ylabel, fontsize=9, color=INK_2)
    return fig, dict(zip(CASES, axs))


def line(ax, x, y, color, label, **kwargs):
    """
    Draw a series as a line with ringed markers.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target panel.
    x : array_like
        Abscissae.
    y : array_like
        Ordinates.
    color : str
        Series colour.
    label : str
        Legend label.
    **kwargs
        Passed to ``Axes.plot`` (e.g. ``linestyle``, ``marker``).
    """
    style = dict(color=color, linewidth=1.7, marker="o", markersize=5.5,
                 markeredgecolor=SURFACE, markeredgewidth=1.2, label=label,
                 solid_capstyle="round", solid_joinstyle="round")
    style.update(kwargs)
    ax.plot(x, y, **style)


def finish(fig, ax_legend, path, title, ncol):
    """
    Add the shared legend and title, then save the figure.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure.
    ax_legend : matplotlib.axes.Axes
        Panel whose handles feed the legend.
    path : pathlib.Path
        Output PNG file.
    title : str
        Figure title.
    ncol : int
        Number of legend columns.
    """
    handles, labels = ax_legend.get_legend_handles_labels()
    fig.suptitle(title, fontsize=11.5, color=INK, x=0.008, ha="left",
                 y=0.985)
    fig.legend(handles, labels, loc="upper right", ncol=ncol, fontsize=8.5,
               frameon=False, labelcolor=INK_2, bbox_to_anchor=(0.995, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(path, dpi=160, facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {path.relative_to(REPO)}")


def reference_slope(ax, x, y_anchor, power, label):
    """
    Draw a thin guide line proportional to ``x**power``.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target panel.
    x : numpy.ndarray
        Abscissae, increasing.
    y_anchor : float
        Value of the guide at ``x[0]``.
    power : float
        Exponent of the guide.
    label : str
        Legend label.
    """
    ax.plot(x, y_anchor * (x / x[0]) ** power, color=MUTED, linewidth=1.0,
            label=label, zorder=1)


### ---------------------------------------------------------------------------
### Figures
### ---------------------------------------------------------------------------

def figure_fd_nodes(rows):
    """
    FD error against the number of nodes, for both boundary conditions.

    Parameters
    ----------
    rows : list of dict
        Rows of ``fd_nodes.csv``.
    """
    fig, axes = panels("relative L²(p) error of φ′", "nodes N")
    for case, ax in axes.items():
        for bc, color, label in (("zero_flux", BLUE, "zero flux"),
                                 ("exact_neumann", ORANGE, "exact Neumann")):
            sel = sorted((r["n_nodes"], r["err_common"]) for r in rows
                         if r["case"] == case and r["bc"] == bc)
            n, err = np.array(sel).T
            line(ax, n, err, color, label)
            if bc == "exact_neumann":
                reference_slope(ax, n, 2.5 * err[0], -2.0, "slope −2")
        ax.set_xscale("log")
        ax.set_yscale("log")
    finish(fig, axes[CASES[0]], SUMMARIES / "fd_nodes.png",
           "Finite differences: error against grid size (ε = 1e-6)", 3)


def figure_fd_eps(rows):
    """
    Zero-flux FD error against the truncation level eps.

    Parameters
    ----------
    rows : list of dict
        Rows of ``fd_eps.csv``.
    """
    fig, axes = panels("relative L²(p) error of φ′ on [a, b]",
                       "tail mass ε cut on each side")
    n_nodes = int(rows[0]["n_nodes"])
    for case, ax in axes.items():
        sel = sorted((r["eps"], r["err_own_domain"]) for r in rows
                     if r["case"] == case)
        eps, err = np.array(sel).T
        line(ax, eps, err, BLUE, "zero flux")
        reference_slope(ax, eps, 2.5 * err[0], 0.5, "slope ½")
        ax.set_xscale("log")
        ax.set_yscale("log")
    finish(fig, axes[CASES[0]], SUMMARIES / "fd_eps.png",
           f"Finite differences: truncation error (N = {n_nodes})", 2)


def galerkin_stats(rows, centre_h=0):
    """
    Group Galerkin errors by case, sample size and degree.

    Parameters
    ----------
    rows : list of dict
        Rows of ``galerkin.csv``.
    centre_h : int, optional
        Which Monte Carlo variant to keep: 0 for h as it is, 1 for h minus
        its sample mean. The deterministic reference is always kept.
        Default is 0.

    Returns
    -------
    dict
        Maps (case, n, degree) to a numpy.ndarray of ``err_common`` over
        the replications; ``n`` is ``numpy.inf`` for the deterministic
        reference.
    """
    groups = defaultdict(list)
    for r in rows:
        if np.isfinite(r["n"]) and int(r["centre_h"]) != centre_h:
            continue
        groups[(r["case"], r["n"], int(r["degree"]))].append(r["err_common"])
    return {key: np.array(val) for key, val in groups.items()}


def figure_galerkin_degree(stats):
    """
    Galerkin error against the degree K, one line per sample size n.

    Lines are medians over replications; bands are the 10-90% range.

    Parameters
    ----------
    stats : dict
        Output of :func:`galerkin_stats`.
    """
    sizes = sorted({n for _, n, _ in stats if np.isfinite(n)})
    degrees = sorted({k for _, _, k in stats})
    fig, axes = panels("relative L²(p) error of φ′", "degree K")
    for case, ax in axes.items():
        for n, color in zip(sizes, RAMP):
            q = np.array([np.quantile(stats[(case, n, k)], [0.1, 0.5, 0.9])
                          for k in degrees])
            ax.fill_between(degrees, q[:, 0], q[:, 2], color=color,
                            alpha=0.12, linewidth=0)
            line(ax, degrees, q[:, 1], color, f"n = 1e{int(np.log10(n))}")
        # the reference is drawn where it is above round-off level; where
        # the basis contains the solution it is ~1e-15 and would squash the
        # Monte Carlo curves, so it is stated in words instead
        exact = np.array([stats[(case, np.inf, k)][0] for k in degrees])
        shown = exact > 1e-9
        line(ax, np.array(degrees)[shown], exact[shown], INK,
             "n = ∞ (quadrature)", linestyle=(0, (4, 2)), marker="s",
             markersize=4.5, linewidth=1.2)
        if not shown.all():
            first = np.array(degrees)[~shown].min()
            ax.text(0.97, 0.04, f"n = ∞: below 1e-9 for K ≥ {first}",
                    transform=ax.transAxes, ha="right", va="bottom",
                    fontsize=8, color=INK_2)
        ax.set_yscale("log")
        ax.set_xticks(degrees)
    finish(fig, axes[CASES[0]], SUMMARIES / "galerkin_degree.png",
           "Galerkin: error against degree (median and 10–90% band over "
           "replications)", 5)


def figure_galerkin_samples(stats):
    """
    Galerkin error against the sample size n, one line per degree K.

    Parameters
    ----------
    stats : dict
        Output of :func:`galerkin_stats`.
    """
    sizes = np.array(sorted({n for _, n, _ in stats if np.isfinite(n)}))
    available = sorted({k for _, _, k in stats})
    wanted = [k for k in (1, 2, 4, 12) if k in available]
    degrees = wanted if len(wanted) == 4 else available[:4]
    fig, axes = panels("relative L²(p) error of φ′", "samples n")
    for case, ax in axes.items():
        for k, color in zip(degrees, RAMP):
            q = np.array([np.quantile(stats[(case, n, k)], [0.1, 0.5, 0.9])
                          for n in sizes])
            ax.fill_between(sizes, q[:, 0], q[:, 2], color=color, alpha=0.12,
                            linewidth=0)
            line(ax, sizes, q[:, 1], color, f"K = {k}")
        top = np.median(stats[(case, sizes[0], degrees[-1])])
        reference_slope(ax, sizes, 3.0 * top, -0.5, "slope −½")
        ax.set_xscale("log")
        ax.set_yscale("log")
    finish(fig, axes[CASES[0]], SUMMARIES / "galerkin_samples.png",
           "Galerkin: error against sample size (median and 10–90% band "
           "over replications)", 5)


### ---------------------------------------------------------------------------
### Summary table
### ---------------------------------------------------------------------------

def summary_table(fd_rows, stats, stats_centred):
    """
    Build and save one summary row per pilot case.

    Parameters
    ----------
    fd_rows : list of dict
        Rows of ``fd_nodes.csv``.
    stats : dict
        Output of :func:`galerkin_stats` for h as it is.
    stats_centred : dict
        Output of :func:`galerkin_stats` for h minus its sample mean.

    Returns
    -------
    list of dict
        The rows written to ``summary.csv``.
    """
    sizes = sorted({n for _, n, _ in stats if np.isfinite(n)})
    degrees = sorted({k for _, _, k in stats})
    out = []
    for case in CASES:
        row = {"case": case}
        for bc in ("zero_flux", "exact_neumann"):
            sel = sorted((r["n_nodes"], r["err_common"]) for r in fd_rows
                         if r["case"] == case and r["bc"] == bc)
            n, err = np.array(sel).T
            row[f"fd_{bc}_err_finest"] = err[-1]
            row[f"fd_{bc}_order_last"] = (np.log(err[-2] / err[-1])
                                          / np.log(n[-1] / n[-2]))
        exact = {k: stats[(case, np.inf, k)][0] for k in degrees}
        row["galerkin_inf_err_Kmax"] = exact[degrees[-1]]
        for n in sizes:
            for tag, group in (("", stats), ("_centred", stats_centred)):
                med = {k: np.median(group[(case, n, k)]) for k in degrees}
                best = min(med, key=med.get)
                row[f"galerkin{tag}_n{int(n)}_best_K"] = best
                row[f"galerkin{tag}_n{int(n)}_best_median_err"] = med[best]
        out.append(row)
    with open(SUMMARIES / "summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(out[0]))
        writer.writeheader()
        for row in out:
            writer.writerow({k: (f"{v:.4g}" if isinstance(v, float) else v)
                             for k, v in row.items()})
    print(f"wrote {(SUMMARIES / 'summary.csv').relative_to(REPO)}")
    return out


def main():
    """
    Read a run directory and write the figures and the summary table.
    """
    if len(sys.argv) > 1:
        run = Path(sys.argv[1]).resolve()
    else:
        run = sorted(p for p in RUNS.iterdir() if p.is_dir())[-1]
    print(f"run: {run.relative_to(REPO)}")
    SUMMARIES.mkdir(parents=True, exist_ok=True)
    fd_rows = read_csv(run / "fd_nodes.csv")
    galerkin_rows = read_csv(run / "galerkin.csv")
    stats = galerkin_stats(galerkin_rows, centre_h=0)
    stats_centred = galerkin_stats(galerkin_rows, centre_h=1)
    figure_fd_nodes(fd_rows)
    figure_fd_eps(read_csv(run / "fd_eps.csv"))
    figure_galerkin_degree(stats)
    figure_galerkin_samples(stats)
    summary_table(fd_rows, stats, stats_centred)


if __name__ == "__main__":
    main()
