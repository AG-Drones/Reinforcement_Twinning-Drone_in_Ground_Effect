"""Generate calibration policies or exact repeats for visual comparisons."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from jDT.main import build_environment
from jDT.params import ROTOR_RADIUS
from .model_based_policy import (
    CLEARANCE_VALIDATION_TOLERANCE,
    MIN_ACTUAL_ROTOR_CLEARANCE,
    MPC_ITERATIONS,
    build_spatial_grid,
    minimum_actual_rotor_clearance,
    optimize_reference_governor,
    policy_metrics,
    run_reference_governor,
    run_pid,
    save_policy,
)
from .expected_improvement_policy import (
    BASIS_CENTERS,
    BASIS_WIDTHS_M,
    basis_matrix,
    policy_coordinates,
)


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "mission_output"
IDENTIFICATION_FILE = (
    ROOT / "identification_output" / "Warm_start" / "E12"
    / "adjoint_results.npz"
)

# USER SETTINGS
# ``video_repeats`` packages exact references from previous experiments without
# rerunning MB optimization. ``cross_condition`` retains the original workflow.
RUN_MODE = "video_repeats"  # video_repeats, cross_condition

# Targeted nominal-condition repeats for synchronized comparison videos.
VIDEO_HORIZONTAL_VELOCITY = 0.35
VIDEO_HEIGHT_IN_ROTOR_RADII = 1.50
VIDEO_CAMPAIGN_LABEL = "video_comparison"
VIDEO_PID_CASE = "BL"
VIDEO_MB_CASE = "MB"
VIDEO_RT_CASE = "EI_09"

# Cross-condition workflow retained from the previous implementation.
HORIZONTAL_VELOCITY = 0.50
HEIGHT_IN_ROTOR_RADII = 1.00
EXPERIMENT_ITERATION = 24
RT_SOURCE_CASE = "EI_09"  # best experimentally validated RT policy
MB_REFERENCE_CASE = "MB"
REGENERATE_RT_ONLY = False
SAVED_MB_POLICY_FILE = OUTPUT_DIR / "next_GE_mission_RG_rt_calibration_2.npz"

POLICY_LABELS = (
    "PID reference",
    "model-based optimum",
    f"RT transfer from {RT_SOURCE_CASE}",
)

VIDEO_POLICY_LABELS = (
    rf"PID repeat ({VIDEO_PID_CASE})",
    rf"MB optimum repeat ({VIDEO_MB_CASE})",
    rf"best RT repeat ({VIDEO_RT_CASE})",
)


def evaluate_policy(policy, alpha, config, trajectory, initial, x_policy,
                    ge_scenarios, label):
    """Evaluate a candidate against the nominal and robust GE scenarios."""
    scenario_data = [
        run_reference_governor(
            config, trajectory, initial, x_policy, policy, scenario
        )
        for scenario in ge_scenarios
    ]
    clearances = np.asarray([
        minimum_actual_rotor_clearance(config, result)
        for result in scenario_data
    ])
    if np.min(clearances) < MIN_ACTUAL_ROTOR_CLEARANCE - CLEARANCE_VALIDATION_TOLERANCE:
        print(f"{label} rejected: robust clearance", flush=True)
        return None
    costs = np.asarray([policy_metrics(result)[0] for result in scenario_data])
    item = {
        "alpha": np.asarray(alpha, dtype=float),
        "policy": np.asarray(policy, dtype=float),
        "data": scenario_data[0],
        "reward": -float(costs[0]),
        "robust_std": float(np.std(costs)),
        "clearance_R": float(np.min(clearances) / ROTOR_RADIUS),
    }
    print(
        f"{label}: alpha={item['alpha'].tolist()}, reward={item['reward']:.4f}, "
        f"clearance={item['clearance_R']:.2f}R",
        flush=True,
    )
    return item


def load_identified_ge() -> np.ndarray:
    if not IDENTIFICATION_FILE.exists():
        raise FileNotFoundError(f"Missing adjoint result: {IDENTIFICATION_FILE}")
    with np.load(IDENTIFICATION_FILE, allow_pickle=False) as data:
        ge = np.asarray(data["GE_coeffs"], dtype=float)
    if ge.shape != (2,) or not np.all(np.isfinite(ge)):
        raise ValueError("Expected finite GE coefficients [A, p]")
    return ge


def load_saved_mb_policy() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load and validate the MB policy produced by the first full run."""
    if not SAVED_MB_POLICY_FILE.exists():
        raise FileNotFoundError(
            f"Missing saved MB policy: {SAVED_MB_POLICY_FILE}. "
            "Set REGENERATE_RT_ONLY=False for the first full run."
        )
    with np.load(SAVED_MB_POLICY_FILE, allow_pickle=False) as data:
        x_policy = np.asarray(data["x_policy"], dtype=float)
        mb_policy = np.asarray(data["delta_z_reference"], dtype=float)
        ge = np.asarray(data["GE_coeffs"], dtype=float)
        velocity = float(data["horizontal_velocity"])
        height_r = float(data["height_in_rotor_radii"])
    if not np.isclose(velocity, HORIZONTAL_VELOCITY, atol=1.0e-9):
        raise ValueError(
            f"Saved MB velocity is {velocity:g} m/s; expected "
            f"{HORIZONTAL_VELOCITY:g} m/s."
        )
    if not np.isclose(height_r, HEIGHT_IN_ROTOR_RADII, atol=1.0e-9):
        raise ValueError(
            f"Saved MB height is {height_r:g}R; expected "
            f"{HEIGHT_IN_ROTOR_RADII:g}R."
        )
    if (x_policy.ndim != 1 or mb_policy.shape != x_policy.shape
            or np.any(np.diff(x_policy) <= 0.0)
            or not np.all(np.isfinite(mb_policy))):
        raise ValueError("Saved MB policy has an invalid spatial grid or profile")
    if ge.shape != (2,) or not np.all(np.isfinite(ge)):
        raise ValueError("Saved MB policy has invalid GE coefficients [A, p]")
    return x_policy, mb_policy, ge


def load_profile(case_name: str, x_policy: np.ndarray) -> np.ndarray:
    profile_path = (
        ROOT / "EXP" / "CLEAN"
        / f"EXP_{case_name}_RG_input.txt"
    )
    if not profile_path.exists():
        raise FileNotFoundError(f"Missing reference profile: {profile_path}")
    profile = np.loadtxt(profile_path, skiprows=1)
    if profile.ndim == 1:
        profile = profile[None, :]
    policy = np.interp(x_policy, profile[:, 0], profile[:, 1])
    policy[0] = policy[-1] = 0.0
    return policy


def load_clean_case(case: str, x_policy: np.ndarray) -> tuple[np.ndarray, dict]:
    """Load one exact CLEAN reference and validate its operating condition."""
    clean_dir = ROOT / "EXP" / "CLEAN"
    profile_path = clean_dir / f"EXP_{case}_RG_input.txt"
    metadata_path = clean_dir / f"EXP_{case}_metadata.json"
    if not profile_path.exists():
        raise FileNotFoundError(f"Missing reference profile: {profile_path}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing experiment metadata: {metadata_path}")

    import json

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    velocity = float(metadata["horizontal_velocity"])
    height_r = float(metadata["height_in_rotor_radii"])
    if not np.isclose(velocity, VIDEO_HORIZONTAL_VELOCITY, atol=1.0e-9):
        raise ValueError(
            f"{case} velocity is {velocity:g} m/s; expected "
            f"{VIDEO_HORIZONTAL_VELOCITY:g} m/s."
        )
    if not np.isclose(height_r, VIDEO_HEIGHT_IN_ROTOR_RADII, atol=1.0e-9):
        raise ValueError(
            f"{case} height is {height_r:g}R; expected "
            f"{VIDEO_HEIGHT_IN_ROTOR_RADII:g}R."
        )

    profile = np.loadtxt(profile_path, skiprows=1)
    if profile.ndim == 1:
        profile = profile[None, :]
    if (profile.shape[1] < 2 or np.any(np.diff(profile[:, 0]) <= 0.0)
            or not np.all(np.isfinite(profile[:, :2]))):
        raise ValueError(f"Invalid reference profile: {profile_path}")
    policy = np.interp(x_policy, profile[:, 0], profile[:, 1])
    policy[0] = policy[-1] = 0.0
    return policy, metadata


def load_source_rt_alpha() -> tuple[np.ndarray, float]:
    profile_path = (
        ROOT / "EXP" / "CLEAN"
        / f"EXP_{RT_SOURCE_CASE}_RG_input.txt"
    )
    profile = np.loadtxt(profile_path, skiprows=1)
    if profile.ndim == 1:
        profile = profile[None, :]
    alpha, projection_mse = policy_coordinates(profile[:, 0], profile[:, 1])
    return np.asarray(alpha, dtype=float), float(projection_mse)


def relative_mb_scales(old_mb: np.ndarray, new_mb: np.ndarray,
                       x_policy: np.ndarray) -> np.ndarray:
    """Scale each RT correction by the local amplitude proposed by MB."""
    basis = basis_matrix(x_policy)
    old_r = np.asarray(old_mb, dtype=float) / ROTOR_RADIUS
    new_r = np.asarray(new_mb, dtype=float) / ROTOR_RADIUS
    weight_sum = np.maximum(np.sum(basis, axis=0), 1.0e-12)
    old_local_rms = np.sqrt(np.sum(basis * old_r[:, None] ** 2, axis=0) / weight_sum)
    new_local_rms = np.sqrt(np.sum(basis * new_r[:, None] ** 2, axis=0) / weight_sum)
    if np.any(old_local_rms < 1.0e-6):
        raise RuntimeError("Old MB policy is too small to define a relative RT correction")
    return new_local_rms / old_local_rms


def save_campaign_policy(number, policy, item, pid, ge, x_policy,
                         alpha, role, history, projection_mse, source_alpha,
                         mb_scales):
    path = OUTPUT_DIR / f"next_GE_mission_RG_rt_calibration_{number}.npz"
    save_policy(
        path,
        HORIZONTAL_VELOCITY,
        HEIGHT_IN_ROTOR_RADII,
        ge,
        x_policy,
        policy,
        np.asarray(history, dtype=float),
        pid,
        item["data"],
        source="RT_Calibration",
        identification_iteration="E12",
        experiment_iteration=f"iteration_{EXPERIMENT_ITERATION:03d}",
        extra_npz={
            "cross_condition_role": np.asarray(role),
            "transferred_alpha_R": np.asarray(alpha),
            "source_rt_alpha_R": np.asarray(source_alpha),
            "relative_mb_scale": np.asarray(mb_scales),
            "rt_source_case": np.asarray(RT_SOURCE_CASE),
            "rt_source_projection_mse_R2": np.asarray(projection_mse),
            "rt_basis_centers_m": np.asarray(BASIS_CENTERS),
            "rt_basis_widths_m": np.asarray(BASIS_WIDTHS_M),
        },
        extra_metadata={
            "mission_phase": "rt",
            "mission_design": "cross_condition_validation",
            "trajectory_number": number,
            "cross_condition_role": role,
            "transferred_alpha_R": np.asarray(alpha).tolist(),
            "source_rt_alpha_R": np.asarray(source_alpha).tolist(),
            "relative_mb_scale": np.asarray(mb_scales).tolist(),
            "rt_source_case": RT_SOURCE_CASE,
            "rt_source_projection_mse_R2": projection_mse,
            "minimum_clearance_R": item["clearance_R"],
        },
    )


def generate_video_repeats() -> None:
    """Package exact PID, MB and best-RT references for repeated video runs."""
    ge = load_identified_ge()
    ge_scenarios = ge[None, :]
    config, environment, initial = build_environment(
        HORIZONTAL_VELOCITY=VIDEO_HORIZONTAL_VELOCITY,
        HEIGHT_IN_ROTOR_RADII=VIDEO_HEIGHT_IN_ROTOR_RADII,
        use_spatial_trajectory=True,
    )
    x_policy = build_spatial_grid()
    pid = run_pid(config, environment.trajectory, initial, ge)

    cases = (VIDEO_PID_CASE, VIDEO_MB_CASE, VIDEO_RT_CASE)
    roles = ("pid_repeat", "model_based_repeat", "best_rt_repeat")
    policies = []
    source_metadata = []
    for case in cases:
        policy, metadata = load_clean_case(case, x_policy)
        policies.append(policy)
        source_metadata.append(metadata)

    # The stored PID reference should be identically zero. Fail loudly if an
    # unrelated governed trajectory is selected by mistake.
    if not np.allclose(policies[0], 0.0, atol=1.0e-10, rtol=0.0):
        raise ValueError(
            f"{VIDEO_PID_CASE} is not a zero-correction PID reference."
        )

    items = []
    for number, (policy, role) in enumerate(zip(policies, roles), start=1):
        item = evaluate_policy(
            policy,
            np.zeros(3),
            config,
            environment.trajectory,
            initial,
            x_policy,
            ge_scenarios,
            f"{number}/3 {role}",
        )
        if item is None:
            raise RuntimeError(f"Video-repeat policy {number} failed the DT clearance check")
        items.append(item)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for number, (case, role, policy, item, metadata) in enumerate(
        zip(cases, roles, policies, items, source_metadata), start=1
    ):
        path = OUTPUT_DIR / f"next_GE_mission_RG_rt_calibration_{number}.npz"
        save_policy(
            path,
            VIDEO_HORIZONTAL_VELOCITY,
            VIDEO_HEIGHT_IN_ROTOR_RADII,
            ge,
            x_policy,
            policy,
            np.empty(0),
            pid,
            item["data"],
            source="RT_Calibration",
            identification_iteration="E12",
            experiment_iteration=VIDEO_CAMPAIGN_LABEL,
            extra_npz={
                "video_repeat_role": np.asarray(role),
                "source_experiment_case": np.asarray(case),
                "source_experiment_iteration": np.asarray(
                    metadata.get("experiment_iteration", "")
                ),
            },
            extra_metadata={
                "mission_phase": "rt",
                "mission_design": "video_repeat",
                "trajectory_number": number,
                "video_repeat_role": role,
                "source_experiment_case": case,
                "source_policy_file": metadata.get("policy_file"),
                "minimum_clearance_R": item["clearance_R"],
            },
        )

    figure, axis = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    colors = ("black", "#00B050", "#8B0000")
    styles = ("--", "-", "-")
    for policy, label, color, style in zip(
        policies, VIDEO_POLICY_LABELS, colors, styles
    ):
        axis.plot(
            x_policy,
            policy / ROTOR_RADIUS,
            color=color,
            linestyle=style,
            linewidth=2.0,
            label=label,
        )
    axis.set(
        xlabel=r"$x$ [m]",
        ylabel=r"$\Delta z^*/R$",
        title=(
            rf"video repeats: $v_x={VIDEO_HORIZONTAL_VELOCITY:.2f}$ m/s, "
            rf"$h/R={VIDEO_HEIGHT_IN_ROTOR_RADII:g}$"
        ),
    )
    axis.grid(alpha=0.2)
    axis.legend(frameon=False)
    plt.show()

    print(
        f"Saved PID, MB and best-RT video repeats from {VIDEO_PID_CASE}, "
        f"{VIDEO_MB_CASE} and {VIDEO_RT_CASE}."
    )
    print(
        "Use run_next_experiment.py with MISSION_PHASE='rt_calibration' and "
        "TRAJECTORY_NUMBER=1 (PID), 2 (MB), or 3 (best RT)."
    )


def main():
    if RUN_MODE == "video_repeats":
        generate_video_repeats()
        return
    if RUN_MODE != "cross_condition":
        raise ValueError("RUN_MODE must be 'video_repeats' or 'cross_condition'")
    if REGENERATE_RT_ONLY:
        regenerate_rt_only()
        return

    ge = load_identified_ge()
    ge_scenarios = ge[None, :]  # nominal DT for this transfer validation
    config, environment, initial = build_environment(
        HORIZONTAL_VELOCITY=HORIZONTAL_VELOCITY,
        HEIGHT_IN_ROTOR_RADII=HEIGHT_IN_ROTOR_RADII,
        use_spatial_trajectory=True,
    )
    x_policy = build_spatial_grid()
    zero_policy = np.zeros_like(x_policy)
    pid = run_pid(config, environment.trajectory, initial, ge)

    pid_item = evaluate_policy(
        zero_policy, np.zeros(3), config, environment.trajectory, initial,
        x_policy, ge_scenarios, "1/3 PID",
    )
    if pid_item is None:
        raise RuntimeError("PID mission failed the DT clearance check")

    mb_policy, mb_history, _, _, _ = optimize_reference_governor(
        config,
        environment.trajectory,
        initial,
        x_policy,
        ge_scenarios,
        iterations=MPC_ITERATIONS,
        progress_label=(
            f"2/3 MB vx={HORIZONTAL_VELOCITY:.2f}, "
            f"h={HEIGHT_IN_ROTOR_RADII:g}R"
        ),
    )
    mb_item = evaluate_policy(
        mb_policy, np.zeros(3), config, environment.trajectory, initial,
        x_policy, ge_scenarios, "2/3 model-based",
    )
    if mb_item is None:
        raise RuntimeError("Model-based mission failed the DT clearance check")

    source_alpha, projection_mse = load_source_rt_alpha()
    old_mb_policy = load_profile(MB_REFERENCE_CASE, x_policy)
    mb_scales = relative_mb_scales(old_mb_policy, mb_policy, x_policy)
    transferred_alpha = source_alpha * mb_scales
    rt_policy = (
        mb_policy
        + ROTOR_RADIUS * basis_matrix(x_policy) @ transferred_alpha
    )
    rt_policy[0] = rt_policy[-1] = 0.0
    rt_item = evaluate_policy(
        rt_policy, transferred_alpha, config, environment.trajectory, initial,
        x_policy, ge_scenarios, "3/3 transferred RT",
    )
    if rt_item is None:
        raise RuntimeError("Transferred RT mission failed the DT clearance check")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    policies = (zero_policy, mb_policy, rt_policy)
    items = (pid_item, mb_item, rt_item)
    alphas = (np.zeros(3), np.zeros(3), transferred_alpha)
    roles = ("pid", "model_based", "rt_transfer")
    histories = (np.empty(0), mb_history, np.empty(0))
    for number, values in enumerate(
        zip(policies, items, alphas, roles, histories), start=1
    ):
        policy, item, alpha, role, history = values
        save_campaign_policy(
            number, policy, item, pid, ge, x_policy, alpha, role,
            history, projection_mse, source_alpha, mb_scales,
        )

    figure, axis = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    colors = ("black", "#00B050", "#C00000")
    styles = ("--", "-", "-")
    for policy, label, color, style in zip(
        policies, POLICY_LABELS, colors, styles
    ):
        axis.plot(
            x_policy,
            policy / ROTOR_RADIUS,
            color=color,
            linestyle=style,
            linewidth=2.0,
            label=label,
        )
    axis.set(
        xlabel=r"$x$ [m]",
        ylabel=r"$\Delta z^*/R$",
        title=(
            rf"$v_x={HORIZONTAL_VELOCITY:.2f}$ m/s, "
            rf"$h/R={HEIGHT_IN_ROTOR_RADII:g}$"
        ),
    )
    axis.grid(alpha=0.2)
    axis.legend(frameon=False)
    plt.show()

    print(
        "Saved PID, MB and transferred-RT cross-condition policies."
    )
    print(f"Source RT alpha from {RT_SOURCE_CASE}: {source_alpha}")
    print(f"Local MB amplitude scales: {mb_scales}")
    print(f"Transferred relative alpha: {transferred_alpha}")
    print(
        "Use run_next_experiment.py with MISSION_PHASE='rt_calibration' and "
        "TRAJECTORY_NUMBER=1, 2 or 3."
    )


def regenerate_rt_only():
    """Reuse the saved MB optimum and overwrite only transferred RT policy #3."""
    x_policy, mb_policy, ge = load_saved_mb_policy()
    ge_scenarios = ge[None, :]
    config, environment, initial = build_environment(
        HORIZONTAL_VELOCITY=HORIZONTAL_VELOCITY,
        HEIGHT_IN_ROTOR_RADII=HEIGHT_IN_ROTOR_RADII,
        use_spatial_trajectory=True,
    )
    pid = run_pid(config, environment.trajectory, initial, ge)

    source_alpha, projection_mse = load_source_rt_alpha()
    old_mb_policy = load_profile(MB_REFERENCE_CASE, x_policy)
    mb_scales = relative_mb_scales(old_mb_policy, mb_policy, x_policy)
    transferred_alpha = source_alpha * mb_scales
    rt_policy = mb_policy + ROTOR_RADIUS * basis_matrix(x_policy) @ transferred_alpha
    rt_policy[0] = rt_policy[-1] = 0.0
    rt_item = evaluate_policy(
        rt_policy, transferred_alpha, config, environment.trajectory, initial,
        x_policy, ge_scenarios, "RT-only regeneration",
    )
    if rt_item is None:
        raise RuntimeError("Transferred RT mission failed the DT clearance check")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    save_campaign_policy(
        3, rt_policy, rt_item, pid, ge, x_policy, transferred_alpha,
        "rt_transfer", np.empty(0), projection_mse, source_alpha, mb_scales,
    )

    figure, axis = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    axis.plot(
        x_policy, mb_policy / ROTOR_RADIUS, color="#00B050", linewidth=2.0,
        label="saved model-based optimum",
    )
    axis.plot(
        x_policy, rt_policy / ROTOR_RADIUS, color="#C00000", linewidth=2.0,
        label=f"RT transfer from {RT_SOURCE_CASE}",
    )
    axis.set(
        xlabel=r"$x$ [m]",
        ylabel=r"$\Delta z^*/R$",
        title=(rf"$v_x={HORIZONTAL_VELOCITY:.2f}$ m/s, "
               rf"$h/R={HEIGHT_IN_ROTOR_RADII:g}$"),
    )
    axis.grid(alpha=0.2)
    axis.legend(frameon=False)
    plt.show()

    print(f"Loaded saved MB policy: {SAVED_MB_POLICY_FILE}")
    print(f"Source RT alpha from {RT_SOURCE_CASE}: {source_alpha}")
    print(f"Local MB amplitude scales: {mb_scales}")
    print(f"Transferred relative alpha: {transferred_alpha}")
    print(
        "Overwritten only the transferred-RT policy. "
        "Use run_next_experiment.py with MISSION_PHASE='rt_calibration' and "
        "TRAJECTORY_NUMBER=3."
    )


if __name__ == "__main__":
    main()
