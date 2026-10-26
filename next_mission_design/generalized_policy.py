"""Condition-aware RT search using corrections relative to each local MB policy."""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import jax.numpy as jnp
from scipy.special import ndtr
from scipy.stats import qmc

from adjoint_identification import load_experiments, simulate_aligned
from jDT.main import build_environment
from jDT.params import ROTOR_RADIUS
from jDT.postprocessing import REWARD_VERSION, vertical_reward
from .model_based_policy import (
    MIN_ACTUAL_ROTOR_CLEARANCE,
    minimum_actual_rotor_clearance,
    run_pid,
    run_reference_governor,
    save_policy,
)
from .expected_improvement_policy import basis_matrix


ROOT = Path(__file__).resolve().parent.parent
CLEAN_DIR = ROOT / "EXP" / "CLEAN"
OUTPUT_DIR = ROOT / "mission_output"
HISTORY_DIR = ROOT / "rt_policy_general_output" / "history"
IDENTIFICATION_FILE = (
    ROOT / "identification_output" / "Warm_start" / "E12"
    / "adjoint_results.npz"
)

# USER SETTINGS
TARGET_VELOCITY = 0.50
TARGET_HEIGHT_R = 1.00
EXPERIMENT_ITERATION = 27
N_SOBOL_CANDIDATES = 2000
N_SELECTED = 3
RANDOM_SEED = 31
SHOW_PRE_EI_OVERVIEW = True

# Retained performance-policy families, using the same names as the paper.
TRAINING_CASES = {
    "BL", "INT_01", "INT_02", "MB",
    *(f"ALPHA_{index:02d}" for index in range(1, 8)),
    *(f"EI_{index:02d}" for index in range(1, 11)),
    "BL_V020_Z25", "MB_V020_Z25", "EI_TR_V020_Z25",
    "BL_V050_Z10", "MB_V050_Z10", "EI_TR_V050_Z10",
    "EI_01_V050_Z10", "EI_STAR_V050_Z10",
}
INVALID_CASES: set[str] = set()

# Local MB anchor used to centre rewards and define relative beta coordinates.
CONDITION_BASELINES = {
    (0.35, 1.50): "MB",
    (0.20, 2.50): "MB_V020_Z25",
    (0.50, 1.00): "MB_V050_Z10",
}

CONDITION_PID_BASELINES = {
    (0.35, 1.50): "BL",
    (0.20, 2.50): "BL_V020_Z25",
    (0.50, 1.00): "BL_V050_Z10",
}

MB_POLICY_FILE = OUTPUT_DIR / "next_GE_mission_RG_rt_calibration_2.npz"
BETA_MIN_SCALE = 0.05
BETA_DOMAIN_MARGIN = 0.35
BETA_DOMAIN_LIMIT = 3.0
MIN_SELECTED_DISTANCE = 0.35


def load_final_ge_coefficients():
    """Always use the final adjoint result, independent of MB manual settings."""
    if not IDENTIFICATION_FILE.exists():
        raise FileNotFoundError(f"Missing final adjoint result: {IDENTIFICATION_FILE}")
    with np.load(IDENTIFICATION_FILE, allow_pickle=False) as data:
        coefficients = np.asarray(data["GE_coeffs"], dtype=float)
    if coefficients.shape != (2,) or not np.all(np.isfinite(coefficients)):
        raise ValueError("Final adjoint GE coefficients must be finite [A, p]")
    return coefficients


def case_key(row):
    return str(row["case_name"])


def condition_key(velocity, height_r):
    return round(float(velocity), 2), round(float(height_r), 2)


def is_selected(row):
    key = case_key(row)
    return key not in INVALID_CASES and key in TRAINING_CASES


def profile_path(case_name):
    return CLEAN_DIR / f"EXP_{case_name}_RG_input.txt"


def load_profile(case_name, x):
    path = profile_path(case_name)
    if not path.exists():
        raise FileNotFoundError(f"Missing reference profile: {path}")
    data = np.loadtxt(path, skiprows=1)
    if data.ndim == 1:
        data = data[None, :]
    values = np.interp(x, data[:, 0], data[:, 1])
    values[0] = values[-1] = 0.0
    return values


def local_mb_scales(mb_policy, x):
    """Positive local MB amplitudes used to make beta dimensionless."""
    basis = basis_matrix(x)
    mb_r = np.asarray(mb_policy, dtype=float) / ROTOR_RADIUS
    weights = np.maximum(np.sum(basis, axis=0), 1.0e-12)
    scales = np.sqrt(np.sum(basis * mb_r[:, None] ** 2, axis=0) / weights)
    return np.maximum(scales, BETA_MIN_SCALE)


def relative_coordinates(policy, mb_policy, x, scales):
    target = (np.asarray(policy) - np.asarray(mb_policy)) / ROTOR_RADIUS
    alpha, *_ = np.linalg.lstsq(basis_matrix(x), target, rcond=None)
    fitted = basis_matrix(x) @ alpha
    error = float(np.mean((fitted - target) ** 2))
    return alpha / scales, alpha, error


def row_lookup(rows):
    return {case_key(row): row for row in rows}


def build_general_replay(coefficients):
    """Replay required policies with the reward definition used by pp_EXP."""
    required_baselines = (
        set(CONDITION_BASELINES.values())
        | set(CONDITION_PID_BASELINES.values())
    )
    rows = []
    requested_cases = TRAINING_CASES | required_baselines
    for experiment in load_experiments(cases=requested_cases):
        key = experiment.CASE_NAME
        selected = key not in INVALID_CASES and key in TRAINING_CASES
        if not selected and key not in required_baselines:
            continue
        prefix = f"EXP_{key}"
        profile = CLEAN_DIR / f"{prefix}_RG_input.txt"
        metadata_path = CLEAN_DIR / f"{prefix}_metadata.json"
        reward_path = CLEAN_DIR / f"{prefix}_reward.json"
        if not metadata_path.exists():
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        phase = str(metadata.get("mission_phase", "")).lower()
        is_pid_anchor = key in set(CONDITION_PID_BASELINES.values())
        if not is_pid_anchor and phase not in {"performance", "rt"}:
            continue
        if not is_pid_anchor and not profile.exists():
            continue
        z_dt = np.asarray(simulate_aligned(jnp.asarray(coefficients), experiment))
        reward_data = (
            json.loads(reward_path.read_text(encoding="utf-8"))
            if reward_path.exists() else {}
        )
        reward_exp = reward_data.get("mean_experimental_reward")
        if reward_exp is None:
            reward_exp = float(vertical_reward(experiment.x, experiment.z_error))
        rows.append({
            "case_name": key,
            "vx_m_s": float(experiment.HORIZONTAL_VELOCITY),
            "height_R": float(experiment.HEIGHT_IN_ROTOR_RADII),
            "reward_EXP": float(reward_exp),
            "reward_EXP_std": float(reward_data.get("standard_deviation", 0.0)),
            "reward_EXP_repetitions": int(reward_data.get("number_of_repetitions", 1)),
            "reward_DT_current": float(vertical_reward(experiment.x, z_dt)),
            "measured_reference_profile": str(profile) if profile.exists() else None,
        })
    if not rows:
        raise FileNotFoundError("No performance experiment available for general RT")
    return rows


def build_training_rows(replay):
    lookup = row_lookup(replay)
    x = np.linspace(1.70, 4.00, 161)
    baseline_cache = {}
    training = []
    for row in replay:
        if not is_selected(row):
            continue
        condition = condition_key(row["vx_m_s"], row["height_R"])
        if condition not in CONDITION_BASELINES:
            continue
        baseline_case = CONDITION_BASELINES[condition]
        pid_case = CONDITION_PID_BASELINES[condition]
        if baseline_case not in lookup:
            raise KeyError(f"Missing replay row for local MB baseline {baseline_case}")
        if pid_case not in lookup:
            raise KeyError(f"Missing replay row for local PID baseline {pid_case}")
        if condition not in baseline_cache:
            mb = load_profile(baseline_case, x)
            baseline_cache[condition] = (
                mb, local_mb_scales(mb, x), lookup[baseline_case], lookup[pid_case]
            )
        mb, scales, baseline_row, pid_row = baseline_cache[condition]
        if row.get("measured_reference_profile") is None:
            policy = np.zeros_like(x)
        else:
            profile = np.loadtxt(row["measured_reference_profile"], skiprows=1)
            if profile.ndim == 1:
                profile = profile[None, :]
            policy = np.interp(x, profile[:, 0], profile[:, 1])
            policy[0] = policy[-1] = 0.0
        beta, alpha, fit_error = relative_coordinates(policy, mb, x, scales)
        pid_reward_dt = float(pid_row["reward_DT_current"])
        pid_reward_exp = float(pid_row["reward_EXP"])
        if pid_reward_dt >= -1.0e-12 or pid_reward_exp >= -1.0e-12:
            raise ValueError(f"PID reward must define a positive cost for {condition}")
        score_dt = 1.0 - float(row["reward_DT_current"]) / pid_reward_dt
        score_exp = 1.0 - float(row["reward_EXP"]) / pid_reward_exp
        score_noise = max(
            float(row.get("reward_EXP_std", 0.0)) / abs(pid_reward_exp),
            0.01,
        )
        training.append({
            **row,
            "condition": condition,
            "baseline_case": baseline_case,
            "beta": beta,
            "alpha": alpha,
            "projection_mse_R2": fit_error,
            "score_DT": score_dt,
            "score_EXP": score_exp,
            "score_EXP_noise": score_noise,
        })
    if len(training) < 6:
        raise RuntimeError("Too few condition-aware RT training policies")
    return training, baseline_cache


def matern32(first, second):
    delta = np.asarray(first)[:, None, :] - np.asarray(second)[None, :, :]
    distance = np.sqrt(np.sum(delta**2, axis=-1))
    scaled = np.sqrt(3.0) * distance
    return (1.0 + scaled) * np.exp(-scaled)


class GeneralRewardModel:
    """PID-normalized DT trend plus condition-aware GP discrepancy."""

    def __init__(self, rows):
        self.rows = rows
        beta = np.asarray([row["beta"] for row in rows], dtype=float)
        operating = np.asarray([
            [row["vx_m_s"], row["height_R"]] for row in rows
        ], dtype=float)
        projection_rmse = np.sqrt(np.asarray([
            row["projection_mse_R2"] for row in rows
        ], dtype=float))[:, None]
        raw_features = np.column_stack((beta, projection_rmse, operating))
        minimum_scales = np.asarray([0.25, 0.25, 0.25, 0.05, 0.10, 0.50])
        self.feature_center = np.mean(raw_features, axis=0)
        self.feature_scale = np.maximum(np.std(raw_features, axis=0), minimum_scales)
        self.features = (raw_features - self.feature_center) / self.feature_scale
        self.x_dt = np.asarray([row["score_DT"] for row in rows])
        self.y_exp = np.asarray([row["score_EXP"] for row in rows])
        self.noise = np.asarray([row["score_EXP_noise"] for row in rows])
        regression = np.column_stack((np.ones(len(rows)), self.x_dt))
        weights = 1.0 / np.maximum(self.noise**2, 1.0e-6)
        normal = regression.T @ (weights[:, None] * regression)
        rhs = regression.T @ (weights * self.y_exp)
        self.gamma0, self.gamma1 = np.linalg.solve(
            normal + np.eye(2) * 1.0e-10, rhs
        )
        self.gamma0, self.gamma1 = float(self.gamma0), float(self.gamma1)
        residual = self.y_exp - (self.gamma0 + self.gamma1 * self.x_dt)
        self.signal = max(float(np.var(residual)), 0.02**2)
        kernel = self.signal * matern32(self.features, self.features)
        kernel += np.diag(self.noise**2 + 1.0e-7)
        self.cholesky = np.linalg.cholesky(kernel)
        self.weights = np.linalg.solve(
            self.cholesky.T,
            np.linalg.solve(self.cholesky, residual),
        )

    def feature(self, beta, projection_rmse, velocity, height_r):
        raw = np.r_[np.asarray(beta, dtype=float), projection_rmse,
                    velocity, height_r]
        return (raw - self.feature_center) / self.feature_scale

    def predict(self, score_dt, beta, projection_rmse, velocity, height_r):
        query = self.feature(beta, projection_rmse, velocity, height_r)[None, :]
        cross = self.signal * matern32(self.features, query)[:, 0]
        mean = self.gamma0 + self.gamma1 * score_dt + cross @ self.weights
        projected = np.linalg.solve(self.cholesky, cross)
        variance = max(self.signal - projected @ projected, 1.0e-8)
        return float(mean), float(np.sqrt(variance))


def expected_improvement(mean, std, incumbent):
    if std <= 1.0e-10:
        return max(mean - incumbent, 0.0)
    z = (mean - incumbent) / std
    density = np.exp(-0.5 * z**2) / np.sqrt(2.0 * np.pi)
    return float((mean - incumbent) * ndtr(z) + std * density)


def candidate_betas(training, local_failed_beta):
    historical = np.vstack([
        np.zeros(3), local_failed_beta,
        *[row["beta"] for row in training],
    ])
    span = np.maximum(np.ptp(historical, axis=0), 0.60)
    lower = np.maximum(np.min(historical, axis=0) - BETA_DOMAIN_MARGIN * span,
                       -BETA_DOMAIN_LIMIT)
    upper = np.minimum(np.max(historical, axis=0) + BETA_DOMAIN_MARGIN * span,
                       BETA_DOMAIN_LIMIT)
    sampler = qmc.Sobol(d=3, scramble=True, seed=RANDOM_SEED)
    unit = sampler.random_base2(int(np.ceil(np.log2(N_SOBOL_CANDIDATES))))
    sobol = qmc.scale(unit, lower, upper)[:N_SOBOL_CANDIDATES]
    line = np.asarray([
        factor * local_failed_beta
        for factor in (-0.50, -0.25, 0.25, 0.50, 0.75)
    ])
    return np.vstack((sobol, line)), lower, upper


def select_distinct(candidates, lower, upper):
    ranked = sorted(candidates, key=lambda item: item["ei"], reverse=True)
    scale = np.maximum(upper - lower, 1.0e-12)
    for threshold in (MIN_SELECTED_DISTANCE, 0.25, 0.15, 0.0):
        selected = []
        for item in ranked:
            if all(np.linalg.norm((item["beta"] - other["beta"]) / scale)
                   >= threshold for other in selected):
                selected.append(item)
            if len(selected) == N_SELECTED:
                return selected
    raise RuntimeError("Unable to select three safe distinct RT candidates")


def plot_pre_ei_overview(model, training, proposals, x_policy, mb_policy,
                         scales, failed_policy, output_path):
    """Show the reward data and candidate library before DT evaluation."""
    fig, axes = plt.subplots(2, 1, figsize=(7.5, 7.2), constrained_layout=True)
    condition_styles = {
        (0.35, 1.50): ("o", "#305B98"),
        (0.20, 2.50): ("s", "#00B050"),
        (0.50, 1.00): ("^", "black"),
    }
    for condition, (marker, color) in condition_styles.items():
        rows = [row for row in training if row["condition"] == condition]
        if not rows:
            continue
        axes[0].scatter(
            [row["score_DT"] for row in rows],
            [row["score_EXP"] for row in rows],
            marker=marker, color=color, edgecolor="white", linewidth=0.5,
            s=45, zorder=4,
            label=rf"$v_x={condition[0]:g}$ m/s, $h/R={condition[1]:g}$",
        )
    reward_values = np.asarray([
        value for row in training
        for value in (row["score_DT"], row["score_EXP"])
    ])
    span = max(float(np.ptp(reward_values)), 0.05)
    reward_line = np.linspace(
        float(np.min(reward_values) - 0.08 * span),
        float(np.max(reward_values) + 0.08 * span), 200,
    )
    axes[0].plot(
        reward_line, model.gamma0 + model.gamma1 * reward_line,
        "--", color="0.35", linewidth=1.3,
        label=r"$\gamma_0+\gamma_1 S^{DT}$",
    )
    axes[0].axhline(0.0, color="0.65", linewidth=0.8)
    axes[0].axvline(0.0, color="0.65", linewidth=0.8)
    axes[0].set(
        xlabel=r"PID-normalized DT score $S^{DT}$",
        ylabel=r"PID-normalized experimental score $S^{EXP}$",
        title="Condition-aware reward data used by EI",
    )
    axes[0].grid(alpha=0.2)
    axes[0].legend(frameon=False, ncol=2)

    basis = basis_matrix(x_policy)
    for beta in proposals:
        alpha = scales * beta
        policy = mb_policy + ROTOR_RADIUS * basis @ alpha
        policy[0] = policy[-1] = 0.0
        axes[1].plot(
            x_policy, policy / ROTOR_RADIUS, color="#C00000",
            linewidth=0.65, alpha=0.10,
        )
    axes[1].plot(
        x_policy, mb_policy / ROTOR_RADIUS, color="#00B050",
        linewidth=2.0, label="local MB",
    )
    axes[1].plot(
        x_policy, failed_policy / ROTOR_RADIUS, "--", color="#E36C0A",
        linewidth=1.7, label="measured transferred RT",
    )
    axes[1].plot([], [], color="#C00000", linewidth=1.0, alpha=0.5,
                 label=f"{len(proposals)} candidates before screening")
    axes[1].set(
        xlabel=r"$x$ [m]", ylabel=r"$\Delta z^*/R$ [-]",
        title="Candidate policies submitted to DT evaluation",
    )
    axes[1].grid(alpha=0.2)
    axes[1].legend(frameon=False)
    fig.savefig(output_path, bbox_inches="tight")
    plt.show()


def save_candidate(number, item, baseline_data, ge, x_policy, history):
    path = OUTPUT_DIR / f"next_GE_mission_RG_rt_general_{number}.npz"
    save_policy(
        path, TARGET_VELOCITY, TARGET_HEIGHT_R, ge, x_policy,
        item["policy"], history, baseline_data, item["data"],
        source="RT_General",
        identification_iteration="latest",
        experiment_iteration=f"iteration_{EXPERIMENT_ITERATION:03d}",
        extra_npz={
            "relative_beta": item["beta"],
            "dimensional_alpha_R": item["alpha"],
            "normalized_score_DT": item["score_DT"],
            "predicted_normalized_score_EXP": item["mean"],
            "predicted_normalized_score_EXP_std": item["std"],
            "expected_improvement": item["ei"],
        },
        extra_metadata={
            "mission_phase": "rt",
            "mission_design": "condition_aware_general_rt",
            "trajectory_number": number,
            "relative_beta": item["beta"].tolist(),
            "dimensional_alpha_R": item["alpha"].tolist(),
            "normalized_score_DT": item["score_DT"],
            "predicted_normalized_score_EXP": item["mean"],
            "predicted_normalized_score_EXP_std": item["std"],
            "expected_improvement": item["ei"],
            "minimum_clearance_R": item["clearance_R"],
        },
    )
    return path


def main():
    ge = load_final_ge_coefficients()
    print(f"Final adjoint GE coefficients: A={ge[0]:.6f}, p={ge[1]:.6f}")
    replay = build_general_replay(ge)
    replay_path = "embedded vertical_tracking_v1 replay"
    training, baseline_cache = build_training_rows(replay)
    model = GeneralRewardModel(training)
    target_condition = condition_key(TARGET_VELOCITY, TARGET_HEIGHT_R)
    if target_condition not in CONDITION_BASELINES:
        raise KeyError(f"No MB anchor configured for target {target_condition}")
    pid_case = CONDITION_PID_BASELINES[target_condition]
    lookup = row_lookup(replay)
    pid_row = lookup[pid_case]

    if not MB_POLICY_FILE.exists():
        raise FileNotFoundError(f"Missing target MB policy: {MB_POLICY_FILE}")
    with np.load(MB_POLICY_FILE, allow_pickle=False) as data:
        saved_v = float(data["horizontal_velocity"])
        saved_h = float(data["height_in_rotor_radii"])
        x_policy = np.asarray(data["x_policy"], dtype=float)
        mb_policy = np.asarray(data["delta_z_reference"], dtype=float)
        history = np.asarray(data["cost_history"], dtype=float)
    if not (np.isclose(saved_v, TARGET_VELOCITY)
            and np.isclose(saved_h, TARGET_HEIGHT_R)):
        raise ValueError(
            f"Saved MB policy is for vx={saved_v:g}, h/R={saved_h:g}; "
            f"target is vx={TARGET_VELOCITY:g}, h/R={TARGET_HEIGHT_R:g}."
        )
    scales = local_mb_scales(mb_policy, x_policy)

    failed_policy = load_profile("EI_TR_V050_Z10", x_policy)
    failed_beta, _, failed_fit = relative_coordinates(
        failed_policy, mb_policy, x_policy, scales
    )
    proposals, lower, upper = candidate_betas(training, failed_beta)

    output = HISTORY_DIR / f"general_rt_{datetime.now():%Y%m%d_%H%M%S}"
    output.mkdir(parents=True, exist_ok=False)
    if SHOW_PRE_EI_OVERVIEW:
        plot_pre_ei_overview(
            model, training, proposals, x_policy, mb_policy, scales,
            failed_policy, output / "pre_EI_reward_and_candidates.pdf",
        )

    config, environment, initial = build_environment(
        HORIZONTAL_VELOCITY=TARGET_VELOCITY,
        HEIGHT_IN_ROTOR_RADII=TARGET_HEIGHT_R,
        use_spatial_trajectory=True,
    )
    baseline_data = run_pid(config, environment.trajectory, initial, ge)
    nominal_reference = np.asarray(baseline_data["reference"])[:, 2]
    incumbent = max(
        row["score_EXP"] for row in training
        if row["condition"] == target_condition
    )
    candidates = []
    basis = basis_matrix(x_policy)
    for index, beta in enumerate(proposals, start=1):
        alpha = scales * beta
        policy = mb_policy + ROTOR_RADIUS * basis @ alpha
        policy[0] = policy[-1] = 0.0
        if np.max(np.abs(policy)) > 4.55 * ROTOR_RADIUS:
            print(
                f"candidate {index:03d}/{len(proposals)}: rejected, "
                "reference correction outside executable bounds",
                flush=True,
            )
            continue
        data = run_reference_governor(
            config, environment.trajectory, initial, x_policy, policy, ge
        )
        clearance = minimum_actual_rotor_clearance(config, data)
        if clearance < MIN_ACTUAL_ROTOR_CLEARANCE - 1.0e-5:
            print(
                f"candidate {index:03d}/{len(proposals)}: rejected, "
                f"clearance={clearance / ROTOR_RADIUS:.2f}R",
                flush=True,
            )
            continue
        state = np.asarray(data["state"])
        reward_dt = float(vertical_reward(
            state[:, 0], state[:, 2] - nominal_reference
        ))
        score_dt = 1.0 - reward_dt / float(pid_row["reward_DT_current"])
        mean, std = model.predict(
            score_dt, beta, 0.0, TARGET_VELOCITY, TARGET_HEIGHT_R
        )
        candidates.append({
            "index": index,
            "beta": np.asarray(beta),
            "alpha": np.asarray(alpha),
            "policy": np.asarray(policy),
            "data": data,
            "clearance_R": float(clearance / ROTOR_RADIUS),
            "reward_DT": float(reward_dt),
            "score_DT": float(score_dt),
            "mean": mean,
            "std": std,
            "ei": expected_improvement(mean, std, incumbent),
        })
        print(
            f"candidate {index:03d}/{len(proposals)}: "
            f"S_DT={score_dt:+.4f}, predicted S_EXP={mean:+.4f} "
            f"+/- {std:.4f}, EI={candidates[-1]['ei']:.3e}, "
            f"clearance={clearance / ROTOR_RADIUS:.2f}R",
            flush=True,
        )
    if not candidates:
        raise RuntimeError("No safe general-RT candidate was found")
    selected = select_distinct(candidates, lower, upper)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = [
        save_candidate(number, item, baseline_data, ge, x_policy, history)
        for number, item in enumerate(selected, start=1)
    ]

    with (output / "training_relative_coordinates.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow([
            "case_name", "vx_m_s", "height_R",
            "beta_1", "beta_2", "beta_3", "score_DT", "score_EXP",
            "score_EXP_noise", "projection_mse_R2",
        ])
        for row in training:
            writer.writerow([
                row["case_name"],
                row["vx_m_s"], row["height_R"], *row["beta"],
                row["score_DT"], row["score_EXP"], row["score_EXP_noise"],
                row["projection_mse_R2"],
            ])

    summary = {
        "target": {"vx_m_s": TARGET_VELOCITY, "height_R": TARGET_HEIGHT_R},
        "experiment_iteration": EXPERIMENT_ITERATION,
        "replay": str(replay_path),
        "reward_version": REWARD_VERSION,
        "gamma0": model.gamma0,
        "gamma1": model.gamma1,
        "incumbent_normalized_score_EXP": incumbent,
        "normalization": "S = 1 - J_policy / J_PID = 1 - R_policy / R_PID",
        "local_mb_scales": scales.tolist(),
        "failed_transfer_beta": failed_beta.tolist(),
        "failed_transfer_projection_mse_R2": failed_fit,
        "beta_bounds": {"lower": lower.tolist(), "upper": upper.tolist()},
        "selected": [{
            key: (value.tolist() if isinstance(value, np.ndarray) else value)
            for key, value in item.items()
            if key not in {"policy", "data"}
        } for item in selected],
    }
    (output / "general_rt_selection.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    fig, axes = plt.subplots(2, 1, figsize=(7.4, 7.0), constrained_layout=True)
    axes[0].plot(x_policy, mb_policy / ROTOR_RADIUS, color="#00B050",
                 linewidth=2.0, label="local MB")
    colors = ("#C00000", "#E36C0A", "#7030A0")
    for number, (item, color) in enumerate(zip(selected, colors), start=1):
        axes[0].plot(x_policy, item["policy"] / ROTOR_RADIUS,
                     color=color, linewidth=1.6,
                     label=f"general RT {number}")
    axes[0].set(xlabel=r"$x$ [m]", ylabel=r"$\Delta z^*/R$ [-]")
    axes[0].grid(alpha=0.2); axes[0].legend(frameon=False)

    condition_styles = {
        (0.35, 1.50): ("o", "#305B98"),
        (0.20, 2.50): ("s", "#00B050"),
        (0.50, 1.00): ("^", "black"),
    }
    for condition, (marker, color) in condition_styles.items():
        condition_rows = [row for row in training if row["condition"] == condition]
        if not condition_rows:
            continue
        axes[1].scatter(
            [row["score_DT"] for row in condition_rows],
            [row["score_EXP"] for row in condition_rows],
            marker=marker, color=color, edgecolor="white", linewidth=0.5,
            s=42, zorder=5,
            label=rf"EXP: $v_x={condition[0]:g}$, $h/R={condition[1]:g}$",
        )
    axes[1].scatter(
        [item["score_DT"] for item in candidates],
        [item["mean"] for item in candidates],
        c=[item["ei"] for item in candidates], s=10, cmap="viridis",
        alpha=0.45, label="safe candidates",
    )
    for number, item in enumerate(selected, start=1):
        axes[1].errorbar(
            item["score_DT"], item["mean"], yerr=item["std"],
            fmt="o", markersize=7, capsize=3, color=colors[number - 1],
            label=f"selected {number}",
        )
    axes[1].axhline(incumbent, color="0.35", linestyle="--", linewidth=1.0,
                    label="best measured local policy")
    axes[1].set(
        xlabel=r"PID-normalized DT score $S^{DT}$",
        ylabel=r"predicted PID-normalized score $S^{EXP}$",
    )
    axes[1].grid(alpha=0.2); axes[1].legend(frameon=False, ncol=2)
    fig.savefig(output / "general_RT_candidates.pdf", bbox_inches="tight")
    plt.show()

    print(f"\nGeneral RT gamma0={model.gamma0:.4f}, gamma1={model.gamma1:.4f}")
    print(f"Local failed-transfer beta: {failed_beta}")
    for number, (item, path) in enumerate(zip(selected, paths), start=1):
        print(
            f"selected {number}: beta={np.round(item['beta'], 3)}, "
            f"predicted S_EXP={item['mean']:.4f} +/- {item['std']:.4f}, "
            f"EI={item['ei']:.4e}, file={path.name}"
        )
    print(
        "Run run_next_experiment.py with MISSION_PHASE='rt_general' and "
        "TRAJECTORY_NUMBER=1, 2, 3."
    )


if __name__ == "__main__":
    main()
