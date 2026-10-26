"""Paper figures for the ground-effect Reinforcement Twinning study.

The user flags below enable independent figures.  The script only reads the
experimental and identification archives; it never modifies source data.
Figures are displayed and saved in ``paper/figures`` as vector PDF and PNG.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
import numpy as np
from scipy.signal import butter, filtfilt, medfilt


plt.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "cm",
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman", "DejaVu Serif"],
    "axes.unicode_minus": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.transparent": False,
})


# =============================================================================
# USER FLAGS
# =============================================================================
PLOT_BASELINE = 0
PLOT_BASELINE_WITH_DT = 1
PLOT_INFORMATION_CONVERGENCE = 1
PLOT_INFORMATION_TRAJECTORIES = 1
PLOT_IDENTIFICATION_QUALITY = 1
PLOT_MODEL_BASED_OPTIMUM = 0
PLOT_PERFORMANCE_INTERMEDIATE_POLICIES = 0
PLOT_PERFORMANCE_POLICY_EXPLORATION = 0
PLOT_PERFORMANCE_REWARD_CALIBRATION = 0
PLOT_PERFORMANCE_TRAJECTORY_COMPARISON = 0
PLOT_PERFORMANCE_EI_REWARD = 0
PLOT_GENERALIZATION_TRAJECTORIES = 0
PLOT_GENERALIZATION_REWARD = 0


# =============================================================================
# USER SETTINGS
# =============================================================================
SAVE_PDF = True
SAVE_PNG = False
SHOW_FIGURES = True
PNG_DPI = 400

BASELINE_CASE = "BL"
MB_OPTIMUM_CASE = "MB"
INTERMEDIATE_CASES = ("INT_01", "INT_02")
ALPHA_EXPLORATION_CASES = tuple(
    f"ALPHA_{index:02d}" for index in range(1, 8)
)
EI_CASES = tuple(f"EI_{index:02d}" for index in range(1, 11))
BEST_EI_CASE = "EI_09"
# Generalization tests: PID, local MB optimum and the nominal EI policy
# transferred through the relative correction law.
GENERALIZATION_CASES = (
    ("BL_V020_Z25", "MB_V020_Z25", "EI_TR_V020_Z25"),
    ("BL_V050_Z10", "MB_V050_Z10", "EI_TR_V050_Z10"),
)
BASELINE_COLOR = "black"
# Global trajectory convention used throughout the paper:
#   reference policy: dashed; experiment: solid; digital twin: dash-dot.
# The DT keeps the EXP hue but uses a lighter shade.
DT_LINESTYLE = "-."
BASELINE_DT_COLOR = "grey"
MB_EXP_COLOR = "#00B050"
MB_DT_COLOR = "lime"
INTERMEDIATE_COLOR = "dodgerblue"
SOBOL_COLOR = "#305B98"
EXPLORATION_COLOR = "blue"
EI_COLOR = "red"
EI_BEST_COLOR = "#C00000"
A_COLOR = "saddlebrown"
P_COLOR = "darkorange"
BROAD_INFORMATION_COLOR = "olive"
NEAR_WALL_INFORMATION_COLOR = "#00B050"

BASELINE_Y_LIMITS = (-0.5, 3.5)
REWARD_X_LIMITS = (0.6, 1.0)
REWARD_Y_LIMITS = (0.4, 1.0)
SOBOL_CANDIDATES = 256
ALPHA_LIMIT = 0.80
RMS_ALPHA = 0.13
AXIS_LABEL_FONTSIZE = 18
LEGEND_FONTSIZE = 14
TICK_LABEL_FONTSIZE = 15

# =============================================================================
# PATHS AND PHYSICAL CONSTANTS
# =============================================================================
PAPER_DIR = Path(__file__).resolve().parent
FIGURES_DIR = PAPER_DIR / "figures"
PROJECT_ROOT = PAPER_DIR.parent
CLEAN_DIR = PROJECT_ROOT / "EXP" / "CLEAN"
EXP_DIR = PROJECT_ROOT / "EXP"
WARM_DIR = PROJECT_ROOT / "identification_output" / "Warm_start"
COLD_DIR = PROJECT_ROOT / "identification_output" / "Cold_start"
DATASET_BOUNDARY_STAGES = {
    "D1": "E03",
    "D2": "E06",
    "D3": "E09",
    "D4": "E12",
}

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from jDT import params  # noqa: E402

R = float(params.ROTOR_RADIUS)
X_SCI_START = float(params.X_ZOOM_START)
X_SCI_END = float(params.X_ZOOM_END)
X_OBSTACLE_START = float(params.OBSTACLE_X_START)
X_OBSTACLE_END = float(params.OBSTACLE_X_END)
TABLE_HEIGHT = float(params.TABLE_HEIGHT_Z)
LIGHTHOUSE_DECK_TO_PROP = float(params.LIGHTHOUSE_DECK_TO_PROP)

MEDIAN_KERNEL = 5
LOWPASS_CUTOFF_HZ = 1.5


def latex_tick(value: float, _position: float) -> str:
    return rf"${value:g}$"


def stage_label(stage: str) -> str:
    return rf"$D_{{{stage.removeprefix('D')}}}$"


def style_axis(ax: plt.Axes, *, grid: bool = True) -> None:
    ax.xaxis.set_major_formatter(FuncFormatter(latex_tick))
    ax.yaxis.set_major_formatter(FuncFormatter(latex_tick))
    ax.tick_params(
        axis="both", which="major", labelsize=TICK_LABEL_FONTSIZE,
        direction="in",
    )
    ax.minorticks_on()
    ax.tick_params(axis="both", which="minor", direction="in")
    if grid:
        ax.grid(True, which="major", color="0.65", alpha=0.28, linewidth=0.7)
        ax.grid(True, which="minor", color="0.75", alpha=0.13, linewidth=0.45)
    for spine in ax.spines.values():
        spine.set_linewidth(1.0)


def add_panel_label(
    ax: plt.Axes,
    label: str,
    *,
    x: float = 0.065,
    y: float = 0.885,
) -> None:
    """Add a consistent circled panel identifier in axes coordinates."""
    ax.text(
        x,
        y,
        rf"$\mathbf{{{label}}}$",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=LEGEND_FONTSIZE + 1,
        color="black",
        bbox={
            "boxstyle": "circle,pad=0.22",
            "facecolor": "white",
            "edgecolor": "black",
            "linewidth": 1.0,
            "alpha": 1.0,
        },
        zorder=20,
        clip_on=True,
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_PDF:
        output = FIGURES_DIR / f"{stem}.pdf"
        fig.savefig(
            output, bbox_inches="tight", pad_inches=0.03,
            facecolor="white", transparent=False,
        )
        print(f"Saved: {output}")
    if SAVE_PNG:
        output = FIGURES_DIR / f"{stem}.png"
        fig.savefig(
            output, dpi=PNG_DPI, bbox_inches="tight", pad_inches=0.03,
            facecolor="white", transparent=False,
        )
        print(f"Saved: {output}")
    if SHOW_FIGURES:
        plt.show()
    else:
        plt.close(fig)


def clean_stem(case: str) -> str:
    """Return the common file stem for one paper-oriented case name."""
    return f"EXP_{case.removeprefix('EXP_')}"


def load_clean_case(case: str) -> tuple[np.ndarray, dict]:
    stem = clean_stem(case)
    clean_path = CLEAN_DIR / f"{stem}_clean.txt"
    metadata_path = CLEAN_DIR / f"{stem}_metadata.json"
    if not clean_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(f"Missing clean case: {stem}")
    data = np.loadtxt(clean_path)
    if data.ndim != 2 or data.shape[1] < 3:
        raise ValueError(f"Unexpected clean-data format: {clean_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return data, metadata


def ensure_scientific_boundaries(
    x: np.ndarray, *signals: np.ndarray,
) -> tuple[np.ndarray, ...]:
    mask = (x >= X_SCI_START) & (x <= X_SCI_END)
    x_cut = np.asarray(x[mask], dtype=float)
    values = [np.asarray(signal[mask], dtype=float) for signal in signals]
    if x_cut.size == 0:
        raise ValueError("No samples in the scientific region")
    if x_cut[0] > X_SCI_START:
        x_cut = np.r_[X_SCI_START, x_cut]
        values = [np.r_[value[0], value] for value in values]
    if x_cut[-1] < X_SCI_END:
        x_cut = np.r_[x_cut, X_SCI_END]
        values = [np.r_[value, value[-1]] for value in values]
    return (x_cut, *values)


def load_trajectory_case(
    case: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    data, metadata = load_clean_case(case)
    x_raw = np.asarray(data[:, 1], dtype=float)
    h_raw = np.asarray(data[:, 2], dtype=float) / R
    x, h_exp = ensure_scientific_boundaries(x_raw, h_raw)

    reference_path = CLEAN_DIR / f"{clean_stem(case)}_RG_input.txt"
    if reference_path.exists():
        reference = np.loadtxt(reference_path)
        h_ref = (
            float(metadata["height_in_rotor_radii"])
            + np.interp(x, reference[:, 0], reference[:, 1]) / R
        )
    else:
        h_ref = np.full_like(x, float(metadata["height_in_rotor_radii"]))
    return x, h_exp, h_ref


def lowpass(signal: np.ndarray, dt: float) -> np.ndarray:
    sample_frequency = 1.0 / dt
    b, a = butter(
        3, LOWPASS_CUTOFF_HZ / (0.5 * sample_frequency), btype="low",
    )
    return filtfilt(b, a, signal)


def load_cleaned_raw_height(path: Path) -> tuple[np.ndarray, np.ndarray]:
    with path.open("r", encoding="utf-8") as stream:
        header = stream.readline().strip().split()
    raw = np.loadtxt(path, skiprows=1)
    columns = {name: raw[:, index] for index, name in enumerate(header)}
    for required in ("t", "x", "z"):
        if required not in columns:
            raise KeyError(f"Column {required!r} missing in {path}")
    t = np.asarray(columns["t"], dtype=float)
    x = np.asarray(columns["x"], dtype=float)
    dt = float(np.median(np.diff(t)))
    h = (
        np.asarray(columns["z"], dtype=float)
        - TABLE_HEIGHT + LIGHTHOUSE_DECK_TO_PROP
    )
    h = lowpass(medfilt(h, MEDIAN_KERNEL), dt)
    order = np.argsort(x)
    x = x[order]
    h = h[order]
    x, unique = np.unique(x, return_index=True)
    return x, h[unique]


def repetition_rms_band(
    case: str, x_reference: np.ndarray, mean_h_over_r: np.ndarray,
) -> tuple[np.ndarray, int]:
    stem = clean_stem(case)
    rms_path = CLEAN_DIR / f"{stem}_rms.txt"
    if rms_path.exists():
        with rms_path.open("r", encoding="utf-8") as stream:
            header = stream.readline().strip().lstrip("#").split()
        stored = np.loadtxt(rms_path, skiprows=1)
        columns = {name: stored[:, index] for index, name in enumerate(header)}
        rms = np.interp(x_reference, columns["x"], columns["z_rms"]) / R
        metadata = json.loads(
            (CLEAN_DIR / f"{stem}_reward.json").read_text(encoding="utf-8")
        )
        return rms, int(metadata.get("number_of_repetitions", 0))

    # Backward-compatible fallback for datasets not yet processed by pp_EXP.
    raw_paths = sorted(EXP_DIR.glob(f"{stem}_*_zoomed.txt"))
    if len(raw_paths) < 2:
        raise FileNotFoundError(
            f"At least two raw repetitions are required for {stem}; "
            f"found {len(raw_paths)}"
        )
    repetitions = []
    for path in raw_paths:
        x_raw, h_raw = load_cleaned_raw_height(path)
        h_interp = np.full(x_reference.shape, np.nan, dtype=float)
        valid = (x_reference >= x_raw[0]) & (x_reference <= x_raw[-1])
        h_interp[valid] = np.interp(x_reference[valid], x_raw, h_raw) / R
        repetitions.append(h_interp)
    squared = (np.asarray(repetitions) - mean_h_over_r[None, :]) ** 2
    counts = np.sum(np.isfinite(squared), axis=0)
    rms = np.full(x_reference.shape, np.nan, dtype=float)
    valid = counts > 0
    rms[valid] = np.sqrt(np.nansum(squared[:, valid], axis=0) / counts[valid])
    finite = np.isfinite(rms)
    if not np.any(finite):
        raise ValueError(f"Raw repetitions do not overlap for {stem}")
    return np.interp(x_reference, x_reference[finite], rms[finite]), len(raw_paths)


def draw_obstacle(ax: plt.Axes, lower_limit: float) -> None:
    start = (X_OBSTACLE_START - X_SCI_START) / R
    end = (X_OBSTACLE_END - X_SCI_START) / R
    ax.fill_between(
        [start, end], lower_limit, 0.0,
        color="0.28", linewidth=0.0, zorder=0,
    )


def plot_reference_and_experiment(
    ax: plt.Axes,
    case: str,
    color: str,
    *,
    reference_label: str = "_nolegend_",
    experiment_label: str = "_nolegend_",
    show_rms: bool = False,
    rms_label: str | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x, h_exp, h_ref = load_trajectory_case(case)
    ell = (x - X_SCI_START) / R
    ax.plot(
        ell, h_ref, color=color, linestyle="--", linewidth=1.8,
        label=reference_label, zorder=2,
    )
    if show_rms:
        rms, repetitions = repetition_rms_band(case, x, h_exp)
        ax.fill_between(
            ell, h_exp - rms, h_exp + rms, color=color,
            alpha=RMS_ALPHA, linewidth=0.0,
            label=(
                rms_label
                if rms_label is not None
                else rf"$\pm\mathrm{{RMS}}_{{\mathrm{{BL}}}}$ "
                     rf"$({repetitions}\ \mathrm{{runs}})$"
            ),
            zorder=1,
        )
    ax.plot(
        ell, h_exp, color=color, linestyle="-", linewidth=2.1,
        label=experiment_label, zorder=3,
    )
    return x, h_exp, h_ref


def plot_dt_trajectory(
    ax: plt.Axes,
    ell: np.ndarray,
    height_over_r: np.ndarray,
    color: str,
    label: str,
    *,
    zorder: float = 4,
) -> None:
    """Plot a DT trajectory using the paper-wide visual convention."""
    ax.plot(
        ell, height_over_r, color=color, linestyle=DT_LINESTYLE,
        linewidth=2.2, label=label, zorder=zorder,
    )


def plot_stage_0_baseline() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.8), constrained_layout=True)
    fig.patch.set_facecolor("white")
    ax.patch.set_facecolor("white")
    draw_obstacle(ax, BASELINE_Y_LIMITS[0])
    plot_reference_and_experiment(
        ax, BASELINE_CASE, BASELINE_COLOR,
        reference_label=r"$\pi_{\mathrm{BL}}$",
        experiment_label=r"$\mathrm{EXP}_{\mathrm{BL}}$",
        show_rms=True,
        rms_label=r"$\pm\mathrm{RMS}_{\mathrm{BL}}$",
    )
    ax.set_xlim(0.0, (X_SCI_END - X_SCI_START) / R)
    ax.set_ylim(*BASELINE_Y_LIMITS)
    ax.set_xlabel(r"$x/R$", fontsize=AXIS_LABEL_FONTSIZE)
    ax.set_ylabel(r"$z/R$", fontsize=AXIS_LABEL_FONTSIZE)
    style_axis(ax)
    handles, labels = ax.get_legend_handles_labels()
    requested_labels = (
        r"$\pi_{\mathrm{BL}}$",
        r"$\mathrm{EXP}_{\mathrm{BL}}$",
        r"$\pm\mathrm{RMS}_{\mathrm{BL}}$",
    )
    order = [labels.index(label) for label in requested_labels]
    ax.legend(
        [handles[index] for index in order],
        [labels[index] for index in order],
        frameon=False,
        fontsize=LEGEND_FONTSIZE,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=3,
    )
    save_figure(fig, "stage_0_pid_baseline")


def final_warm_coefficients() -> np.ndarray:
    path = WARM_DIR / DATASET_BOUNDARY_STAGES["D4"] / "adjoint_results.npz"
    if not path.exists():
        raise FileNotFoundError(f"Final warm adjoint result not found: {path}")
    with np.load(path, allow_pickle=False) as result:
        return np.asarray(result["GE_coeffs"], dtype=float)


def simulate_dt_case(
    case: str,
    x_query: np.ndarray,
    coefficients: np.ndarray | None = None,
) -> np.ndarray:
    # Importing adjoint_identification initializes JAX, so it is delayed.
    # until the DT replay figure is explicitly enabled.
    from adjoint_identification import load_experiments, simulate_aligned

    experiments = load_experiments(cases={case})
    if len(experiments) != 1:
        raise ValueError(
            f"Expected one experiment for {case}, found {len(experiments)}"
        )
    if coefficients is None:
        coefficients = final_warm_coefficients()
    coefficients = np.asarray(coefficients, dtype=float)
    experiment = experiments[0]
    x_dt = np.asarray(experiment.x, dtype=float)
    h_dt = np.asarray(
        simulate_aligned(
            coefficients, experiment, absolute_clearance=True,
        ),
        dtype=float,
    ) / R
    return np.interp(x_query, x_dt, h_dt)


def simulate_dt_baseline(
    x_query: np.ndarray,
    coefficients: np.ndarray | None = None,
) -> np.ndarray:
    return simulate_dt_case(BASELINE_CASE, x_query, coefficients)


def plot_stage_1_baseline_with_dt() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.8), constrained_layout=True)
    fig.patch.set_facecolor("white")
    ax.patch.set_facecolor("white")
    draw_obstacle(ax, BASELINE_Y_LIMITS[0])
    x, h_exp, _ = plot_reference_and_experiment(
        ax, BASELINE_CASE, BASELINE_COLOR,
        reference_label=r"$\pi_{\mathrm{BL}}$",
        experiment_label=r"$\mathrm{EXP}_{\mathrm{BL}}$",
        show_rms=True,
        rms_label=r"$\pm\mathrm{RMS}_{\mathrm{BL}}$",
    )
    ell = (x - X_SCI_START) / R
    cheeseman_bennett = np.array([1.0 / 16.0, 2.0])
    broad_domain_coefficients = load_stage_statistics("D2")[0]
    final_coefficients = final_warm_coefficients()
    plot_dt_trajectory(
        ax, ell, simulate_dt_baseline(x, cheeseman_bennett), "black",
        r"$\mathrm{DT}_{\mathrm{C&B}}$", zorder=3.2,
    )
    plot_dt_trajectory(
        ax, ell, simulate_dt_baseline(x, broad_domain_coefficients),
        BROAD_INFORMATION_COLOR,
        r"$\mathrm{DT}\;(0.5<z/R<6)$", zorder=3.4,
    )
    plot_dt_trajectory(
        ax, ell, simulate_dt_baseline(x, final_coefficients),
        NEAR_WALL_INFORMATION_COLOR,
        r"$\mathrm{DT}$", zorder=3.6,
    )
    ax.set_xlim(0.0, (X_SCI_END - X_SCI_START) / R)
    ax.set_ylim(*BASELINE_Y_LIMITS)
    ax.set_xlabel(r"$x/R$", fontsize=AXIS_LABEL_FONTSIZE)
    ax.set_ylabel(r"$z/R$", fontsize=AXIS_LABEL_FONTSIZE)
    style_axis(ax)
    ax.legend(
        frameon=False,
        fontsize=LEGEND_FONTSIZE,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=3,
    )
    save_figure(fig, "stage_1_baseline_with_converged_dt")


def load_npz_history(path: Path) -> dict[str, np.ndarray]:
    if not path.exists():
        raise FileNotFoundError(f"Adjoint result not found: {path}")
    with np.load(path, allow_pickle=False) as result:
        history = {
            "A": np.asarray(result["a1_history"], dtype=float),
            "p": np.asarray(result["a2_history"], dtype=float),
        }
    if history["A"].size != history["p"].size or history["A"].size < 2:
        raise ValueError(f"Invalid parameter history: {path}")
    return history


def load_optimization_iterations(path: Path) -> int:
    metadata = json.loads(path.read_text(encoding="utf-8"))
    return int(metadata["optimization_iterations"])


def load_cold_history() -> tuple[
    np.ndarray, np.ndarray, np.ndarray, int,
]:
    result_npz = COLD_DIR / "adjoint_results.npz"
    result_json = COLD_DIR / "adjoint_results.json"
    history = load_npz_history(result_npz)
    iterations = load_optimization_iterations(result_json)
    x = np.linspace(0.0, 100.0, history["A"].size)
    return x, history["A"], history["p"], iterations


def cumulative_designed_vs_baseline_eoptimal_information(
    identification_cases: tuple[str, ...],
    episode_coefficients: np.ndarray,
    episode_covariances: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Compare cumulative information from designed and repeated-BL policies.

    A single final twin, parameter scale and residual variance are used for all
    episodes.  The designed branch follows the policies actually deployed,
    while the counterfactual branch repeats the exact 0.35 m/s baseline PID
    experiment for the same number of episodes.
    """
    cache_dir = PAPER_DIR / "cache"
    cache_path = (
        cache_dir / "stage_1_eoptimal_designed_vs_fixed_035_baseline.npz"
    )
    case_array = np.asarray(identification_cases, dtype="U32")
    if cache_path.exists():
        with np.load(cache_path, allow_pickle=False) as cached:
            if (
                np.array_equal(cached["cases"], case_array)
                and np.allclose(cached["coefficients"], episode_coefficients)
                and np.allclose(cached["covariances"], episode_covariances)
            ):
                return (
                    np.asarray(cached["designed"], dtype=float),
                    np.asarray(cached["baseline"], dtype=float),
                )

    # Importing these modules initializes JAX; delay it until this figure is
    # explicitly requested.  The first execution is cached for later plots.
    from dataclasses import replace
    import jax
    import jax.numpy as jnp
    from adjoint_identification import load_experiments, simulate_aligned

    coefficients = np.asarray(episode_coefficients[-1], dtype=float)
    covariance = np.asarray(episode_covariances[-1], dtype=float)
    result_path = WARM_DIR / "E12" / "adjoint_results.npz"
    with np.load(result_path, allow_pickle=False) as result:
        residual_variance = max(float(result["final_loss"]), 1.0e-12)
    parameter_scale = np.sqrt(np.maximum(np.diag(covariance), 1.0e-14))

    designed = np.empty(len(identification_cases), dtype=float)
    baseline = np.empty(len(identification_cases), dtype=float)
    cumulative_designed = np.zeros((2, 2), dtype=float)
    cumulative_baseline = np.zeros((2, 2), dtype=float)

    baseline_experiments = load_experiments(cases={BASELINE_CASE})
    if len(baseline_experiments) != 1:
        raise ValueError(
            f"Expected one baseline replay experiment for {BASELINE_CASE}"
        )
    # Reuse the complete measured baseline episode at every accumulation step:
    # same 0.35 m/s velocity history, altitude, sampling and PID policy.
    baseline_experiment = replace(
        baseline_experiments[0],
        HORIZONTAL_VELOCITY=0.35,
        CONTROL_MODE=0,
        feedforward_x=jnp.asarray(
            [X_SCI_START, X_SCI_END], dtype=jnp.float64,
        ),
        feedforward_pwm=jnp.zeros(2, dtype=jnp.float64),
    )

    for episode_index, case in enumerate(identification_cases):
        experiments = load_experiments(cases={case})
        if len(experiments) != 1:
            raise ValueError(f"Expected one replay experiment for {case}")
        designed_experiment = experiments[0]

        def fisher_matrix(experiment) -> np.ndarray:
            def sampled_clearance(ge_coefficients):
                return (
                    simulate_aligned(
                        ge_coefficients, experiment, absolute_clearance=True,
                    ) / R
                )

            sensitivity = np.asarray(
                jax.jacrev(sampled_clearance)(jnp.asarray(coefficients)),
                dtype=float,
            )
            x = np.asarray(experiment.x, dtype=float)
            mask = (x >= X_OBSTACLE_START) & (x <= X_OBSTACLE_END)
            sensitivity = sensitivity[mask] * parameter_scale[None, :]
            if sensitivity.shape[0] < 2 or not np.all(np.isfinite(sensitivity)):
                raise ValueError(f"Invalid Fisher sensitivity for {case}")
            fisher = (
                sensitivity.T @ sensitivity
                / (residual_variance * sensitivity.shape[0])
            )
            return 0.5 * (fisher + fisher.T)

        cumulative_designed += fisher_matrix(designed_experiment)
        cumulative_baseline += fisher_matrix(baseline_experiment)
        designed[episode_index] = max(float(
            np.linalg.eigvalsh(cumulative_designed)[0]
        ), 0.0)
        baseline[episode_index] = max(float(
            np.linalg.eigvalsh(cumulative_baseline)[0]
        ), 0.0)

    cache_dir.mkdir(parents=True, exist_ok=True)
    np.savez(
        cache_path,
        cases=case_array,
        coefficients=episode_coefficients,
        covariances=episode_covariances,
        designed=designed,
        baseline=baseline,
    )
    return designed, baseline


def plot_stage_1_adjoint_convergence() -> None:
    """Show the converged estimate after each cumulative experiment."""
    episode_stages = tuple(f"E{index:02d}" for index in range(13))
    episode_statistics = tuple(
        load_sequential_statistics(stage) for stage in episode_stages
    )
    episode_coefficients = np.asarray([
        statistics[0] for statistics in episode_statistics
    ])
    episode_covariances = np.asarray([
        statistics[1] for statistics in episode_statistics
    ])
    warm_coefficients = np.vstack((
        np.array([1.0 / 16.0, 2.0]),
        episode_coefficients,
    ))
    x_warm = np.arange(warm_coefficients.shape[0], dtype=float)
    x_final = float(x_warm[-1])

    # Retrospective cumulative Fisher diagnostic.  At episode k, all available
    # experiments are evaluated around the coefficients identified after that
    # episode.  Fisher information and posterior correlation therefore describe
    # the same cumulative identification state.  The two columns are
    # sensitivities of
    #     f_GE(q)=1+A*q**(-p), q=z/R,
    # with respect to dimensionless relative changes of A and p.  Averaging
    # within an episode prevents long recordings from receiving more weight
    # solely because they contain more samples.
    identification_cases = (
        BASELINE_CASE,
        *(f"INF_{index:02d}" for index in range(1, 13)),
    )
    episode_clearances = []
    for case in identification_cases:
        data, _metadata = load_clean_case(case)
        x = np.asarray(data[:, 1], dtype=float)
        q = np.asarray(data[:, 2], dtype=float) / R
        mask = (
            (x >= X_OBSTACLE_START) & (x <= X_OBSTACLE_END)
            & np.isfinite(q) & (q > 0.0)
        )
        if np.count_nonzero(mask) < 2:
            raise ValueError(f"Insufficient Fisher samples for {clean_stem(case)}")
        episode_clearances.append(q[mask])

    conditional_A, conditional_p = [], []
    for episode_index, (current_A, current_p) in enumerate(episode_coefficients):
        cumulative_fisher = np.zeros((2, 2), dtype=float)
        for q in episode_clearances[:episode_index + 1]:
            power = q ** (-current_p)
            sensitivity = np.column_stack((
                current_A * power,
                -current_A * current_p * power * np.log(q),
            ))
            cumulative_fisher += sensitivity.T @ sensitivity / q.size
        F_AA, F_Ap, F_pp = (
            cumulative_fisher[0, 0], cumulative_fisher[0, 1],
            cumulative_fisher[1, 1],
        )
        conditional_A.append(max(F_AA - F_Ap**2 / max(F_pp, 1.0e-14), 0.0))
        conditional_p.append(max(F_pp - F_Ap**2 / max(F_AA, 1.0e-14), 0.0))
    conditional_A = np.asarray(conditional_A)
    conditional_p = np.asarray(conditional_p)
    # Express the cumulative conditional information as a gain over the
    # baseline experiment.  Unlike normalisation by the final dataset, this
    # retains the magnitude of the improvement delivered by the campaign.
    conditional_A /= max(conditional_A[0], 1.0e-14)
    conditional_p /= max(conditional_p[0], 1.0e-14)

    covariance_denominator = np.sqrt(np.maximum(
        episode_covariances[:, 0, 0] * episode_covariances[:, 1, 1],
        1.0e-28,
    ))
    parameter_correlation = (
        episode_covariances[:, 0, 1] / covariance_denominator
    )
    parameter_correlation = np.clip(parameter_correlation, -1.0, 1.0)

    designed_information, baseline_information = (
        cumulative_designed_vs_baseline_eoptimal_information(
            identification_cases,
            episode_coefficients,
            episode_covariances,
        )
    )
    fig, (ax_A, ax_eoptimal, ax_information, ax_correlation) = plt.subplots(
        4, 1, figsize=(8.2, 8.0), constrained_layout=True, sharex=True,
        gridspec_kw={"height_ratios": (3.0, 1.15, 1.05, 1.05)},
    )
    fig.patch.set_facecolor("white")
    ax_p = ax_A.twinx()
    for axis in (ax_A, ax_p, ax_information, ax_correlation, ax_eoptimal):
        axis.patch.set_facecolor("white")

    # Identification phases: baseline PID, broad-domain informative policies,
    # and near-wall informative policies.  C&B at x=0 is the prior model.
    phase_spans = (
        (0.5, 1.5, "grey", 0.16),
        (1.5, 7.5, BROAD_INFORMATION_COLOR, 0.14),
        (7.5, x_final, NEAR_WALL_INFORMATION_COLOR, 0.14),
    )
    for axis in (ax_A, ax_information, ax_correlation, ax_eoptimal):
        for left, right, color, alpha in phase_spans:
            axis.axvspan(
                left, right, color=color, alpha=alpha, linewidth=0.0,
                zorder=0,
            )
        for boundary in (0.5, 1.5, 7.5):
            axis.axvline(
                boundary, color="0.35", linestyle="--", linewidth=0.8,
                alpha=0.55, zorder=1,
            )

    phase_labels = (
        (1.0, r"$\pi_{\mathrm{BL}}$"),
        (4.5, r"$\pi_{\mathrm{INF}}\;(0.5<z/R<6)$"),
        ((7.5 + x_final) / 2.0,
         r"$\pi_{\mathrm{INF}}\;(0.5<z/R<1.5)$"),
    )
    for center, label in phase_labels:
        ax_A.text(
            center, 0.035, label,
            transform=ax_A.get_xaxis_transform(),
            ha="center", va="bottom", fontsize=15.5, color="0.20",
            zorder=4,
        )

    ax_A.plot(
        x_warm, warm_coefficients[:, 0], color=A_COLOR, linestyle="-", linewidth=2.1,
        marker="o", markersize=6.8, markerfacecolor=A_COLOR,
        markeredgecolor=A_COLOR, zorder=3,
    )
    ax_p.plot(
        x_warm, warm_coefficients[:, 1], color=P_COLOR, linestyle="-", linewidth=2.1,
        marker="D", markersize=6.8, markerfacecolor=P_COLOR,
        markeredgecolor=P_COLOR, zorder=3,
    )
    ax_A.set_ylabel(r"$A$", color=A_COLOR, fontsize=AXIS_LABEL_FONTSIZE)
    ax_p.set_ylabel(r"$p$", color=P_COLOR, fontsize=AXIS_LABEL_FONTSIZE)
    ax_A.tick_params(axis="y", colors=A_COLOR)
    ax_p.tick_params(axis="y", colors=P_COLOR)
    ax_A.set_xlim(0.0, x_final)
    ax_A.set_ylim(0.0, 0.3)
    ax_p.set_ylim(0.0, 3.0)
    ax_A.set_xticks(x_warm)
    ax_A.set_xticklabels(
        ("C&B", "BL", *[str(index) for index in range(1, 13)]),
    )
    style_axis(ax_A)
    ax_p.yaxis.set_major_formatter(FuncFormatter(latex_tick))
    ax_p.tick_params(
        axis="y", colors=P_COLOR, labelsize=TICK_LABEL_FONTSIZE,
        direction="in",
    )
    for spine in ax_p.spines.values():
        spine.set_linewidth(1.0)

    legend_handles = [
        Line2D(
            [], [], color=A_COLOR, linestyle="-", linewidth=2.1, marker="o",
            markersize=6.8, label=r"$A$",
        ),
        Line2D(
            [], [], color=P_COLOR, linestyle="-", linewidth=2.1, marker="D",
            markersize=6.8, label=r"$p$",
        ),
    ]
    ax_A.legend(
        handles=legend_handles, frameon=False, fontsize=LEGEND_FONTSIZE,
        loc="best", ncol=2,
    )

    ax_information.plot(
        x_warm[1:], conditional_A,
        color=A_COLOR, linestyle="-", linewidth=2.0, marker="o", markersize=6.0,
        markerfacecolor=A_COLOR, markeredgecolor=A_COLOR,
        label=r"$\mathcal{G}_{A\mid p}$", zorder=3,
    )
    ax_information.plot(
        x_warm[1:], conditional_p,
        color=P_COLOR, linestyle="-", linewidth=2.0, marker="D", markersize=6.0,
        markerfacecolor=P_COLOR, markeredgecolor=P_COLOR,
        label=r"$\mathcal{G}_{p\mid A}$", zorder=3,
    )
    ax_information.set_xlim(0.0, x_final)
    ax_information.set_ylim(0.0, 560.0)
    ax_information.set_xticks(x_warm)
    ax_information.set_xticklabels(
        ("C&B", "BL", *[str(index) for index in range(1, 13)]),
    )
    ax_information.set_ylabel(
        r"$\mathcal{G}_{i\mid j}$",
        fontsize=AXIS_LABEL_FONTSIZE,
    )
    style_axis(ax_information)
    ax_information.legend(
        frameon=False, fontsize=LEGEND_FONTSIZE - 1,
        loc="upper center", bbox_to_anchor=(0.5, 0.99), ncol=2,
    )

    ax_correlation.plot(
        x_warm[1:], parameter_correlation,
        color="0.20", linewidth=2.0, marker="o", markersize=4.7,
        markerfacecolor="0.20", markeredgecolor="0.20", zorder=3,
    )
    ax_correlation.axhline(
        0.0, color="0.45", linestyle=":", linewidth=0.9, zorder=1,
    )
    ax_correlation.set_xlim(0.0, x_final)
    ax_correlation.set_ylim(0.5, 1.0)
    ax_correlation.set_yticks((0.5, 0.75, 1.0))
    ax_correlation.set_xticks(x_warm)
    ax_correlation.set_xticklabels(
        ("C&B", "BL", *[str(index) for index in range(1, 13)]),
    )
    ax_correlation.set_ylabel(
        r"$\rho_{A,p}$", fontsize=AXIS_LABEL_FONTSIZE,
    )
    ax_correlation.set_xlabel(
        r"Cumulative identification episodes", fontsize=AXIS_LABEL_FONTSIZE,
    )
    style_axis(ax_correlation)

    ax_eoptimal.plot(
        x_warm[1:], baseline_information,
        color="0.35", linestyle="--", linewidth=2.0,
        marker="D", markersize=4.7,
        label=r"Repeated $\pi_{\mathrm{BL}}$", zorder=3,
    )
    ax_eoptimal.plot(
        x_warm[1:], designed_information,
        color="black", linestyle="-", linewidth=2.0,
        marker="o", markersize=4.7,
        label=r"Designed $\pi_{\mathrm{INF}}$", zorder=3.2,
    )
    ax_eoptimal.set_xlim(0.0, x_final)
    ax_eoptimal.set_xticks(x_warm)
    ax_eoptimal.set_xticklabels(
        ("C&B", "BL", *[str(index) for index in range(1, 13)]),
    )
    ax_eoptimal.set_ylabel(
        r"$\lambda_{\min}(\mathbf{F})$",
        fontsize=AXIS_LABEL_FONTSIZE,
    )
    style_axis(ax_eoptimal)
    ax_eoptimal.legend(
        frameon=False, fontsize=LEGEND_FONTSIZE - 1,
        loc="upper center", bbox_to_anchor=(0.5, 0.99), ncol=2,
    )

    add_panel_label(ax_A, "a")
    # The lower panels are comparatively shallow: move their labels farther
    # from the upper spine so the circular boxes remain visually separated.
    add_panel_label(ax_eoptimal, "b", y=0.76)
    add_panel_label(ax_information, "c", y=0.76)
    add_panel_label(ax_correlation, "d", y=0.76)

    save_figure(fig, "stage_1_sequential_adjoint_convergence")


def plot_stage_1_informative_trajectories() -> None:
    """Show representative broad-domain and near-wall informative episodes."""
    fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    fig.patch.set_facecolor("white")
    ax.patch.set_facecolor("white")

    y_limits = (-1.5, 8.0)
    draw_obstacle(ax, y_limits[0])
    episodes = (
        (
            "INF_01", "olive",
            r"$\pi_{\mathrm{INF},1}$", r"$\mathrm{EXP}_{\mathrm{INF},1}$",
        ),
        (
            "INF_06", "darkolivegreen",
            r"$\pi_{\mathrm{INF},6}$", r"$\mathrm{EXP}_{\mathrm{INF},6}$",
        ),
        (
            "INF_09", NEAR_WALL_INFORMATION_COLOR,
            r"$\pi_{\mathrm{INF},9}$", r"$\mathrm{EXP}_{\mathrm{INF},9}$",
        ),
    )
    for case, color, policy_label, experiment_label in episodes:
        plot_reference_and_experiment(
            ax,
            case,
            color,
            reference_label=policy_label,
            experiment_label=experiment_label,
        )

    handles, labels = ax.get_legend_handles_labels()
    legend_lookup = dict(zip(labels, handles))
    # Matplotlib fills multi-column legends column by column.  Interleaving
    # each policy/experiment pair therefore produces one policy row followed
    # by one experimental row.
    ordered_labels = tuple(
        label
        for episode in episodes
        for label in (episode[2], episode[3])
    )
    ax.legend(
        [legend_lookup[label] for label in ordered_labels],
        ordered_labels,
        frameon=False,
        fontsize=LEGEND_FONTSIZE,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=3,
    )
    ax.set_xlim(0.0, 100.0)
    ax.set_ylim(*y_limits)
    ax.set_xlabel(r"$x/R$", fontsize=AXIS_LABEL_FONTSIZE)
    ax.set_ylabel(r"$z/R$", fontsize=AXIS_LABEL_FONTSIZE)
    style_axis(ax)
    save_figure(fig, "stage_1_representative_informative_trajectories")


def load_sequential_statistics(stage: str) -> tuple[np.ndarray, np.ndarray]:
    path = WARM_DIR / stage / "adjoint_results.npz"
    with np.load(path, allow_pickle=False) as result:
        coefficients = np.asarray(result["GE_coeffs"], dtype=float)
        covariance = np.asarray(result["GE_covariance"], dtype=float)
    if coefficients.shape != (2,) or covariance.shape != (2, 2):
        raise ValueError(f"Invalid GE statistics in {path}")
    return coefficients, covariance


def load_stage_statistics(stage: str) -> tuple[np.ndarray, np.ndarray]:
    """Load the sequential episode corresponding to a D1--D4 boundary."""
    if stage not in DATASET_BOUNDARY_STAGES:
        raise KeyError(f"Unknown cumulative dataset: {stage}")
    return load_sequential_statistics(DATASET_BOUNDARY_STAGES[stage])


def propagated_f_ge_uncertainty(
    height_over_r: np.ndarray,
    coefficients: np.ndarray,
    covariance: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return f_GE and its local 1-sigma uncertainty via the delta method."""
    A, p = coefficients
    inverse_height = 1.0 / np.asarray(height_over_r, dtype=float)
    power = inverse_height ** p
    f_ge = 1.0 + A * power
    jacobian = np.column_stack((power, A * power * np.log(inverse_height)))
    variance = np.einsum("ni,ij,nj->n", jacobian, covariance, jacobian)
    sigma = np.sqrt(np.maximum(variance, 0.0))
    return f_ge, sigma


def plot_stage_1_identification_quality() -> None:
    """Compare the classical, pre-focus, and final identified GE response."""
    BROAD_DOMAIN_COLOR = BROAD_INFORMATION_COLOR
    FINAL_COLOR = NEAR_WALL_INFORMATION_COLOR
    d2_coefficients, d2_covariance = load_stage_statistics("D2")
    final_coefficients, final_covariance = load_stage_statistics("D4")

    fig, (ax_function, ax_uncertainty) = plt.subplots(
        2, 1, figsize=(7.2, 5.7), constrained_layout=True, sharex=True,
        gridspec_kw={"height_ratios": (2.0, 1.0)},
    )
    fig.patch.set_facecolor("white")
    for axis in (ax_function, ax_uncertainty):
        axis.patch.set_facecolor("white")

    height_over_r = np.linspace(1.0, 6.0, 301)
    classical_f_ge = 1.0 + (1.0 / 16.0) * height_over_r ** (-2.0)
    d2_f_ge, d2_sigma = propagated_f_ge_uncertainty(
        height_over_r, d2_coefficients, d2_covariance,
    )
    final_f_ge, final_sigma = propagated_f_ge_uncertainty(
        height_over_r, final_coefficients, final_covariance,
    )
    ax_function.plot(
        height_over_r, classical_f_ge, color="black", linestyle="--",
        linewidth=1.9, label=r"Cheeseman-Bennett", zorder=2,
    )
    ax_function.plot(
        height_over_r, d2_f_ge, color=BROAD_DOMAIN_COLOR,
        linestyle="-.", linewidth=2.1,
        label=r"$f_{\mathrm{GE}}\;(0.5<z/R<6)$", zorder=2,
    )
    ax_function.plot(
        height_over_r, final_f_ge, color=FINAL_COLOR, linewidth=2.6,
        label=r"$f_{\mathrm{GE}}$", zorder=4,
    )
    ax_function.axhline(1.0, color="0.45", linestyle=":", linewidth=1.0)
    ax_function.set_xlim(1.0, 6.0)
    ax_function.set_ylim(1.0, 1.20)
    ax_function.set_ylabel(r"$f_{\mathrm{GE}}$", fontsize=AXIS_LABEL_FONTSIZE)
    style_axis(ax_function)
    ax_function.legend(
        frameon=False, fontsize=LEGEND_FONTSIZE, loc="upper right",
    )

    d2_relative_uncertainty = 100.0 * 2.0 * d2_sigma / d2_f_ge
    final_relative_uncertainty = 100.0 * 2.0 * final_sigma / final_f_ge
    ax_uncertainty.plot(
        height_over_r, d2_relative_uncertainty,
        color=BROAD_DOMAIN_COLOR, linestyle="-.", linewidth=2.1, zorder=2,
    )
    ax_uncertainty.plot(
        height_over_r, final_relative_uncertainty,
        color=FINAL_COLOR, linewidth=2.6, zorder=4,
    )
    ax_uncertainty.set_xlim(1.0, 6.0)
    ax_uncertainty.set_ylim(0.0, 40.0)
    ax_uncertainty.set_xlabel(r"$z/R$", fontsize=AXIS_LABEL_FONTSIZE)
    ax_uncertainty.set_ylabel(
        r"$2\sigma_{f_{\mathrm{GE}}}/f_{\mathrm{GE}}\,[\%]$",
        fontsize=AXIS_LABEL_FONTSIZE,
    )
    style_axis(ax_uncertainty)
    add_panel_label(ax_function, "a")
    add_panel_label(ax_uncertainty, "b", y=0.80)
    save_figure(fig, "stage_1_identification_quality")


def plot_stage_2_mb_optimum() -> None:
    """Compare baseline and model-based optimum in EXP and in the DT."""
    fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    fig.patch.set_facecolor("white")
    ax.patch.set_facecolor("white")
    draw_obstacle(ax, BASELINE_Y_LIMITS[0])

    cases = (
        (
            BASELINE_CASE,
            BASELINE_COLOR,
            None,
            r"$\pi_{\mathrm{BL}}$",
            r"$\mathrm{EXP}_{\mathrm{BL}}$",
            None,
        ),
        (
            MB_OPTIMUM_CASE,
            MB_EXP_COLOR,
            MB_DT_COLOR,
            r"$\pi_{\mathrm{MB}}$",
            r"$\mathrm{EXP}_{\mathrm{MB}}$",
            r"$\mathrm{DT}_{\mathrm{MB}}$",
        ),
    )
    for case, exp_color, dt_color, policy_label, exp_label, dt_label in cases:
        x, _, _ = plot_reference_and_experiment(
            ax,
            case,
            exp_color,
            reference_label=policy_label,
            experiment_label=exp_label,
            show_rms=True,
            rms_label="_nolegend_",
        )
        if dt_color is not None and dt_label is not None:
            ell = (x - X_SCI_START) / R
            plot_dt_trajectory(
                ax,
                ell,
                simulate_dt_case(case, x),
                dt_color,
                dt_label,
            )

    ax.set_xlim(0.0, (X_SCI_END - X_SCI_START) / R)
    ax.set_ylim(*BASELINE_Y_LIMITS)
    ax.set_xlabel(r"$x/R$", fontsize=AXIS_LABEL_FONTSIZE)
    ax.set_ylabel(r"$z/R$", fontsize=AXIS_LABEL_FONTSIZE)
    style_axis(ax)
    ax.legend(
        frameon=False,
        fontsize=LEGEND_FONTSIZE,
        loc="upper left",
        ncol=2,
    )
    save_figure(fig, "stage_2_mb_optimum")


def plot_stage_3_intermediate_policies() -> None:
    """Show the policy interpolation used to initialize reward transfer."""
    fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    fig.patch.set_facecolor("white")
    ax.patch.set_facecolor("white")
    draw_obstacle(ax, BASELINE_Y_LIMITS[0])

    reference_cases = (
        (BASELINE_CASE, BASELINE_COLOR, r"$\pi_{\mathrm{BL}}$", 2.1),
        (
            INTERMEDIATE_CASES[0],
            INTERMEDIATE_COLOR,
            r"$\pi_{k,i}$",
            1.9,
        ),
        (
            INTERMEDIATE_CASES[1],
            INTERMEDIATE_COLOR,
            "_nolegend_",
            1.9,
        ),
        (MB_OPTIMUM_CASE, MB_EXP_COLOR, r"$\pi_{\mathrm{MB}}$", 2.2),
    )
    intermediate_profiles = []
    for case, color, label, linewidth in reference_cases:
        x, _, h_ref = load_trajectory_case(case)
        ell = (x - X_SCI_START) / R
        ax.plot(
            ell,
            h_ref,
            color=color,
            linestyle="--",
            linewidth=linewidth,
            label=label,
            zorder=3,
        )
        if case in INTERMEDIATE_CASES:
            intermediate_profiles.append((ell, h_ref))

    # Identify the two interpolation levels directly on the curves while
    # retaining a single legend entry for the policy family.
    annotation_positions = (27.0, 68.0)
    annotation_texts = (r"$k=1/3$", r"$k=2/3$")
    for (ell, h_ref), ell_label, text in zip(
        intermediate_profiles,
        annotation_positions,
        annotation_texts,
    ):
        h_label = float(np.interp(ell_label, ell, h_ref))
        ax.text(
            ell_label,
            h_label,
            text,
            ha="center",
            va="center",
            fontsize=LEGEND_FONTSIZE,
            color="black",
            bbox={
                "boxstyle": "round,pad=0.18,rounding_size=0.16",
                "facecolor": "white",
                "edgecolor": "black",
                "linewidth": 0.6,
                "alpha": 0.78,
            },
            zorder=10,
        )

    ax.set_xlim(0.0, (X_SCI_END - X_SCI_START) / R)
    ax.set_ylim(*BASELINE_Y_LIMITS)
    ax.set_xlabel(r"$x/R$", fontsize=AXIS_LABEL_FONTSIZE)
    ax.set_ylabel(r"$z/R$", fontsize=AXIS_LABEL_FONTSIZE)
    style_axis(ax)
    ax.legend(
        frameon=False,
        fontsize=LEGEND_FONTSIZE,
        loc="upper left",
        ncol=2,
    )
    save_figure(fig, "stage_3_intermediate_policy_references")


def load_replayed_reward_cases(
    cases: tuple[str, ...],
) -> list[dict]:
    """Replay and return reward data for an explicit ordered case list."""
    from next_mission_design.expected_improvement_policy import replay_rows

    coefficients = final_warm_coefficients()
    rows, _ = replay_rows(coefficients)
    lookup = {str(row["case_name"]): row for row in rows}
    missing = [case for case in cases if case not in lookup]
    if missing:
        # Generalization cases are replayed by the condition-aware pipeline;
        # merge them only when requested to keep nominal figures lightweight.
        from next_mission_design.generalized_policy import build_general_replay

        lookup.update({
            str(row["case_name"]): row
            for row in build_general_replay(coefficients)
        })
    missing = [case for case in cases if case not in lookup]
    if missing:
        raise ValueError(f"Missing replayed reward cases: {missing}")
    return [lookup[case] for case in cases]


def plot_reward_transfer(
    rows: list[dict],
    point_specs: tuple[tuple[int, str, str, str, float, int], ...],
    filename: str,
) -> None:
    """Plot the affine transfer and its policy-dependent GP envelope."""
    from next_mission_design.expected_improvement_policy import RealRewardModel

    model = RealRewardModel(rows)
    reward_dt = np.asarray(
        [row["reward_DT_current"] for row in rows], dtype=float,
    )
    reward_exp = np.asarray(
        [row["reward_EXP"] for row in rows], dtype=float,
    )

    fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    fig.patch.set_facecolor("white")
    ax.patch.set_facecolor("white")

    score_line = np.linspace(*REWARD_X_LIMITS, 250)
    affine_score = (
        1.0 + model.gamma0 + model.gamma1 * (score_line - 1.0)
    )
    ax.plot(
        score_line,
        affine_score,
        color="0.38",
        linewidth=2.0,
        label=(
            r"$\widehat{\mathcal{R}}_{\bullet,\mathrm{aff}}"
            r"(\mathcal{R}_{\circ})$"
        ),
        zorder=2,
    )

    envelope_lower = []
    envelope_upper = []
    for score in score_line:
        raw_reward = score - 1.0
        predictions = [
            model.predict(
                raw_reward,
                row["vx_m_s"],
                row["height_R"],
                coordinates,
            )
            for row, coordinates in zip(rows, model.coordinates)
        ]
        means = np.asarray([prediction[0] for prediction in predictions])
        standard_deviations = np.asarray(
            [prediction[1] for prediction in predictions]
        )
        envelope_lower.append(
            1.0 + np.min(means - 1.645 * standard_deviations)
        )
        envelope_upper.append(
            1.0 + np.max(means + 1.645 * standard_deviations)
        )
    ax.fill_between(
        score_line,
        envelope_lower,
        envelope_upper,
        color="0.45",
        alpha=0.16,
        linewidth=0.0,
        label=(
            r"$\widehat{\mathcal{R}}_{\bullet}="
            r"\widehat{\mathcal{R}}_{\bullet,\mathrm{aff}}+"
            r"\widehat{\delta}(\boldsymbol{\theta}_{\pi})$"
        ),
        zorder=1,
    )

    for index, color, marker, label, size, zorder in point_specs:
        ax.plot(
            1.0 + reward_dt[index],
            1.0 + reward_exp[index],
            marker=marker,
            linestyle="none",
            markersize=size,
            markerfacecolor=color,
            markeredgecolor="none",
            label=label,
            zorder=zorder,
        )

    ax.set_xlim(*REWARD_X_LIMITS)
    ax.set_ylim(*REWARD_Y_LIMITS)
    ax.set_xlabel(r"$\mathcal{R}_{\circ}$", fontsize=AXIS_LABEL_FONTSIZE)
    ax.set_ylabel(r"$\mathcal{R}_{\bullet}$", fontsize=AXIS_LABEL_FONTSIZE)
    style_axis(ax)
    ax.legend(
        frameon=False,
        fontsize=LEGEND_FONTSIZE,
        loc="upper left",
    )
    save_figure(fig, filename)


def plot_stage_4_policy_exploration() -> None:
    """Show the Sobol policy domain and the policies selected for testing."""
    from scipy.stats import qmc
    from next_mission_design.expected_improvement_policy import (
        BASIS_CENTERS, N_BASIS, RANDOM_SEED, basis_matrix,
    )

    x_mb, _, h_mb_source = load_trajectory_case(MB_OPTIMUM_CASE)
    x = np.linspace(X_SCI_START, X_SCI_END, 401)
    h_mb = np.interp(x, x_mb, h_mb_source)
    x_pid, _, h_pid_source = load_trajectory_case(BASELINE_CASE)
    h_pid = np.interp(x, x_pid, h_pid_source)
    ell = (x - X_SCI_START) / R
    bases = basis_matrix(x)

    sampler = qmc.Sobol(d=N_BASIS, scramble=True, seed=RANDOM_SEED)
    power = int(np.ceil(np.log2(SOBOL_CANDIDATES)))
    alpha_samples = qmc.scale(
        sampler.random_base2(power)[:SOBOL_CANDIDATES],
        np.full(N_BASIS, -ALPHA_LIMIT),
        np.full(N_BASIS, +ALPHA_LIMIT),
    )

    fig, ax = plt.subplots(figsize=(7.2, 3.8), constrained_layout=True)
    fig.patch.set_facecolor("white")
    ax.patch.set_facecolor("white")
    draw_obstacle(ax, BASELINE_Y_LIMITS[0])

    for index, alpha in enumerate(alpha_samples):
        ax.plot(
            ell,
            h_mb + bases @ alpha,
            color=SOBOL_COLOR,
            alpha=0.12,
            linewidth=0.9,
            label=(r"$\Pi_{\mathrm{Sobol}}$" if index == 0 else "_nolegend_"),
            zorder=1,
        )

    for case_index, case in enumerate(ALPHA_EXPLORATION_CASES):
        x_case, _, h_ref = load_trajectory_case(case)
        ax.plot(
            (x_case - X_SCI_START) / R,
            h_ref,
            color=EXPLORATION_COLOR,
            linestyle="--",
            linewidth=1.5,
            label=(
                r"$\pi_{\boldsymbol{\alpha},i}$"
                if case_index == 0 else "_nolegend_"
            ),
            zorder=4,
        )

    ax.plot(
        ell, h_pid, color=BASELINE_COLOR, linestyle="--",
        linewidth=2.0, label=r"$\pi_{\mathrm{BL}}$", zorder=5,
    )
    ax.plot(
        ell, h_mb, color=MB_EXP_COLOR, linestyle="--",
        linewidth=2.2, label=r"$\pi_{\mathrm{MB}}$", zorder=6,
    )

    # Draw the basis centers last so markers and annotations remain readable
    # above both the Sobol family and the tested trajectories.
    center_ell = (BASIS_CENTERS - X_SCI_START) / R
    center_height = np.interp(BASIS_CENTERS, x, h_mb)
    ax.scatter(
        center_ell, center_height, s=42, color="black",
        edgecolors="white", linewidths=0.7, zorder=10,
    )
    for label, x_center, y_center in zip("ABC", center_ell, center_height):
        ax.annotate(
            rf"$\mathrm{{{label}}}$",
            (x_center, y_center),
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=15,
            color="black",
            bbox={
                "boxstyle": "round,pad=0.18,rounding_size=0.16",
                "facecolor": "white",
                "edgecolor": "black",
                "linewidth": 0.6,
                "alpha": 0.78,
            },
            zorder=11,
        )

    ax.set_xlim(0.0, (X_SCI_END - X_SCI_START) / R)
    ax.set_ylim(*BASELINE_Y_LIMITS)
    ax.set_xlabel(r"$x/R$", fontsize=AXIS_LABEL_FONTSIZE)
    ax.set_ylabel(r"$z/R$", fontsize=AXIS_LABEL_FONTSIZE)
    style_axis(ax)
    ax.legend(
        frameon=False, fontsize=LEGEND_FONTSIZE, loc="upper left", ncol=2,
    )
    save_figure(fig, "stage_4_sobol_and_tested_policy_references")


def plot_stage_4_reward_transfer() -> None:
    """Update the complete reward transfer with policy-shape exploration."""
    ordered_cases = (
        BASELINE_CASE,
        *INTERMEDIATE_CASES,
        MB_OPTIMUM_CASE,
        *ALPHA_EXPLORATION_CASES,
    )
    rows = load_replayed_reward_cases(ordered_cases)
    point_specs = [
        (0, BASELINE_COLOR, "o", r"$\pi_{\mathrm{BL}}$", 7.5, 6),
        (1, INTERMEDIATE_COLOR, "D", r"$\pi_{k}$", 6.0, 4),
        (2, INTERMEDIATE_COLOR, "D", "_nolegend_", 6.0, 4),
        (3, MB_EXP_COLOR, "s", r"$\pi_{\mathrm{MB}}$", 7.5, 8),
    ]
    for case_index, _case in enumerate(ALPHA_EXPLORATION_CASES):
        index = 4 + case_index
        point_specs.append(
            (
                index,
                EXPLORATION_COLOR,
                "o",
                (
                    r"$\pi_{\boldsymbol{\alpha},i}$"
                    if case_index == 0 else "_nolegend_"
                ),
                5.4,
                5,
            )
        )
    plot_reward_transfer(
        rows,
        tuple(point_specs),
        "stage_4_reward_transfer_after_policy_exploration",
    )


def plot_stage_5_reward_transfer() -> None:
    """Add the EI policy family and highlight the best measured policy."""
    ordered_cases = (
        BASELINE_CASE,
        *INTERMEDIATE_CASES,
        MB_OPTIMUM_CASE,
        *ALPHA_EXPLORATION_CASES,
        *EI_CASES,
    )
    rows = load_replayed_reward_cases(ordered_cases)
    point_specs = [
        (0, BASELINE_COLOR, "o", r"$\pi_{\mathrm{BL}}$", 7.5, 6),
        (1, INTERMEDIATE_COLOR, "D", r"$\pi_{k,i}$", 6.0, 4),
        (2, INTERMEDIATE_COLOR, "D", "_nolegend_", 6.0, 4),
        (3, MB_EXP_COLOR, "s", r"$\pi_{\mathrm{MB}}$", 7.5, 8),
    ]

    for case_index, _case in enumerate(ALPHA_EXPLORATION_CASES):
        index = 4 + case_index
        label = (
            r"$\pi_{\boldsymbol{\alpha},i}$"
            if case_index == 0 else "_nolegend_"
        )
        point_specs.append(
            (index, EXPLORATION_COLOR, "o", label, 5.4, 5)
        )

    first_ei_index = 4 + len(ALPHA_EXPLORATION_CASES)
    regular_ei_label_used = False
    for offset, case in enumerate(EI_CASES):
        index = first_ei_index + offset
        if case == BEST_EI_CASE:
            point_specs.append(
                (
                    index,
                    EI_BEST_COLOR,
                    "*",
                    r"$\pi_{\mathrm{EI}}^{\star}$",
                    12.0,
                    10,
                )
            )
            continue

        label = r"$\pi_{\mathrm{EI},i}$" if not regular_ei_label_used else "_nolegend_"
        regular_ei_label_used = True
        point_specs.append((index, EI_COLOR, "o", label, 5.6, 7))

    plot_reward_transfer(
        rows,
        tuple(point_specs),
        "stage_5_reward_transfer_after_EI",
    )


def plot_stage_5_trajectory_comparison() -> None:
    """Compare baseline, model-based and best EI trajectories."""
    fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    fig.patch.set_facecolor("white")
    ax.patch.set_facecolor("white")
    draw_obstacle(ax, BASELINE_Y_LIMITS[0])

    cases = (
        (
            BASELINE_CASE,
            BASELINE_COLOR,
            r"$\pi_{\mathrm{BL}}$",
            r"$\mathrm{EXP}_{\mathrm{BL}}$",
        ),
        (
            MB_OPTIMUM_CASE,
            MB_EXP_COLOR,
            r"$\pi_{\mathrm{MB}}$",
            r"$\mathrm{EXP}_{\mathrm{MB}}$",
        ),
        (
            BEST_EI_CASE,
            EI_BEST_COLOR,
            r"$\pi_{\mathrm{EI}}^{\star}$",
            r"$\mathrm{EXP}_{\mathrm{EI}}^{\star}$",
        ),
    )
    for case, color, policy_label, experiment_label in cases:
        plot_reference_and_experiment(
            ax,
            case,
            color,
            reference_label=policy_label,
            experiment_label=experiment_label,
            show_rms=True,
            rms_label="_nolegend_",
        )

    ax.set_xlim(0.0, (X_SCI_END - X_SCI_START) / R)
    ax.set_ylim(*BASELINE_Y_LIMITS)
    ax.set_xlabel(r"$x/R$", fontsize=AXIS_LABEL_FONTSIZE)
    ax.set_ylabel(r"$z/R$", fontsize=AXIS_LABEL_FONTSIZE)
    style_axis(ax)
    ax.legend(
        frameon=False,
        fontsize=LEGEND_FONTSIZE,
        loc="upper left",
        ncol=2,
    )
    save_figure(fig, "stage_5_baseline_MB_and_best_EI_trajectories")


def plot_stage_6_generalization() -> None:
    """Compare PID, local MB and transferred EI at two new conditions."""
    fig, axes = plt.subplots(
        2, 1, figsize=(7.2, 6.8), constrained_layout=True, sharex=True,
    )
    fig.patch.set_facecolor("white")

    curve_specs = (
        (
            BASELINE_COLOR,
            r"$\pi_{\mathrm{BL}}$",
            r"$\mathrm{EXP}_{\mathrm{BL}}$",
        ),
        (
            MB_EXP_COLOR,
            r"$\pi_{\mathrm{MB}}$",
            r"$\mathrm{EXP}_{\mathrm{MB}}$",
        ),
        (
            EI_BEST_COLOR,
            r"$\pi_{\mathrm{EI}}^{\mathrm{tr}}$",
            r"$\mathrm{EXP}_{\mathrm{EI}}^{\mathrm{tr}}$",
        ),
    )

    for panel_index, (ax, condition_cases) in enumerate(
        zip(axes, GENERALIZATION_CASES)
    ):
        ax.patch.set_facecolor("white")
        draw_obstacle(ax, -1.0)
        for case, (color, policy_label, experiment_label) in zip(
            condition_cases, curve_specs
        ):
            if panel_index > 0:
                policy_label = "_nolegend_"
                experiment_label = "_nolegend_"
            plot_reference_and_experiment(
                ax,
                case,
                color,
                reference_label=policy_label,
                experiment_label=experiment_label,
                show_rms=True,
                rms_label="_nolegend_",
            )

        if panel_index == 1:
            plot_reference_and_experiment(
                ax,
                "EI_STAR_V050_Z10",
                "purple",
                reference_label=r"$\pi_{\mathrm{EI}}^{\star}$",
                experiment_label=r"$\mathrm{EXP}_{\mathrm{EI}}^{\star}$",
                show_rms=True,
                rms_label="_nolegend_",
            )

        add_panel_label(
            ax, chr(ord("a") + panel_index), x=0.955, y=0.91,
        )
        ax.set_xlim(0.0, (X_SCI_END - X_SCI_START) / R)
        ax.set_ylim(-1.0, 5.0)
        ax.set_ylabel(r"$z/R$", fontsize=AXIS_LABEL_FONTSIZE)
        style_axis(ax)

    axes[0].legend(
        frameon=False,
        fontsize=LEGEND_FONTSIZE,
        loc="upper left",
        ncol=3,
    )
    axes[1].legend(
        frameon=False,
        fontsize=LEGEND_FONTSIZE,
        loc="upper left",
        ncol=2,
    )
    axes[-1].set_xlabel(r"$x/R$", fontsize=AXIS_LABEL_FONTSIZE)
    save_figure(fig, "stage_6_generalization_trajectory_comparison")


def plot_stage_6_normalized_reward() -> None:
    """Compare PID-normalized DT and EXP rewards across three conditions."""
    nominal_other_cases = (
        *INTERMEDIATE_CASES,
        *ALPHA_EXPLORATION_CASES,
        *(case for case in EI_CASES if case != BEST_EI_CASE),
    )
    conditions = (
        {
            "key": (0.35, 1.50),
            "color": "black",
            "pid": BASELINE_CASE,
            "mb": MB_OPTIMUM_CASE,
            "others": nominal_other_cases,
            "transfer": None,
            "best": BEST_EI_CASE,
        },
        {
            "key": (0.20, 2.50),
            "color": "darkorange",
            "pid": "BL_V020_Z25",
            "mb": "MB_V020_Z25",
            "others": (),
            "transfer": "EI_TR_V020_Z25",
            "best": None,
        },
        {
            "key": (0.50, 1.00),
            "color": "purple",
            "pid": "BL_V050_Z10",
            "mb": "MB_V050_Z10",
            "others": ("EI_01_V050_Z10",),
            "transfer": "EI_TR_V050_Z10",
            "best": "EI_STAR_V050_Z10",
        },
    )

    ordered_cases = []
    for condition in conditions:
        condition_cases = (
            condition["pid"],
            condition["mb"],
            *condition["others"],
            condition["transfer"],
            condition["best"],
        )
        for case in condition_cases:
            if case is not None and case not in ordered_cases:
                ordered_cases.append(case)

    rows = load_replayed_reward_cases(tuple(ordered_cases))
    row_by_case = dict(zip(ordered_cases, rows))

    def normalized_scores(case, pid_case):
        row = row_by_case[case]
        pid = row_by_case[pid_case]
        pid_dt = float(pid["reward_DT_current"])
        pid_exp = float(pid["reward_EXP"])
        if pid_dt >= -1.0e-12 or pid_exp >= -1.0e-12:
            raise ValueError(f"PID case {pid_case} must have negative rewards")
        return (
            1.0 - float(row["reward_DT_current"]) / pid_dt,
            1.0 - float(row["reward_EXP"]) / pid_exp,
        )

    # Rebuild the condition-aware surrogate from the exact normalized rewards
    # displayed below, avoiding any mismatch with legacy reward files.
    from next_mission_design.generalized_policy import (
        GeneralRewardModel,
        load_profile,
        local_mb_scales,
        relative_coordinates,
    )

    x_policy = np.linspace(1.70, 4.00, 161)
    surrogate_rows = []
    for condition in conditions:
        mb_case = condition["mb"]
        mb_policy = load_profile(mb_case, x_policy)
        scales = local_mb_scales(mb_policy, x_policy)
        condition_cases = (
            condition["pid"],
            mb_case,
            *condition["others"],
            condition["transfer"],
            condition["best"],
        )
        for case in condition_cases:
            if case is None:
                continue
            policy = load_profile(case, x_policy)
            beta, _alpha, projection_mse = relative_coordinates(
                policy, mb_policy, x_policy, scales,
            )
            score_dt, score_exp = normalized_scores(case, condition["pid"])
            surrogate_rows.append({
                "beta": beta,
                "projection_mse_R2": projection_mse,
                "vx_m_s": condition["key"][0],
                "height_R": condition["key"][1],
                "score_DT": score_dt,
                "score_EXP": score_exp,
                "score_EXP_noise": 0.01,
            })
    model = GeneralRewardModel(surrogate_rows)

    fig, ax = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    fig.patch.set_facecolor("white")
    ax.patch.set_facecolor("white")

    score_line = np.linspace(-0.05, 1.05, 260)
    affine_line = model.gamma0 + model.gamma1 * score_line
    marginal_curve = []
    envelope_lower = []
    envelope_upper = []
    for score in score_line:
        predictions = [
            model.predict(
                score,
                row["beta"],
                np.sqrt(row["projection_mse_R2"]),
                row["vx_m_s"],
                row["height_R"],
            )
            for row in surrogate_rows
        ]
        means = np.asarray([prediction[0] for prediction in predictions])
        standard_deviations = np.asarray([
            prediction[1] for prediction in predictions
        ])
        # Marginalize the condition-aware GP over the policy/operating-point
        # descriptors represented by the experimental data.  The total
        # variance contains both the mean GP predictive variance and the
        # spread of the conditional GP means (law of total variance).
        mean_marginal = float(np.mean(means))
        variance_marginal = float(np.mean(
            standard_deviations ** 2 + (means - mean_marginal) ** 2
        ))
        std_marginal = np.sqrt(max(variance_marginal, 0.0))
        marginal_curve.append(mean_marginal)
        envelope_lower.append(mean_marginal - 1.645 * std_marginal)
        envelope_upper.append(mean_marginal + 1.645 * std_marginal)
    delta_band = ax.fill_between(
        score_line,
        envelope_lower,
        envelope_upper,
        color="0.55",
        alpha=0.18,
        linewidth=0.0,
        label=(
            r"$\widehat{\mathcal{S}}_{\bullet}="
            r"\widehat{\mathcal{S}}_{\bullet,\mathrm{aff}}+"
            r"\widehat{\delta}(\mathbf{a},v_x,z/R)"
            r"\pm1.645\sigma_{\mathrm{marg}}$"
        ),
        zorder=1,
    )
    ax.plot(
        score_line,
        marginal_curve,
        color="0.45",
        linewidth=1.6,
        linestyle="--",
        label=r"$\widehat{\mathcal{S}}_{\bullet}$",
        zorder=2,
    )
    affine_handle, = ax.plot(
        score_line,
        affine_line,
        color="0.35",
        linewidth=2.0,
        label=(
            r"$\widehat{\mathcal{S}}_{\bullet,\mathrm{aff}}"
            r"(\mathcal{S}_{\circ})$"
        ),
        zorder=2,
    )

    for condition in conditions:
        color = condition["color"]
        pid_case = condition["pid"]

        def draw_case(case, marker, size, zorder):
            if case is None:
                return
            score_dt, score_exp = normalized_scores(case, pid_case)
            ax.scatter(
                score_dt,
                score_exp,
                s=size,
                marker=marker,
                color=color,
                edgecolors="white",
                linewidths=0.65,
                zorder=zorder,
            )

        draw_case(pid_case, "o", 105, 8)
        draw_case(condition["mb"], "s", 86, 8)
        for case in condition["others"]:
            draw_case(case, "o", 34, 6)
        draw_case(condition["transfer"], "D", 82, 9)
        draw_case(condition["best"], "*", 185, 10)

    ax.axhline(0.0, color="0.65", linewidth=0.8, zorder=0)
    ax.axvline(0.0, color="0.65", linewidth=0.8, zorder=0)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel(r"$\mathcal{S}_{\circ}$", fontsize=AXIS_LABEL_FONTSIZE)
    ax.set_ylabel(r"$\mathcal{S}_{\bullet}$", fontsize=AXIS_LABEL_FONTSIZE)
    style_axis(ax)

    condition_handles = [affine_handle, delta_band, *[
        Line2D(
            [], [], marker="o", linestyle="none", markersize=8,
            markerfacecolor=condition["color"], markeredgecolor="white",
            label=(
                rf"$v_x={condition['key'][0]:g}\,\mathrm{{m/s}},\ "
                rf"z/R={condition['key'][1]:g}$"
            ),
        )
        for condition in conditions
    ]]
    condition_legend = ax.legend(
        handles=condition_handles,
        frameon=False,
        fontsize=LEGEND_FONTSIZE,
        loc="upper left",
    )
    ax.add_artist(condition_legend)

    role_handles = (
        Line2D([], [], marker="o", linestyle="none", color="0.35",
               markersize=9, label=r"$\pi_{\mathrm{BL}}$"),
        Line2D([], [], marker="s", linestyle="none", color="0.35",
               markersize=8, label=r"$\pi_{\mathrm{MB}}$"),
        Line2D([], [], marker="o", linestyle="none", color="0.35",
               markersize=5, label=r"$\pi_i$"),
        Line2D([], [], marker="D", linestyle="none", color="0.35",
               markersize=8, label=r"$\pi_{\mathrm{EI}}^{\mathrm{tr}}$"),
        Line2D([], [], marker="*", linestyle="none", color="0.35",
               markersize=12, label=r"$\pi_{\mathrm{EI}}^{\star}$"),
    )
    ax.legend(
        handles=role_handles,
        frameon=False,
        fontsize=LEGEND_FONTSIZE,
        loc="lower right",
        ncol=2,
    )
    save_figure(fig, "stage_6_PID_normalized_reward_generalization")


def main() -> None:
    if PLOT_BASELINE:
        plot_stage_0_baseline()
    if PLOT_BASELINE_WITH_DT:
        plot_stage_1_baseline_with_dt()
    if PLOT_INFORMATION_CONVERGENCE:
        plot_stage_1_adjoint_convergence()
    if PLOT_INFORMATION_TRAJECTORIES:
        plot_stage_1_informative_trajectories()
    if PLOT_IDENTIFICATION_QUALITY:
        plot_stage_1_identification_quality()
    if PLOT_MODEL_BASED_OPTIMUM:
        plot_stage_2_mb_optimum()
    if PLOT_PERFORMANCE_INTERMEDIATE_POLICIES:
        plot_stage_3_intermediate_policies()
    if PLOT_PERFORMANCE_POLICY_EXPLORATION:
        plot_stage_4_policy_exploration()
    if PLOT_PERFORMANCE_REWARD_CALIBRATION:
        plot_stage_4_reward_transfer()
    if PLOT_PERFORMANCE_TRAJECTORY_COMPARISON:
        plot_stage_5_trajectory_comparison()
    if PLOT_PERFORMANCE_EI_REWARD:
        plot_stage_5_reward_transfer()
    if PLOT_GENERALIZATION_TRAJECTORIES:
        plot_stage_6_generalization()
    if PLOT_GENERALIZATION_REWARD:
        plot_stage_6_normalized_reward()


if __name__ == "__main__":
    main()
