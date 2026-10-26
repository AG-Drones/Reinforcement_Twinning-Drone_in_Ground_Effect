"""Refine a model-based vertical policy using experimental rewards."""
from __future__ import annotations

import csv
from datetime import datetime
import gc
import importlib
import json
import os
from pathlib import Path
import shutil

import jax.numpy as jnp
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
import numpy as np
from scipy.special import ndtr
from scipy.stats import qmc

from jDT.main import build_environment
from jDT.postprocessing import vertical_reward
from jDT.params import (FF_X_START, MAX_HORIZONTAL_VELOCITY, OBSTACLE_X_END,
                        OBSTACLE_X_START, ROTOR_RADIUS, X_ZOOM_END)
import adjoint_identification as _adjoint

# Spyder keeps imported modules alive between ``%runfile`` calls.  Reload the
# shared experiment loader so changes to its filename parser take effect
# without requiring the user to restart the console.
_adjoint = importlib.reload(_adjoint)
load_experiments = _adjoint.load_experiments
simulate_aligned = _adjoint.simulate_aligned
from .model_based_policy import (
    MIN_ACTUAL_ROTOR_CLEARANCE, build_spatial_grid,
    minimum_actual_rotor_clearance, next_experiment_iteration_label, run_pid,
    run_reference_governor, save_policy)

ROOT = Path(__file__).resolve().parent.parent
MISSION_FILE = ROOT / "mission_output" / "next_GE_mission_RG_performance.npz"
REPLAY_HISTORY = ROOT / "rt_replay_output" / "history"
OUTPUT_HISTORY = ROOT / "rt_policy_output" / "history"
TESTER_HISTORY = ROOT / "test_ref_gov"
PERFORMANCE_TESTER_HISTORY = ROOT / "test_ref_gov_performance"
RT_BASELINE_IDENTIFICATION_FILE = (
    ROOT / "identification_output" / "Warm_start" / "E12"
    / "adjoint_results.npz"
)
RT_BASELINE_PROFILE = (
    ROOT / "EXP" / "CLEAN" / "EXP_MB_RG_input.txt"
)
RT_BASELINE_METADATA = (
    ROOT / "EXP" / "CLEAN" / "EXP_MB_metadata.json"
)
GP_ALPHA_REFERENCE_CASE = "MB"
GP_ALPHA_REFERENCE_PROFILE = (
    ROOT / "EXP" / "CLEAN" / f"EXP_{GP_ALPHA_REFERENCE_CASE}_RG_input.txt"
)
RT_HEIGHT_UPPER_R = 3.0
N_SOBOL_CANDIDATES = 2048
N_LOCAL_CANDIDATES = 128
CHECKPOINT_INTERVAL = 200
SEARCH_CHECKPOINT_FILE = OUTPUT_HISTORY / "RT_policy_search_checkpoint.json"
RESUME_SEARCH_CHECKPOINT = True
RANDOM_SEED = 17
RT_SELECTION_VERSION = "mb_reward_policy_alpha_gp_global_sobol_ei_nominal_v15"
# User option:
#   "mb"           -> original MB reward (global + downstream + peak terms)
#   "simple_z_mse" -> only mean squared z error from the obstacle entrance
#                     to x = 4 m, normalized by the rotor radius
RT_REWARD_MODE = "simple_z_mse"
if RT_REWARD_MODE not in {"mb", "simple_z_mse"}:
    raise ValueError(f"Unknown RT_REWARD_MODE: {RT_REWARD_MODE!r}")
RT_REWARD_END_M = 3.70
# User option.  Keep False while inspecting only the experimental/DT replay
# and its reward-transfer model.  True additionally searches and saves the
# next RT mission.
SEARCH_NEXT_MISSION = 0
RT_REWARD_VERSION = (
    "vertical_tracking_v1" if RT_REWARD_MODE == "mb"
    else "simple_z_mse_obstacle_to_3p70m_v1"
)
RT_TRAINING_FILTER = "performance_pid_policy_alpha_gp_v3_all_subiterations"
N_BASIS = 3
ALPHA_SEED_R = 0.25
BASIS_CENTERS = np.asarray([
    2.50,
    2.95,
    3.30,
])
BASIS_WIDTHS_M = np.asarray([0.25, 0.20, 0.25])
# Global RT search over the same three-dimensional Sobol policy family shown in
# the slides. The Gaussian basis locations and widths remain fixed; only their
# three amplitudes are explored.
ALPHA_LOWER_R = np.full(N_BASIS, -1)
ALPHA_UPPER_R = np.full(N_BASIS, +1)
SHOW_PLOTS = os.environ.get("GE_RG_BATCH_RUN") != "1"
PARAMETER_NAMES = ("alpha_GE_R", "alpha_edge_R", "alpha_post_R")
GP_ALPHA_LENGTH_SCALES_R = np.asarray([0.30, 0.30, 0.30])
INCLUDED_CASES = {
    "BL", "INT_01", "INT_02", "MB",
    *(f"ALPHA_{index:02d}" for index in range(1, 8)),
    *(f"EI_{index:02d}" for index in range(1, 11)),
}
INVALID_CASES = set()

# Optional display subset. By default it is identical to the training set.
# It may be replaced by a smaller positive list without changing the RT fit.
PLOT_INCLUDED_CASES = INCLUDED_CASES


def case_is_selected(row, selectors):
    """Return True when a replay row matches a paper-oriented case name."""
    if row.get("case_name") in selectors:
        return True
    iteration = int(row["iteration_index"])
    trajectory = int(row.get("trajectory_index", 0))
    return iteration in selectors or (iteration, trajectory) in selectors


def case_is_valid(row):
    """Return False for measurements invalidated by an experimental fault."""
    iteration = int(row["iteration_index"])
    trajectory = int(row.get("trajectory_index", 0))
    return (iteration, trajectory) not in INVALID_CASES


def json_numpy_default(value):
    """Convert NumPy values stored in RT diagnostics to plain JSON types."""
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(
        f"Object of type {value.__class__.__name__} is not JSON serializable"
    )


def checkpoint_candidate(item):
    """Return the lightweight, serializable part of one evaluated candidate."""
    return {
        key: value for key, value in item.items()
        if key not in {"policy", "data"}
    }


def save_search_checkpoint(signature, candidates, phase, global_index,
                           local_index=0, local_proposals=None):
    """Atomically save a resumable RT candidate-search checkpoint."""
    payload = {
        "signature": signature,
        "phase": phase,
        "global_index": int(global_index),
        "local_index": int(local_index),
        "local_proposals": ([] if local_proposals is None
                            else np.asarray(local_proposals).tolist()),
        "candidates": [checkpoint_candidate(item) for item in candidates],
    }
    SEARCH_CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = SEARCH_CHECKPOINT_FILE.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, default=json_numpy_default),
        encoding="utf-8",
    )
    temporary.replace(SEARCH_CHECKPOINT_FILE)
    print(
        f"Search checkpoint: {len(candidates)} safe candidates, "
        f"phase={phase}, file={SEARCH_CHECKPOINT_FILE}",
        flush=True,
    )
    gc.collect()


def load_search_checkpoint(signature, x_grid, rg_policy):
    """Load a compatible checkpoint and reconstruct its small policy arrays."""
    if not RESUME_SEARCH_CHECKPOINT or not SEARCH_CHECKPOINT_FILE.exists():
        return None
    payload = json.loads(SEARCH_CHECKPOINT_FILE.read_text(encoding="utf-8"))
    if payload.get("signature") != signature:
        print("Ignoring incompatible RT search checkpoint.", flush=True)
        return None
    candidates = []
    for stored in payload.get("candidates", []):
        item = dict(stored)
        item["theta"] = np.asarray(item["theta"], dtype=float)
        item["gp_alpha_R"] = np.asarray(item["gp_alpha_R"], dtype=float)
        item["policy"] = (
            np.asarray(rg_policy).copy()
            if item["is_exact_mpc"]
            else corrected_policy(x_grid, rg_policy, item["theta"])
        )
        candidates.append(item)
    payload["candidates"] = candidates
    payload["local_proposals"] = np.asarray(
        payload.get("local_proposals", []), dtype=float
    )
    print(
        f"Resuming RT search from {SEARCH_CHECKPOINT_FILE}: "
        f"phase={payload['phase']}, global_index={payload['global_index']}, "
        f"local_index={payload['local_index']}",
        flush=True,
    )
    return payload


def basis_matrix(x):
    """Smooth local corrections, exactly zero at both policy boundaries."""
    x = np.asarray(x, dtype=float)
    gaussian = np.exp(-0.5 * ((x[:, None] - BASIS_CENTERS[None, :])
                              / BASIS_WIDTHS_M[None, :]) ** 2)
    phase = np.clip((x - FF_X_START) / (X_ZOOM_END - FF_X_START), 0.0, 1.0)
    envelope = np.sin(np.pi * phase) ** 2
    basis = gaussian * envelope[:, None]
    basis /= np.maximum(np.max(basis, axis=0, keepdims=True), 1.0e-12)
    return basis


def policy_coordinates(x, delta_z):
    """Represent a policy by three alpha corrections from the fixed MB reference."""
    if not GP_ALPHA_REFERENCE_PROFILE.exists():
        raise FileNotFoundError(
            f"GP alpha-reference profile not found: {GP_ALPHA_REFERENCE_PROFILE}"
        )
    reference = np.loadtxt(GP_ALPHA_REFERENCE_PROFILE, skiprows=1)
    if reference.ndim == 1:
        reference = reference[None, :]
    query = np.linspace(FF_X_START, X_ZOOM_END, 161)
    policy = np.interp(query, np.asarray(x), np.asarray(delta_z))
    baseline = np.interp(query, reference[:, 0], reference[:, 1])
    target = (policy - baseline) / ROTOR_RADIUS
    basis = basis_matrix(query)
    coordinates, *_ = np.linalg.lstsq(basis, target, rcond=None)
    fitted = basis @ coordinates
    return coordinates, float(np.mean((fitted - target) ** 2))


def corrected_policy(x, baseline, alpha):
    policy = np.asarray(baseline) + ROTOR_RADIUS * basis_matrix(x) @ np.asarray(alpha)
    policy[0] = 0.0
    policy[-1] = 0.0
    return policy


def feature(velocity, height_R, alpha_coordinates):
    """Dimensionless GP input formed by the three policy alpha coordinates."""
    del velocity, height_R
    alpha_coordinates = np.asarray(alpha_coordinates, dtype=float)
    return alpha_coordinates / GP_ALPHA_LENGTH_SCALES_R


def regional_rewards(x, z_error):
    """Separate rewards above the obstacle and in the downstream recovery."""
    x = np.asarray(x, dtype=float)
    error_r2 = (np.asarray(z_error, dtype=float) / ROTOR_RADIUS) ** 2
    ge = (x >= OBSTACLE_X_START) & (x <= OBSTACLE_X_END)
    exit_region = (x > OBSTACLE_X_END) & (x <= RT_REWARD_END_M)
    ge_reward = -float(np.mean(error_r2[ge])) if np.any(ge) else 0.0
    exit_reward = -float(np.mean(error_r2[exit_region])) if np.any(exit_region) else 0.0
    return ge_reward, exit_reward


def performance_reward(x, z_error):
    """Return the experimental/DT reward selected by ``RT_REWARD_MODE``."""
    x = np.asarray(x, dtype=float)
    z_error = np.asarray(z_error, dtype=float)
    if RT_REWARD_MODE == "mb":
        return float(vertical_reward(x, z_error))

    scored = (x >= OBSTACLE_X_START) & (x <= RT_REWARD_END_M)
    if not np.any(scored):
        raise ValueError(
            "Reward interval has no samples between the obstacle entrance "
            f"and x={RT_REWARD_END_M:g} m."
        )
    error_r = z_error[scored] / ROTOR_RADIUS
    return -float(np.mean(error_r**2))


def matern32(first, second):
    delta = np.asarray(first)[:, None, :] - np.asarray(second)[None, :, :]
    distance = np.sqrt(np.sum(delta**2, axis=-1))
    scaled = np.sqrt(3.0) * distance
    return (1.0 + scaled) * np.exp(-scaled)


class RealRewardModel:
    """Affine twin trend plus a Matérn GP of the physical discrepancy."""
    def __init__(self, rows, dt_key="reward_DT_current", exp_key="reward_EXP"):
        self.dt_key, self.exp_key = dt_key, exp_key
        self.x_dt = np.asarray([row[dt_key] for row in rows])
        self.y_real = np.asarray([row[exp_key] for row in rows])
        self.features, self.coordinates, self.descriptors, self.fit_errors = [], [], [], []
        for row in rows:
            if row["measured_reference_profile"] is None:
                profile = np.asarray([[FF_X_START, 0.0], [X_ZOOM_END, 0.0]])
            else:
                profile = np.loadtxt(row["measured_reference_profile"], skiprows=1)
            coordinates, error = policy_coordinates(profile[:, 0], profile[:, 1])
            descriptor = coordinates.copy()
            self.coordinates.append(coordinates)
            self.descriptors.append(descriptor)
            self.fit_errors.append(error)
            self.features.append(feature(row["vx_m_s"], row["height_R"], descriptor))
        self.features = np.asarray(self.features)
        # Each cleaned, averaged experimental reward is treated as an exact
        # campaign datum.  Only the tiny diagonal jitter added below remains,
        # for numerical stability of the Cholesky factorization.
        self.noise = np.zeros(len(rows), dtype=float)
        weights = np.ones(len(rows), dtype=float)
        mx, my = np.average(self.x_dt, weights=weights), np.average(self.y_real, weights=weights)
        cx, cy = self.x_dt - mx, self.y_real - my
        self.gamma1 = float(
            np.sum(weights * cx * cy)
            / (np.sum(weights * cx**2) + 1.0e-12)
        )
        self.gamma0 = float(my - self.gamma1 * mx)
        residual = self.y_real - (self.gamma0 + self.gamma1 * self.x_dt)
        self.signal = max(float(np.var(residual)), 0.05**2)
        kernel = self.signal * matern32(self.features, self.features)
        kernel += np.diag(self.noise + 1.0e-8)
        self.cholesky = np.linalg.cholesky(kernel)
        self.alpha = np.linalg.solve(self.cholesky.T,
                                     np.linalg.solve(self.cholesky, residual))

    def predict(self, reward_dt, velocity, height_R, alpha_coordinates):
        query = feature(velocity, height_R, alpha_coordinates)[None, :]
        cross = self.signal * matern32(self.features, query)[:, 0]
        mean = self.gamma0 + self.gamma1 * reward_dt + cross @ self.alpha
        projected = np.linalg.solve(self.cholesky, cross)
        variance = max(self.signal - projected @ projected, 1.0e-8)
        return float(mean), float(np.sqrt(variance))


def expected_improvement(mean, std, incumbent):
    if std <= 1.0e-9:
        return max(mean - incumbent, 0.0)
    z_value = (mean - incumbent) / std
    density = np.exp(-0.5 * z_value**2) / np.sqrt(2.0 * np.pi)
    return float((mean - incumbent) * ndtr(z_value) + std * density)


def save_policy_alpha_table(model, rows, output_path):
    """Save the three GP alpha coordinates assigned to every experiment."""
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow([
            "iteration", "trajectory", *PARAMETER_NAMES,
            "projection_mse", "reward_DT", "reward_EXP", "affine_residual",
        ])
        for row, alpha, error in zip(rows, model.coordinates, model.fit_errors):
            affine = model.gamma0 + model.gamma1 * row[model.dt_key]
            writer.writerow([
                int(row["iteration_index"]),
                int(row.get("trajectory_index", 0)),
                *np.asarray(alpha, dtype=float).tolist(),
                float(error),
                float(row[model.dt_key]),
                float(row[model.exp_key]),
                float(row[model.exp_key] - affine),
            ])


def plot_reward_calibration(model, rows, output_path):
    """Show reward transfer and leave-one-out discrepancy prediction."""
    all_rows = list(rows)
    visible_indices = [
        index for index, row in enumerate(all_rows)
        if case_is_selected(row, PLOT_INCLUDED_CASES)
    ]
    rows = [all_rows[index] for index in visible_indices]
    descriptors = [model.descriptors[index] for index in visible_indices]
    reward_dt = np.asarray([row["reward_DT_current"] for row in rows], dtype=float)
    reward_exp = np.asarray([row["reward_EXP"] for row in rows], dtype=float)
    iterations = np.asarray([row["iteration_index"] for row in rows], dtype=int)
    trajectories = np.asarray([row["trajectory_index"] for row in rows], dtype=int)
    unique_iterations = np.unique(iterations)
    iteration_to_color = {
        iteration: index for index, iteration in enumerate(unique_iterations)
    }
    color_indices = np.asarray(
        [iteration_to_color[iteration] for iteration in iterations], dtype=int
    )
    iteration_cmap = ListedColormap(
        plt.cm.jet(np.linspace(0.0, 1.0, len(unique_iterations)))
    )
    iteration_norm = BoundaryNorm(
        np.arange(len(unique_iterations) + 1) - 0.5, iteration_cmap.N
    )
    affine = model.gamma0 + model.gamma1 * reward_dt
    fitted_delta = []
    predicted_exp = []
    for row, descriptor in zip(rows, descriptors):
        mean, _ = model.predict(row["reward_DT_current"], row["vx_m_s"],
                                row["height_R"], descriptor)
        predicted_exp.append(mean)
        fitted_delta.append(mean - (model.gamma0 + model.gamma1
                                     * row["reward_DT_current"]))
    fitted_delta = np.asarray(fitted_delta)
    predicted_exp = np.asarray(predicted_exp)

    # Honest prediction test: remove each visible experiment, refit on all
    # remaining campaign data, and predict the omitted policy.
    loo_measured_delta, loo_predicted_delta = [], []
    loo_predicted_exp, loo_std = [], []
    for original_index, row, descriptor in zip(
            visible_indices, rows, descriptors):
        training_rows = [
            item for index, item in enumerate(all_rows)
            if index != original_index
        ]
        loo_model = RealRewardModel(training_rows)
        affine_loo = (
            loo_model.gamma0
            + loo_model.gamma1 * row["reward_DT_current"]
        )
        predicted, uncertainty = loo_model.predict(
            row["reward_DT_current"], row["vx_m_s"],
            row["height_R"], descriptor,
        )
        loo_measured_delta.append(row["reward_EXP"] - affine_loo)
        loo_predicted_delta.append(predicted - affine_loo)
        loo_predicted_exp.append(predicted)
        loo_std.append(uncertainty)
    loo_measured_delta = np.asarray(loo_measured_delta)
    loo_predicted_delta = np.asarray(loo_predicted_delta)
    loo_predicted_exp = np.asarray(loo_predicted_exp)
    loo_std = np.asarray(loo_std)
    loo_rmse = float(np.sqrt(np.mean(
        (loo_predicted_delta - loo_measured_delta) ** 2
    )))
    loo_mae = float(np.mean(np.abs(
        loo_predicted_delta - loo_measured_delta
    )))
    print(
        f"LOO discrepancy prediction: RMSE={loo_rmse:.6f}, "
        f"MAE={loo_mae:.6f}",
        flush=True,
    )

    fig, axes = plt.subplots(2, 1, figsize=(6.2, 7.0), constrained_layout=True)
    lower = min(reward_dt.min(), reward_exp.min())
    upper = max(reward_dt.max(), reward_exp.max())
    span = max(upper - lower, 1.0e-6)
    reward_line = np.linspace(lower - 0.05 * span, upper + 0.05 * span, 200)
    axes[0].plot(reward_line, model.gamma0 + model.gamma1 * reward_line,
                 "--", color="0.35", label="affine transfer")
    marker_by_trajectory = {0: "D", 1: "o", 2: "s", 3: "*"}
    points = None
    for trajectory in np.unique(trajectories):
        mask = trajectories == trajectory
        marker = marker_by_trajectory.get(int(trajectory), "P")
        size = 90 if marker == "*" else 48
        label = ("EXP single" if trajectory == 0 else f"EXP _{trajectory}")
        plotted = axes[0].scatter(
            reward_dt[mask], reward_exp[mask], c=color_indices[mask],
            cmap=iteration_cmap, norm=iteration_norm, marker=marker, s=size,
            edgecolor="black", zorder=4, label=label,
        )
        if points is None:
            points = plotted
        fitted_colors = iteration_cmap(iteration_norm(color_indices[mask]))
        axes[0].scatter(
            reward_dt[mask], loo_predicted_exp[mask], marker=marker, s=size,
            facecolors="none", edgecolors=fitted_colors, linewidths=1.5,
            label="leave-one-out prediction"
            if trajectory == np.unique(trajectories)[0] else None,
            zorder=5,
        )
    point_colors = iteration_cmap(iteration_norm(color_indices))
    for x_value, affine_value, measured, color in zip(
            reward_dt, affine, reward_exp, point_colors):
        axes[0].plot([x_value, x_value], [affine_value, measured],
                     color=color, alpha=0.55, lw=0.9)
    axes[0].set(xlabel=r"DT reward $\mathcal{R}^{DT}$",
                ylabel=r"experimental reward $\mathcal{R}^{EXP}$")
    axes[0].set_title(
        rf"$\gamma_0={model.gamma0:.3f}$, $\gamma_1={model.gamma1:.3f}$")
    axes[0].grid(alpha=0.18); axes[0].legend(frameon=False)
    top_colorbar = fig.colorbar(points, ax=axes[0], ticks=np.arange(len(unique_iterations)))
    top_colorbar.ax.set_yticklabels([f"It{value}" for value in unique_iterations])
    top_colorbar.set_label("iteration")

    scatter = None
    for trajectory in np.unique(trajectories):
        mask = trajectories == trajectory
        marker = marker_by_trajectory.get(int(trajectory), "P")
        size = 90 if marker == "*" else 48
        label = ("LOO single" if trajectory == 0 else f"LOO _{trajectory}")
        colors = iteration_cmap(iteration_norm(color_indices[mask]))
        for measured, predicted, uncertainty, color in zip(
                loo_measured_delta[mask], loo_predicted_delta[mask],
                loo_std[mask], colors):
            axes[1].errorbar(
                measured, predicted, yerr=uncertainty, fmt="none",
                ecolor=color, elinewidth=0.8, capsize=2,
                alpha=0.45, zorder=2,
            )
        plotted = axes[1].scatter(
            loo_measured_delta[mask], loo_predicted_delta[mask],
            c=color_indices[mask],
            cmap=iteration_cmap, norm=iteration_norm, marker=marker, s=size,
            edgecolor="black", label=label, zorder=3,
        )
        if scatter is None:
            scatter = plotted
    loo_lower = min(loo_measured_delta.min(), loo_predicted_delta.min())
    loo_upper = max(loo_measured_delta.max(), loo_predicted_delta.max())
    loo_span = max(loo_upper - loo_lower, 1.0e-6)
    loo_line = np.linspace(
        loo_lower - 0.08 * loo_span, loo_upper + 0.08 * loo_span, 100
    )
    axes[1].plot(loo_line, loo_line, "--", color="0.35",
                 label="ideal LOO prediction", zorder=1)
    axes[1].set(
        xlabel=r"measured omitted residual $\delta_{EXP}$",
        ylabel=r"leave-one-out GP prediction $\widehat{\delta}_{LOO}$",
        title=rf"LOO residual prediction: RMSE={loo_rmse:.3f}, MAE={loo_mae:.3f}",
    )
    axes[1].grid(alpha=0.18); axes[1].legend(frameon=False)
    bottom_colorbar = fig.colorbar(
        scatter, ax=axes[1], ticks=np.arange(len(unique_iterations))
    )
    bottom_colorbar.ax.set_yticklabels([f"It{value}" for value in unique_iterations])
    bottom_colorbar.set_label("iteration")
    fig.savefig(output_path, bbox_inches="tight")
    if SHOW_PLOTS:
        plt.show()
    else:
        plt.close(fig)


def replay_rows(coefficients):
    # A cached replay is valid only while no experimental input has changed.
    # Otherwise a newly cleaned RT mission would be silently omitted and the
    # acquisition would propose exactly the same candidate again.
    clean_dir = ROOT / "EXP" / "CLEAN"
    input_paths = [
        path
        for pattern in (
            "EXP_*_clean.txt",
            "EXP_*_reward.json",
            "EXP_*_metadata.json",
            "EXP_*_RG_input.txt",
        )
        for path in clean_dir.glob(pattern)
    ]
    newest_input_mtime = max(
        (path.stat().st_mtime for path in input_paths), default=0.0
    )
    for path in sorted(REPLAY_HISTORY.glob("*/RT_reward_comparison.json"), reverse=True):
        payload = json.loads(path.read_text(encoding="utf-8"))
        archived = np.asarray(payload["GE_coeffs"], dtype=float)
        cached_rows = payload.get("rows", [])
        regional_keys = {"reward_EXP_GE", "reward_EXP_exit",
                         "reward_DT_GE", "reward_DT_exit"}
        if (payload.get("rt_reward_version") == RT_REWARD_VERSION
                and payload.get("training_filter") == RT_TRAINING_FILTER
                and path.stat().st_mtime >= newest_input_mtime
                and archived.shape == coefficients.shape
                and np.allclose(archived, coefficients, rtol=1e-10, atol=1e-10)
                and cached_rows and regional_keys.issubset(cached_rows[0])):
            return cached_rows, path

    rows = []
    for experiment in load_experiments(cases=INCLUDED_CASES):
        clean_dir = ROOT / "EXP" / "CLEAN"
        prefix = f"EXP_{experiment.CASE_NAME}"
        metadata_path = clean_dir / f"{prefix}_metadata.json"
        metadata = (json.loads(metadata_path.read_text(encoding="utf-8"))
                    if metadata_path.exists() else {})
        phase = str(metadata.get("mission_phase", "")).lower()
        is_pid_baseline = experiment.CASE_NAME == "BL"
        is_performance = experiment.CASE_NAME in INCLUDED_CASES - {"BL"}
        if not (is_pid_baseline or is_performance):
            continue
        profile_path = clean_dir / f"{prefix}_RG_input.txt"
        if is_performance and not profile_path.exists():
            continue
        measured_profile = str(profile_path) if is_performance else None
        # The current z-only adjoint returns the aligned vertical history
        # directly.  Older multichannel versions returned a tuple, for which
        # [0] selected z; keeping that index now collapses the history to one
        # scalar and breaks the regional masks below.
        z_dt = simulate_aligned(jnp.asarray(coefficients), experiment)
        exp_ge, exp_exit = regional_rewards(experiment.x, experiment.z_error)
        dt_ge, dt_exit = regional_rewards(experiment.x, z_dt)
        reward_path = clean_dir / f"{prefix}_reward.json"
        reward_data = (json.loads(reward_path.read_text(encoding="utf-8"))
                       if reward_path.exists() else {})
        rows.append({
            "case_name": experiment.CASE_NAME,
            "dataset_index": experiment.DATASET_INDEX,
            "iteration_index": experiment.ITERATION_INDEX,
            "trajectory_index": experiment.TRAJECTORY_INDEX,
            "vx_m_s": experiment.HORIZONTAL_VELOCITY,
            "height_R": experiment.HEIGHT_IN_ROTOR_RADII,
            "reward_EXP": performance_reward(experiment.x, experiment.z_error),
            "reward_EXP_GE": exp_ge,
            "reward_EXP_exit": exp_exit,
            # Stored reward files contain uncertainty for the original MB
            # reward. Do not reuse it for the simple reward.
            "EXP_reward_std": (reward_data.get("standard_deviation")
                               if RT_REWARD_MODE == "mb" else None),
            "EXP_repetitions": reward_data.get("number_of_repetitions", 1),
            "reward_DT_current": performance_reward(experiment.x, z_dt),
            "reward_DT_GE": dt_ge,
            "reward_DT_exit": dt_exit,
            "measured_reference_profile": measured_profile,
            "mission_phase": "pid" if is_pid_baseline else phase,
        })
    if not rows:
        raise FileNotFoundError("RT requires at least one clean RG experiment.")
    path = REPLAY_HISTORY / f"embedded_{datetime.now():%Y%m%d_%H%M%S}" / "RT_reward_comparison.json"
    path.parent.mkdir(parents=True, exist_ok=False)
    path.write_text(json.dumps({"GE_coeffs": np.asarray(coefficients).tolist(),
                                "rt_reward_version": RT_REWARD_VERSION,
                                "training_filter": RT_TRAINING_FILTER,
                                "rows": rows}, indent=2), encoding="utf-8")
    return rows, path


def proposal_set(baseline_coordinates, historical_coordinates):
    sampler = qmc.Sobol(d=N_BASIS, scramble=True, seed=RANDOM_SEED)
    samples = qmc.scale(
        sampler.random_base2(int(np.log2(N_SOBOL_CANDIDATES))),
        ALPHA_LOWER_R, ALPHA_UPPER_R)
    deterministic = [np.zeros(N_BASIS)]
    for index in range(N_BASIS):
        direction = np.zeros(N_BASIS)
        direction[index] = ALPHA_SEED_R
        deterministic.extend((direction.copy(), -direction.copy()))
    transferred = [
        np.clip(np.asarray(item) - baseline_coordinates,
                ALPHA_LOWER_R, ALPHA_UPPER_R)
        for item in historical_coordinates
    ]
    proposed = [*deterministic, *transferred, *samples]
    unique = []
    for alpha in proposed:
        if not any(np.allclose(alpha, old) for old in unique):
            unique.append(np.asarray(alpha))
    return unique


def local_proposal_set(candidates):
    """Refine the most promising first-stage candidates with eight local moves."""
    ranked = sorted(candidates, key=lambda item: item["selection_score"], reverse=True)
    parents = [item["theta"] for item in ranked[:4]]
    rng = np.random.default_rng(RANDOM_SEED + 1)
    proposals = []
    for index in range(N_LOCAL_CANDIDATES):
        parent = np.asarray(parents[index % len(parents)], dtype=float)
        perturbation = rng.normal(0.0, 0.10, size=N_BASIS)
        proposals.append(np.clip(
            parent + perturbation, ALPHA_LOWER_R, ALPHA_UPPER_R
        ))
    return proposals


def load_tester_policy(coefficients, velocity, height_R):
    """Load an existing MPC_tester output; never optimize MPC inside RT."""
    paths = [MISSION_FILE]
    paths.extend(sorted(OUTPUT_HISTORY.glob("*/policy_before_RT.npz"),
                        key=lambda path: path.stat().st_mtime, reverse=True))
    paths.extend(sorted(PERFORMANCE_TESTER_HISTORY.glob(
        "*/next_GE_mission_RG_performance.npz"),
        key=lambda path: path.stat().st_mtime, reverse=True))
    paths.extend(sorted(TESTER_HISTORY.glob("*/next_GE_mission_RG.npz"),
                        key=lambda path: path.stat().st_mtime, reverse=True))
    for path in paths:
        if not path.is_file():
            continue
        with np.load(path, allow_pickle=False) as data:
            source = str(data["policy_source"])
            if (source in {"MB_next_mission", "MB_Performance_NextMission", "MPC_tester_ref_gov", "MPC_tester_ref_gov_high_iteration"}
                    and np.isclose(float(data["horizontal_velocity"]), velocity)
                    and np.isclose(float(data["height_in_rotor_radii"]), height_R)
                    and np.asarray(data["GE_coeffs"]).shape == coefficients.shape
                    and np.allclose(data["GE_coeffs"], coefficients,
                                    rtol=1e-10, atol=1e-10)):
                return {
                    "path": path,
                    "x": np.asarray(data["x_policy"], dtype=float),
                    "delta_z": np.asarray(data["delta_z_reference"], dtype=float),
                    "history": np.asarray(data["cost_history"], dtype=float),
                    "ge_scenarios": (
                        np.asarray(data["robust_GE_scenarios"], dtype=float)
                        if "robust_GE_scenarios" in data.files
                        else np.asarray(data["rt_robust_GE_scenarios"], dtype=float)
                        if "rt_robust_GE_scenarios" in data.files
                        else coefficients[None, :]
                    ),
                }
    # The archived It6 MPC file may have been removed after the experiment.
    # Its applied spatial reference and its adjoint uncertainty are retained
    # in CLEAN and in the identification history, which fully define the MB
    # baseline required by RT.
    if RT_BASELINE_PROFILE.exists() and RT_BASELINE_IDENTIFICATION_FILE.exists():
        profile = np.loadtxt(RT_BASELINE_PROFILE, skiprows=1)
        if profile.ndim == 1:
            profile = profile[None, :]
        x_policy = build_spatial_grid()
        delta_z = np.interp(x_policy, profile[:, 0], profile[:, 1])
        delta_z[0] = delta_z[-1] = 0.0
        with np.load(RT_BASELINE_IDENTIFICATION_FILE, allow_pickle=False) as data:
            archived_coefficients = np.asarray(data["GE_coeffs"], dtype=float)
            covariance = np.asarray(data["GE_covariance"], dtype=float)
        if np.allclose(
                archived_coefficients, coefficients, rtol=1e-10, atol=1e-10):
            values, vectors = np.linalg.eigh(0.5 * (covariance + covariance.T))
            index = int(np.argmax(values))
            shift = 0.50 * np.sqrt(max(float(values[index]), 0.0)) * vectors[:, index]
            ge_scenarios = np.stack([
                archived_coefficients,
                archived_coefficients + shift,
                archived_coefficients - shift,
            ])
            ge_scenarios[:, 1] = np.maximum(ge_scenarios[:, 1], 0.0)
            return {
                "path": RT_BASELINE_PROFILE,
                "x": x_policy,
                "delta_z": delta_z,
                "history": np.empty(0, dtype=float),
                "ge_scenarios": ge_scenarios,
            }
    raise FileNotFoundError(
        "No matching model-based mission output exists for the selected mission "
        "and current GE coefficients. Generate the model-based policy first."
    )


def plot_comparison(x_grid, rg_policy, rt_policy, rg_data, rt_data,
                    candidates, winner, model, training_rows, incumbent, output):
    state_rg, state_rt = np.asarray(rg_data["state"]), np.asarray(rt_data["state"])
    ref_rg, ref_rt = np.asarray(rg_data["reference"]), np.asarray(rt_data["reference"])
    fig, axes = plt.subplots(3, 1, figsize=(7.2, 9.0), constrained_layout=True)
    # Do not subsample a Sobol sequence with a fixed stride: its ordered digital
    # structure can strongly bias the displayed alpha signs even when the full
    # candidate population is balanced.  Draw a fixed, reproducible subset
    # instead so the plot represents the searched policy domain faithfully.
    if len(candidates) <= 300:
        plotted_candidates = candidates
    else:
        plot_rng = np.random.default_rng(RANDOM_SEED + 2)
        plot_indices = np.sort(
            plot_rng.choice(len(candidates), size=300, replace=False)
        )
        plotted_candidates = [candidates[index] for index in plot_indices]
    for item in plotted_candidates:
        axes[0].plot(x_grid, item["policy"] / ROTOR_RADIUS, "--", color="red",
                     alpha=0.22, linewidth=0.8)
    axes[0].plot(x_grid, rg_policy / ROTOR_RADIUS, "-", color="tab:green",
                 linewidth=1.5, label="RG (MPC tester)", zorder=4)
    axes[0].plot(x_grid, rt_policy / ROTOR_RADIUS, "-", color="red",
                 linewidth=1.7, label="RT selected", zorder=6)
    marker_x = np.arange(FF_X_START, X_ZOOM_END + 1e-9, 0.20)
    marker_indices = [int(np.argmin(np.abs(x_grid - value))) for value in marker_x]
    axes[0].plot(x_grid, rg_policy / ROTOR_RADIUS, linestyle="none", marker="D",
                 markevery=marker_indices, markersize=4, color="tab:green", zorder=8)
    axes[0].set_ylabel(r"$\Delta z^*/R$ [-]"); axes[0].legend(frameon=False)
    # Candidate simulations are deliberately not retained in memory.  Only the
    # baseline and selected DT trajectories are plotted; all candidate
    # reference policies remain visible in the panel above.
    axes[1].plot(state_rg[:, 0], (state_rg[:, 2] - ref_rg[:, 2]) / ROTOR_RADIUS,
                 "-", color="tab:green", linewidth=1.5, label="DT with RG", zorder=4)
    axes[1].plot(state_rt[:, 0], (state_rt[:, 2] - ref_rt[:, 2]) / ROTOR_RADIUS,
                 "-", color="red", linewidth=1.7, label="DT with RT", zorder=6)
    response_marker_indices = [
        int(np.argmin(np.abs(state_rg[:, 0] - value))) for value in marker_x
    ]
    axes[1].plot(state_rg[:, 0], (state_rg[:, 2] - ref_rg[:, 2]) / ROTOR_RADIUS,
                 linestyle="none", marker="D", markevery=response_marker_indices,
                 markersize=4, color="tab:green", zorder=8)
    axes[1].set_ylabel(r"$(z-z^*)/R$ [-]"); axes[1].set_ylim(-2, 2)
    axes[1].legend(frameon=False)
    axes[1].set_xlabel(r"$x$ [m]")
    for axis in axes[:2]:
        axis.set_xlim(FF_X_START, X_ZOOM_END)
        axis.axvspan(OBSTACLE_X_START, OBSTACLE_X_END, color="0.92", zorder=0)
        axis.axvline(OBSTACLE_X_START, color="0.45", ls="--", lw=0.8)
        axis.axvline(OBSTACLE_X_END, color="0.45", ls="--", lw=0.8)
        axis.grid(alpha=0.18)

    # Reward-transfer diagnostic.  Historical dots are measured physical
    # rewards; candidate dots are the RT posterior predictions after the GP
    # discrepancy correction.  The dashed line shows only the affine part.
    visible_rows = [
        row for row in training_rows
        if case_is_selected(row, PLOT_INCLUDED_CASES)
    ]
    visible_incumbent = max(row["reward_EXP"] for row in visible_rows)
    historical_dt = np.asarray([row["reward_DT_current"] for row in visible_rows])
    historical_exp = np.asarray([row["reward_EXP"] for row in visible_rows])
    candidate_dt = np.asarray([item["reward_DT"] for item in candidates])
    candidate_exp = np.asarray([item["predicted_reward_EXP"] for item in candidates])
    candidate_std = np.asarray([item["predicted_reward_EXP_std"] for item in candidates])
    reward_min = min(historical_dt.min(), candidate_dt.min())
    reward_max = max(historical_dt.max(), candidate_dt.max())
    reward_line = np.linspace(reward_min, reward_max, 200)
    axes[2].plot(reward_line, model.gamma0 + model.gamma1 * reward_line,
                 "--", color="0.45", linewidth=1.2, label="affine DT transfer")
    axes[2].scatter(historical_dt, historical_exp, s=38, color="black", marker="o",
                    label="measured policies", zorder=5)
    axes[2].errorbar(candidate_dt, candidate_exp, yerr=candidate_std, fmt="o",
                     markersize=3.5, color="red", ecolor="lightcoral", alpha=0.50,
                     elinewidth=0.7, capsize=1.5, label="RT candidates")
    axes[2].errorbar(winner["reward_DT"], winner["predicted_reward_EXP"],
                     yerr=winner["predicted_reward_EXP_std"], fmt="o", markersize=7,
                     color="red", ecolor="red", capsize=3, label="RT selected", zorder=7)
    axes[2].annotate(f"candidate {winner['candidate']}",
                     (winner["reward_DT"], winner["predicted_reward_EXP"]),
                     xytext=(6, 6), textcoords="offset points", fontsize=8)
    axes[2].axhline(visible_incumbent, color="tab:blue", linestyle=":", linewidth=1.0,
                    label=f"visible incumbent = {visible_incumbent:.3f}")
    axes[2].text(0.02, 0.04,
                 rf"$\gamma_0={model.gamma0:.3f}$, $\gamma_1={model.gamma1:.3f}$" "\n"
                 rf"GP signal variance $={model.signal:.4f}$",
                 transform=axes[2].transAxes, fontsize=8,
                 bbox=dict(facecolor="white", edgecolor="0.8", alpha=0.85))
    axes[2].set_xlabel(r"DT reward $\mathcal{R}^{DT}$")
    axes[2].set_ylabel(r"physical/RT reward $\mathcal{R}^{EXP}$")
    axes[2].grid(alpha=0.18)
    axes[2].legend(frameon=False, fontsize=8, ncol=2)
    fig.savefig(output, dpi=200)
    if SHOW_PLOTS:
        plt.show()
    else:
        plt.close(fig)


def main():
    print(f"RT reward mode: {RT_REWARD_MODE} ({RT_REWARD_VERSION})", flush=True)
    if not RT_BASELINE_IDENTIFICATION_FILE.exists():
        raise FileNotFoundError(
            f"RT baseline identification not found: {RT_BASELINE_IDENTIFICATION_FILE}"
        )
    if not RT_BASELINE_METADATA.exists():
        raise FileNotFoundError(
            f"RT baseline metadata not found: {RT_BASELINE_METADATA}"
        )
    if not GP_ALPHA_REFERENCE_PROFILE.exists():
        raise FileNotFoundError(
            f"GP alpha-reference profile not found: {GP_ALPHA_REFERENCE_PROFILE}"
        )
    baseline_metadata = json.loads(RT_BASELINE_METADATA.read_text(encoding="utf-8"))
    velocity = float(baseline_metadata["horizontal_velocity"])
    height_R = float(baseline_metadata["height_in_rotor_radii"])
    campaign = "E12"
    with np.load(RT_BASELINE_IDENTIFICATION_FILE, allow_pickle=False) as data:
        coefficients = np.asarray(data["GE_coeffs"], dtype=float)
    if coefficients.shape != (2,) or not np.all(np.isfinite(coefficients)):
        raise ValueError("The MB mission must contain finite GE coefficients [A, p].")
    if not 0.0 < velocity <= MAX_HORIZONTAL_VELOCITY:
        raise ValueError("Mission velocity outside the domain.")
    if not 0.0 < height_R < RT_HEIGHT_UPPER_R:
        raise ValueError(f"RT requires h/R < {RT_HEIGHT_UPPER_R:g}.")

    rows, replay_path = replay_rows(coefficients)
    omitted_rows = [
        row for row in rows
        if not case_is_selected(row, INCLUDED_CASES) or not case_is_valid(row)
    ]
    rows = [
        row for row in rows
        if case_is_selected(row, INCLUDED_CASES) and case_is_valid(row)
    ]
    if len(rows) < 2:
        raise ValueError("RT requires at least two included experiments.")
    if omitted_rows:
        labels = [str(row["case_name"]) for row in omitted_rows]
        print(
            "Not included in RT fit, LOO and plots: " + ", ".join(labels),
            flush=True,
        )
    included_labels = [str(row["case_name"]) for row in rows]
    print("Included in RT fit: " + ", ".join(included_labels), flush=True)
    model = RealRewardModel(rows)
    model_ge = RealRewardModel(rows, "reward_DT_GE", "reward_EXP_GE")
    model_exit = RealRewardModel(rows, "reward_DT_exit", "reward_EXP_exit")
    output = OUTPUT_HISTORY / f"rt_policy_{datetime.now():%Y%m%d_%H%M%S}"
    output.mkdir(parents=True)
    alpha_table = output / "RT_policy_alpha_coordinates.csv"
    save_policy_alpha_table(model, rows, alpha_table)
    print(f"Policy alpha coordinates saved: {alpha_table}", flush=True)
    calibration_plot = output / "RT_reward_calibration.pdf"
    plot_reward_calibration(model, rows, calibration_plot)
    print(f"RT reward calibration saved: {calibration_plot}", flush=True)
    print(f"gamma0={model.gamma0:.6f}, gamma1={model.gamma1:.6f}", flush=True)
    if not SEARCH_NEXT_MISSION:
        print(
            "Replay-only mode: candidate search disabled; mission_output was not modified.",
            flush=True,
        )
        return
    config, environment, initial = build_environment(
        HORIZONTAL_VELOCITY=velocity, HEIGHT_IN_ROTOR_RADII=height_R,
        use_spatial_trajectory=True)
    trajectory, x_grid = environment.trajectory, build_spatial_grid()
    baseline = run_pid(config, trajectory, initial, coefficients)
    tester = load_tester_policy(coefficients, velocity, height_R)
    print(f"Using existing MPC tester policy: {tester['path']}", flush=True)
    history = tester["history"]
    rg_policy = np.interp(x_grid, tester["x"], tester["delta_z"])
    baseline_coordinates, rg_fit_error = policy_coordinates(x_grid, rg_policy)
    # The latest identified GE coefficients are treated as final for this
    # search.  Evaluating only the nominal model avoids three simulations per
    # candidate and prevents an obsolete covariance from steering RT.
    ge_scenarios = np.asarray([coefficients], dtype=float)
    print(
        "Nominal RT evaluation: one GE model, "
        f"A={coefficients[0]:.6f}, p={coefficients[1]:.6f}",
        flush=True,
    )

    proposals = proposal_set(baseline_coordinates, model.coordinates)
    proposals = [
        np.asarray(alpha, dtype=float)
        for alpha in proposals if not np.allclose(alpha, 0.0)
    ]
    same = [row["reward_EXP"] for row in rows if np.isclose(row["vx_m_s"], velocity)
            and np.isclose(row["height_R"], height_R)]
    incumbent = max(same) if same else max(row["reward_EXP"] for row in rows)
    checkpoint_signature = {
        "selection_version": RT_SELECTION_VERSION,
        "GE_coeffs": coefficients.tolist(),
        "included_cases": [str(item) for item in sorted(INCLUDED_CASES, key=str)],
        "invalid_cases": [str(item) for item in sorted(INVALID_CASES, key=str)],
        "alpha_lower_R": ALPHA_LOWER_R.tolist(),
        "alpha_upper_R": ALPHA_UPPER_R.tolist(),
        "n_sobol": N_SOBOL_CANDIDATES,
        "n_local": N_LOCAL_CANDIDATES,
        "random_seed": RANDOM_SEED,
    }

    def evaluate_candidate(number, alpha, *, exact=False, keep_data=False):
        policy = rg_policy if exact else corrected_policy(x_grid, rg_policy, alpha)
        data = run_reference_governor(
            config, trajectory, initial, x_grid, policy, coefficients
        )
        clearance = minimum_actual_rotor_clearance(config, data)
        if clearance < MIN_ACTUAL_ROTOR_CLEARANCE - 1e-5:
            print(f"candidate {number:04d}: rejected, nominal clearance="
                  f"{clearance/ROTOR_RADIUS:.2f}R")
            return None
        coordinates, _ = policy_coordinates(x_grid, policy)
        descriptor = coordinates
        state, reference = np.asarray(data["state"]), np.asarray(data["reference"])
        error = state[:, 2] - reference[:, 2]
        dt_ge, dt_exit = regional_rewards(state[:, 0], error)
        reward_dt = performance_reward(state[:, 0], error)
        mean, std = model.predict(reward_dt, velocity, height_R, descriptor)
        ge_mean, _ = model_ge.predict(dt_ge, velocity, height_R, descriptor)
        exit_mean, _ = model_exit.predict(dt_exit, velocity, height_R, descriptor)
        robust_std = 0.0
        ei = expected_improvement(mean, std, incumbent)
        item = dict(candidate=number, theta=np.asarray(alpha), policy=policy,
                    gp_alpha_R=np.asarray(coordinates),
                    reward_DT=reward_dt,
                    reward_DT_GE=dt_ge, reward_DT_exit=dt_exit,
                    predicted_reward_EXP=mean,
                    predicted_reward_EXP_GE=ge_mean,
                    predicted_reward_EXP_exit=exit_mean,
                    predicted_reward_EXP_std=std,
                    robust_DT_reward_std=robust_std,
                    selection_score=ei, expected_improvement=ei,
                     minimum_clearance_R=float(clearance / ROTOR_RADIUS),
                    is_twin_fit=False, is_exact_mpc=exact)
        if keep_data:
            item["data"] = data
        print(f"candidate {number:04d}: DT={item['reward_DT']:.3f}, "
              f"EXP={mean:.3f} ± {std:.3f}, "
              f"EI={ei:.4f}")
        return item

    exact = evaluate_candidate(
        0, np.zeros(N_BASIS), exact=True, keep_data=True
    )
    if exact is None:
        raise RuntimeError("The nominal MB reference violates the clearance constraint.")

    resumed = load_search_checkpoint(
        checkpoint_signature, x_grid, rg_policy
    )
    if resumed is None:
        candidates = [exact]
        phase = "global"
        global_index = 0
        local_index = 0
        local_proposals = np.empty((0, N_BASIS), dtype=float)
    else:
        candidates = [exact] + [
            item for item in resumed["candidates"]
            if int(item["candidate"]) != 0
        ]
        phase = resumed["phase"]
        global_index = int(resumed["global_index"])
        local_index = int(resumed["local_index"])
        local_proposals = resumed["local_proposals"]

    if phase == "global":
        for proposal_index in range(global_index, len(proposals)):
            item = evaluate_candidate(proposal_index + 1, proposals[proposal_index])
            if item is not None:
                candidates.append(item)
            global_index = proposal_index + 1
            if global_index % CHECKPOINT_INTERVAL == 0:
                save_search_checkpoint(
                    checkpoint_signature, candidates, "global", global_index
                )
        print("Refining the best first-stage RT candidates locally...", flush=True)
        local_proposals = np.asarray(local_proposal_set(candidates), dtype=float)
        local_index = 0
        phase = "local"
        save_search_checkpoint(
            checkpoint_signature, candidates, phase, global_index,
            local_index, local_proposals,
        )

    if phase == "local":
        for proposal_index in range(local_index, len(local_proposals)):
            number = 1 + len(proposals) + proposal_index
            item = evaluate_candidate(number, local_proposals[proposal_index])
            if item is not None:
                candidates.append(item)
            local_index = proposal_index + 1
            if local_index % CHECKPOINT_INTERVAL == 0:
                save_search_checkpoint(
                    checkpoint_signature, candidates, "local", global_index,
                    local_index, local_proposals,
                )
        phase = "complete"
        save_search_checkpoint(
            checkpoint_signature, candidates, phase, global_index,
            local_index, local_proposals,
        )

    if not candidates:
        raise RuntimeError("No safe RT candidates.")
    winner = max(
        candidates,
        key=lambda item: (item["expected_improvement"], item["predicted_reward_EXP"]),
    )
    if winner["is_exact_mpc"]:
        winner["data"] = exact["data"]
    else:
        winner["data"] = run_reference_governor(
            config, trajectory, initial, x_grid, winner["policy"], coefficients
        )
    rg_data = exact["data"]

    np.savez(
        output / "policy_before_RT.npz",
        x_policy=np.asarray(x_grid),
        delta_z_reference=np.asarray(rg_policy),
        horizontal_velocity=np.asarray(velocity),
        height_in_rotor_radii=np.asarray(height_R),
        GE_coeffs=np.asarray(coefficients),
        cost_history=np.asarray(history),
        policy_source=np.asarray("model_based_policy"),
        identification_iteration=np.asarray(campaign),
        robust_GE_scenarios=np.asarray(ge_scenarios),
    )
    (output / "policy_before_RT.json").write_text(
        json.dumps({
            "policy_source": "model_based_policy",
            "baseline_MB_case": "MB",
            "identification_iteration": campaign,
            "GE_coeffs": coefficients.tolist(),
            "horizontal_velocity": velocity,
            "height_in_rotor_radii": height_R,
        }, indent=2),
        encoding="utf-8",
    )
    selected_source = ("RT_exact_MB_expected_improvement" if winner["is_exact_mpc"]
                       else "RT_residual_basis_expected_improvement")
    save_policy(MISSION_FILE, velocity, height_R, coefficients, x_grid, winner["policy"],
                history, baseline, winner["data"], source=selected_source,
                identification_iteration=campaign,
                experiment_iteration=next_experiment_iteration_label(),
                extra_npz={
                    "rt_selection_version": np.asarray(RT_SELECTION_VERSION),
                    "rt_exact_mpc_in_candidate_set": np.asarray(True),
                    "rt_selected_is_exact_mpc": np.asarray(winner["is_exact_mpc"]),
                    "rt_alpha_R": np.asarray(winner["theta"]),
                    "rt_gp_alpha_R": np.asarray(winner["gp_alpha_R"]),
                    "rt_basis_centers_m": np.asarray(BASIS_CENTERS),
                    "rt_basis_widths_m": np.asarray(BASIS_WIDTHS_M),
                    "rt_baseline_delta_z_reference": np.asarray(rg_policy),
                    "rt_selection_score": np.asarray(winner["selection_score"]),
                    "robust_GE_scenarios": np.asarray(ge_scenarios),
                    "rt_robust_GE_scenarios": np.asarray(ge_scenarios),
                },
                extra_metadata={
                    "rt_selection_version": RT_SELECTION_VERSION,
                    "rt_exact_mpc_in_candidate_set": True,
                    "rt_selected_is_exact_mpc": winner["is_exact_mpc"],
                    "rt_alpha_lower_R": ALPHA_LOWER_R.tolist(),
                    "rt_alpha_upper_R": ALPHA_UPPER_R.tolist(),
                    "rt_basis_centers_m": BASIS_CENTERS.tolist(),
                    "rt_basis_widths_m": BASIS_WIDTHS_M.tolist(),
                    "rt_gp_alpha_reference_case": GP_ALPHA_REFERENCE_CASE,
                    "rt_gp_alpha_length_scales_R": GP_ALPHA_LENGTH_SCALES_R.tolist(),
                    "rt_reward_version": RT_REWARD_VERSION,
                    "rt_acquisition": "expected_improvement",
                    "rt_policy_features": (
                        "three alpha coefficients obtained by projecting the "
                        "policy correction relative to the fixed model-based "
                        "reference onto the local basis functions"
                    ),
                })
    metadata_path = MISSION_FILE.with_suffix(".json")
    metadata = json.loads(metadata_path.read_text())
    metadata["RT_selection"] = dict(parameterization=list(PARAMETER_NAMES),
        selected_parameters=winner["theta"].tolist(),
        selected_is_exact_MPC=winner["is_exact_mpc"],
        predicted_real_reward=winner["predicted_reward_EXP"],
        predicted_real_reward_std=winner["predicted_reward_EXP_std"],
        selection_score=winner["selection_score"],
        expected_improvement_diagnostic=winner["expected_improvement"],
        training_policies=len(rows),
        RT_domain="0 < h/R < 3")
    metadata_path.write_text(json.dumps(metadata, indent=2))
    shutil.copy2(MISSION_FILE, output / MISSION_FILE.name)
    shutil.copy2(metadata_path, output / metadata_path.name)

    serial = []
    for item in candidates:
        row = {key: value for key, value in item.items() if key not in ("theta", "policy", "data")}
        row.update(dict(zip(PARAMETER_NAMES, item["theta"].tolist()))); serial.append(row)
    with (output / "RT_policy_candidates.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(serial[0])); writer.writeheader(); writer.writerows(serial)
    summary = dict(mission=dict(vx_m_s=velocity, height_R=height_R), GE_coeffs=coefficients.tolist(),
        RT_domain="0 < h/R < 3", replay_data=str(replay_path), training_policies=len(rows),
        affine_calibration=dict(gamma0=model.gamma0, gamma1=model.gamma1),
        surrogate="affine DT reward + Matern-3/2 GP discrepancy",
        acquisition="expected improvement of experimental MB reward",
        parameterization=list(PARAMETER_NAMES),
        policy_definition=(
            "z_RT(x)=z_MB(x)+R*[alpha_GE*phi_GE(x)+"
            "alpha_edge*phi_edge(x)+alpha_post*phi_post(x)]"
        ),
        basis_centers_m=BASIS_CENTERS.tolist(), basis_widths_m=BASIS_WIDTHS_M.tolist(),
        GP_features=(
            "signed mean reference over obstacle body; positive mean "
            "reference pre-edge; positive mean reference post-edge"
        ),
        included_cases=[str(item) for item in sorted(INCLUDED_CASES, key=str)],
        invalid_cases=[str(item) for item in sorted(INVALID_CASES, key=str)],
        plot_included_cases=[
            str(item) for item in sorted(PLOT_INCLUDED_CASES, key=str)
        ],
        alpha_bounds_R=dict(
            lower=ALPHA_LOWER_R.tolist(), upper=ALPHA_UPPER_R.tolist()
        ),
        reward_definition=dict(
            version=RT_REWARD_VERSION,
            mode=RT_REWARD_MODE,
            interval_m=[float(OBSTACLE_X_START), float(RT_REWARD_END_M)],
            normalized_by_rotor_radius=True,
            identical_to_MB_Performance=(RT_REWARD_MODE == "mb"),
        ),
        robust_GE_scenarios=np.asarray(ge_scenarios).tolist(),
        MPC_tester_policy_file=str(tester["path"]),
        baseline_policy_coordinates=baseline_coordinates.tolist(),
        baseline_projection_MSE_R2=rg_fit_error,
        selected_candidate=winner["candidate"], selected_parameters=winner["theta"].tolist(),
        selected_is_exact_MPC=winner["is_exact_mpc"],
        selected_predicted_real_reward=winner["predicted_reward_EXP"],
        selected_real_reward_std=winner["predicted_reward_EXP_std"],
        selected_selection_score=winner["selection_score"],
        selected_expected_improvement_diagnostic=winner["expected_improvement"],
        historical_policy_fit_MSE_R2=model.fit_errors, candidate_ranking=serial)
    (output / "RT_policy_selection.json").write_text(
        json.dumps(summary, indent=2, default=json_numpy_default)
    )
    plot_comparison(x_grid, rg_policy, winner["policy"], rg_data, winner["data"],
                    candidates, winner, model, rows, incumbent,
                    output / "RG_vs_RT_comparison.png")
    print(f"\nRT selected candidate {winner['candidate']}")
    print(f"RT selection version: {RT_SELECTION_VERSION}")
    print(f"Selected policy source: {selected_source}")
    print(", ".join(f"{name}={value:.3f}" for name, value in zip(PARAMETER_NAMES, winner["theta"])))
    print(f"Policy for run_next_experiment.py: {MISSION_FILE}\nArchive: {output}")


if __name__ == "__main__": main()

