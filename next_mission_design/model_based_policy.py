from __future__ import annotations

"""Model-based performance reference-governor generator.

The policy changes only z_ref(x).  The Crazyflie PID and the nominal horizontal
mission remain unchanged. The mission context and identified GE coefficients
are read from the final warm-start identification result.
"""

from pathlib import Path
import json
import os
import shutil

import jax
import jax.numpy as jnp
from jax import config as jax_config
import matplotlib.pyplot as plt
import numpy as np

from jDT.postprocessing import create_timestamped_directory
from jDT.controller import CrazyfliePIDController
from jDT.main import build_environment
from jDT.params import (
    FF_X_START, MAX_HORIZONTAL_VELOCITY, OBSTACLE_X_END, OBSTACLE_X_START,
    ROTOR_RADIUS, TABLE_HEIGHT_Z, X_ZOOM_END, X_ZOOM_START,
)
from jDT.simulator import SimulationEnvironment, quat_to_rot
from jDT.params import configure_jax_runtime

jax_config.update("jax_enable_x64", True)
configure_jax_runtime()

ROOT = Path(__file__).resolve().parent.parent
IDENTIFICATION_FILE = (
    ROOT / "identification_output" / "Warm_start" / "E12"
    / "adjoint_results.npz"
)
MISSION_FILE = ROOT / "mission_output" / "next_GE_mission_RG_performance.npz"
PLOT_FILE = ROOT / "mission_output" / "reference_governor_performance.pdf"
TEST_OUTPUT_DIR = ROOT / "test_ref_gov_performance"

# USER SETTINGS
HORIZONTAL_VELOCITY = 0.35
HEIGHT_IN_ROTOR_RADII = 1.5
GE_COEFFICIENT_SOURCE = "manual"  # historical first-identification model
# Historical adjoint result used to design the original It3 policy.
MANUAL_GE_COEFFICIENTS = (0.23041618552410736, 3.136230312560768)
MANUAL_IDENTIFICATION_LABEL = "iteration_003_manual_nominal_only"
# In manual mode the historical coefficients remain the nominal model, while
# robustness uses the same final uncertainty envelope used to design It6.
MANUAL_GE_COVARIANCE_FILE = IDENTIFICATION_FILE
MPC_ITERATIONS = 150
COMMAND_DX = 0.025
LEARNING_RATE = 1.0e-3
ROBUST_MB_POLICY = False
ROBUST_SIGMA_SCALE = 0.50
ROBUST_DISPERSION_WEIGHT = 0.50
ROBUST_MIN_MODEL_CLEARANCE_R = 0.50
ROBUST_MIN_F_GE = 0.05
PERFORMANCE_REWARD_VERSION = "simple_z_mse_obstacle_to_4m_v1"

# Vertical policy: conservative and smooth.
DELTA_Z_MIN = -3.0 * ROTOR_RADIUS
DELTA_Z_MAX = 3.0 * ROTOR_RADIUS
W_POLICY_AMPLITUDE = 0.10
W_POLICY_CURVATURE = 2.0
# Nonlinear state constraint: while the vehicle COM is longitudinally above
# the obstacle, even the lowest tilted rotor must retain this clearance.
MIN_ACTUAL_ROTOR_CLEARANCE = 0.50 * ROTOR_RADIUS
CLEARANCE_CONSTRAINT_WEIGHT = 1.0e5
CLEARANCE_VALIDATION_TOLERANCE = 1.0e-5
SHOW_PLOT = os.environ.get("GE_RG_BATCH_RUN") != "1"
# Compile one Adam step and reuse it by default.  Compiling the complete scan
# duplicates the long DT simulation across every MPC iteration, causing very
# long silent compilation and excessive memory use.  The full scan remains an
# explicit opt-in for numerical regression only.
USE_COMPILED_MPC_LOOP = os.environ.get("GE_RG_COMPILED_MPC_SCAN") == "1"


class SpatialVerticalReferenceGovernor(CrazyfliePIDController):
    def __init__(self, config, x_policy, delta_z_policy):
        super().__init__(config)
        self.x_policy = jnp.asarray(x_policy, dtype=jnp.float64)
        self.delta_z_policy = jnp.asarray(delta_z_policy, dtype=jnp.float64)

    def compute_control(self, state, ref, dt, controller_state, *, return_collective=False):
        delta_z = jnp.interp(
            state[0], self.x_policy, self.delta_z_policy, left=0.0, right=0.0
        )
        governed_ref = ref.at[2].add(delta_z)
        return super().compute_control(
            state, governed_ref, dt, controller_state,
            return_collective=return_collective,
        )


def build_spatial_grid():
    count = int(np.ceil((X_ZOOM_END - FF_X_START) / COMMAND_DX)) + 1
    return np.linspace(FF_X_START, X_ZOOM_END, count, dtype=float)


def performance_cost(x, z_error):
    """Mean squared vertical error from obstacle entrance to x=4 m."""
    x = jnp.asarray(x, dtype=jnp.float64)
    error_r = jnp.asarray(z_error, dtype=jnp.float64) / ROTOR_RADIUS
    scored = (
        (x >= OBSTACLE_X_START) & (x <= X_ZOOM_END)
    ).astype(jnp.float64)
    count = jnp.maximum(jnp.sum(scored), 1.0)
    mse = jnp.sum(scored * error_r**2) / count
    return mse, jnp.asarray([mse], dtype=jnp.float64)


def load_ge_coefficients(path=IDENTIFICATION_FILE):
    if GE_COEFFICIENT_SOURCE == "adjoint":
        if not Path(path).exists():
            raise FileNotFoundError(
                f"Adjoint output not found: {path}. Run adjoint_identification.py first."
            )
        with np.load(path, allow_pickle=False) as data:
            coefficients = np.asarray(data["GE_coeffs"], dtype=float)
    elif GE_COEFFICIENT_SOURCE == "manual":
        coefficients = np.asarray(MANUAL_GE_COEFFICIENTS, dtype=float)
    else:
        raise ValueError(
            "GE_COEFFICIENT_SOURCE must be 'adjoint' or 'manual'"
        )

    if coefficients.shape != (2,) or not np.all(np.isfinite(coefficients)):
        raise ValueError("GE coefficients must contain two finite values: (A, p)")
    if coefficients[1] < 0.0:
        raise ValueError("The exponent p must be non-negative")
    print(
        f"GE coefficients ({GE_COEFFICIENT_SOURCE}): "
        f"A={coefficients[0]:.6f}, p={coefficients[1]:.6f}"
    )
    return coefficients


def build_ge_scenarios(coefficients, path=IDENTIFICATION_FILE):
    """Nominal model and two ends of its dominant correlated uncertainty."""
    nominal = np.asarray(coefficients, dtype=float)
    if not ROBUST_MB_POLICY:
        print("Robust MB policy: nominal GE model only.")
        return nominal[None, :]
    covariance_path = (
        Path(path) if GE_COEFFICIENT_SOURCE == "adjoint"
        else MANUAL_GE_COVARIANCE_FILE
    )
    if not covariance_path.exists():
        print(
            f"Robust MB policy: covariance file unavailable: {covariance_path}; "
            "using nominal model."
        )
        return nominal[None, :]
    with np.load(covariance_path, allow_pickle=False) as data:
        if "GE_covariance" not in data:
            print("Robust MB policy: covariance unavailable; using nominal model.")
            return nominal[None, :]
        covariance = np.asarray(data["GE_covariance"], dtype=float)
        uncertainty_center = (
            np.asarray(data["GE_coeffs"], dtype=float)
            if GE_COEFFICIENT_SOURCE == "manual" and "GE_coeffs" in data
            else nominal
        )
    if covariance.shape != (2, 2) or not np.all(np.isfinite(covariance)):
        print("Robust MB policy: invalid covariance; using nominal model.")
        return nominal[None, :]
    values, vectors = np.linalg.eigh(0.5 * (covariance + covariance.T))
    index = int(np.argmax(values))
    shift = ROBUST_SIGMA_SCALE * np.sqrt(max(float(values[index]), 0.0)) * vectors[:, index]
    # Manual mode deliberately evaluates the historical nominal model together
    # with the final correlated uncertainty endpoints. This reproduces It6's
    # robust envelope without extrapolating It3's very large early covariance.
    scenarios = np.stack([
        nominal,
        uncertainty_center + shift,
        uncertainty_center - shift,
    ])
    scenarios[:, 1] = np.maximum(scenarios[:, 1], 0.0)
    for scenario in scenarios:
        maximum_gain = (1.0 / ROBUST_MIN_MODEL_CLEARANCE_R) ** scenario[1]
        scenario[0] = max(scenario[0], (ROBUST_MIN_F_GE - 1.0) / maximum_gain)
    print("Robust GE scenarios (nominal, correlated +/- uncertainty):")
    print(f"  covariance source: {covariance_path}")
    for index, (amplitude, exponent) in enumerate(scenarios):
        print(f"  scenario {index}: A={amplitude:.6f}, p={exponent:.6f}")
    return scenarios


def selected_context():
    return (float(HORIZONTAL_VELOCITY), float(HEIGHT_IN_ROTOR_RADII),
            "E12")


def next_experiment_iteration_label():
    exp_dir = ROOT / "EXP"
    clean_dir = ROOT / "EXP" / "CLEAN"
    numbers = []
    paths = list(clean_dir.glob("EXP_*_metadata.json"))
    paths.extend(exp_dir.glob("EXP_*_metadata.json"))
    for path in paths:
        metadata = json.loads(path.read_text(encoding="utf-8"))
        value = metadata.get("iteration", metadata.get("legacy_iteration"))
        if value is not None:
            numbers.append(int(value))
    return f"iteration_{max(numbers, default=-1) + 1:03d}"


def run_pid(config, trajectory, initial_state, ge_coefficients):
    environment = SimulationEnvironment(
        config, CrazyfliePIDController(config), trajectory,
        dt=config.DT, t_final=trajectory.T_total,
    )
    return environment.run(initial_state, jnp.asarray(ge_coefficients))


def run_reference_governor(
    config, trajectory, initial_state, x_policy, delta_z_policy, ge_coefficients
):
    controller = SpatialVerticalReferenceGovernor(config, x_policy, delta_z_policy)
    environment = SimulationEnvironment(
        config, controller, trajectory, dt=config.DT, t_final=trajectory.T_total,
    )
    return environment.run(initial_state, jnp.asarray(ge_coefficients))


def reference_governor_objective(
    delta_z_policy, config, trajectory, initial_state, x_policy, ge_scenarios
):
    normalized_policy = delta_z_policy / ROTOR_RADIUS
    amplitude = jnp.mean(normalized_policy**2)
    second_difference = jnp.diff(normalized_policy, n=2)
    curvature = jnp.mean(second_difference**2)
    arm_xy = 0.5 * config.MOTOR_DISTANCE
    rotor_body = jnp.asarray([
        [ arm_xy, -arm_xy, config.ROTOR_PLANE_Z_ABOVE_COM],
        [-arm_xy, -arm_xy, config.ROTOR_PLANE_Z_ABOVE_COM],
        [-arm_xy,  arm_xy, config.ROTOR_PLANE_Z_ABOVE_COM],
        [ arm_xy,  arm_xy, config.ROTOR_PLANE_Z_ABOVE_COM],
    ], dtype=jnp.float64)

    def lowest_rotor_z(sample):
        rotation = quat_to_rot(sample[6:10])
        return sample[2] + jnp.min((rotation @ rotor_body.T).T[:, 2])

    performance_costs, clearance_penalties = [], []
    for ge_coefficients in ge_scenarios:
        data = run_reference_governor(
            config, trajectory, initial_state, x_policy, delta_z_policy, ge_coefficients
        )
        state, reference = data["state"], data["reference"]
        scenario_cost, _ = performance_cost(
            state[:, 0], state[:, 2] - reference[:, 2]
        )
        lowest_rotor_z_history = jax.vmap(lowest_rotor_z)(state)
        actual_clearance = lowest_rotor_z_history - TABLE_HEIGHT_Z
        above_obstacle = (
            (state[:, 0] >= OBSTACLE_X_START)
            & (state[:, 0] <= OBSTACLE_X_END)
        ).astype(jnp.float64)
        violation = jax.nn.relu(
            (MIN_ACTUAL_ROTOR_CLEARANCE - actual_clearance) / ROTOR_RADIUS
        )
        clearance_penalties.append(
            jnp.sum(above_obstacle * violation**2)
            / jnp.maximum(jnp.sum(above_obstacle), 1.0)
        )
        performance_costs.append(scenario_cost)
    performance_costs = jnp.stack(performance_costs)
    mean_performance = jnp.mean(performance_costs)
    # A direct std has an undefined derivative at zero variance.  That occurs
    # systematically in manual mode, where only the nominal scenario exists,
    # and used to turn the first Adam update into NaN.
    centered_costs = performance_costs - mean_performance
    performance_dispersion = jnp.sqrt(jnp.mean(centered_costs**2) + 1.0e-12)
    worst_clearance_penalty = jnp.max(jnp.stack(clearance_penalties))
    total = (
        mean_performance
        + ROBUST_DISPERSION_WEIGHT * performance_dispersion
        + W_POLICY_AMPLITUDE * amplitude
        + W_POLICY_CURVATURE * curvature
        + CLEARANCE_CONSTRAINT_WEIGHT * worst_clearance_penalty
    )
    return total, jnp.asarray([
        mean_performance, performance_dispersion, amplitude, curvature,
        worst_clearance_penalty,
    ])


def optimize_reference_governor(
    config,
    trajectory,
    initial_state,
    x_policy,
    ge_scenarios,
    *,
    iterations=MPC_ITERATIONS,
    progress_label="reference governor",
):
    x_policy_jax = jnp.asarray(x_policy, dtype=jnp.float64)
    ge_jax = jnp.asarray(ge_scenarios, dtype=jnp.float64)
    policy = jnp.zeros(x_policy_jax.shape, dtype=jnp.float64)

    value_and_grad = jax.value_and_grad(
        lambda p, ge: reference_governor_objective(
            p, config, trajectory, initial_state, x_policy_jax, ge
        ),
        has_aux=True,
    )
    first = jnp.zeros_like(policy)
    second = jnp.zeros_like(policy)
    beta1, beta2, epsilon = 0.9, 0.999, 1.0e-8

    def adam_step(carry, iteration):
        current_policy, current_first, current_second, current_ge = carry
        (cost, components), gradient = value_and_grad(current_policy, current_ge)
        gradient = jnp.where(jnp.isfinite(gradient), gradient, 0.0)
        current_first = beta1 * current_first + (1.0 - beta1) * gradient
        current_second = beta2 * current_second + (1.0 - beta2) * gradient**2
        first_hat = current_first / (1.0 - beta1**iteration)
        second_hat = current_second / (1.0 - beta2**iteration)
        current_policy = current_policy - (
            LEARNING_RATE * first_hat / (jnp.sqrt(second_hat) + epsilon)
        )
        current_policy = jnp.clip(current_policy, DELTA_Z_MIN, DELTA_Z_MAX)
        current_policy = current_policy.at[0].set(0.0).at[-1].set(0.0)
        return (current_policy, current_first, current_second, current_ge), (
            cost, components, jnp.min(current_policy), jnp.max(current_policy)
        )

    iteration_numbers = jnp.arange(1, int(iterations) + 1)
    if USE_COMPILED_MPC_LOOP:
        run_adam = jax.jit(
            lambda initial_carry: jax.lax.scan(
                adam_step, initial_carry, iteration_numbers
            )
        )
        (policy, first, second, _), optimizer_output = run_adam(
            (policy, first, second, ge_jax)
        )
    else:
        outputs = []
        carry = (policy, first, second, ge_jax)
        jitted_step = jax.jit(adam_step)
        for iteration in range(1, int(iterations) + 1):
            carry, output = jitted_step(carry, jnp.asarray(iteration))
            outputs.append(output)
            if (iteration == 1 or iteration == int(iterations)
                    or iteration % max(1, int(iterations) // 10) == 0):
                cost_now = float(jax.device_get(output[0]))
                minimum_now = float(jax.device_get(output[2])) / ROTOR_RADIUS
                maximum_now = float(jax.device_get(output[3])) / ROTOR_RADIUS
                print(
                    f"{progress_label}: {iteration}/{iterations}, "
                    f"cost={cost_now:.6e}, dz=[{minimum_now:.2f}, "
                    f"{maximum_now:.2f}] R",
                    flush=True,
                )
        policy, first, second, _ = carry
        optimizer_output = tuple(jnp.stack(items) for items in zip(*outputs))

    costs, _components, policy_minima, policy_maxima = optimizer_output
    history = np.asarray(jax.device_get(costs), dtype=float)
    minima = np.asarray(jax.device_get(policy_minima), dtype=float)
    maxima = np.asarray(jax.device_get(policy_maxima), dtype=float)
    report_iterations = {1, int(iterations)}
    report_iterations.update(
        range(max(1, int(iterations) // 5), int(iterations) + 1,
              max(1, int(iterations) // 5))
    )
    if USE_COMPILED_MPC_LOOP:
        for iteration in sorted(report_iterations):
            index = iteration - 1
            print(
                f"{progress_label}: {iteration}/{iterations}, cost={history[index]:.6e}, "
                f"dz=[{minima[index]/ROTOR_RADIUS:.2f}, "
                f"{maxima[index]/ROTOR_RADIUS:.2f}] R"
            )

    policy_np = np.asarray(jax.device_get(policy), dtype=float)
    scenario_results = [
        run_reference_governor(config, trajectory, initial_state, x_policy_jax, policy, scenario)
        for scenario in ge_jax
    ]
    optimized = scenario_results[0]
    clearances = np.asarray([
        minimum_actual_rotor_clearance(config, result) for result in scenario_results
    ])
    performance_costs = np.asarray([policy_metrics(result)[0] for result in scenario_results])
    if np.min(clearances) < MIN_ACTUAL_ROTOR_CLEARANCE - CLEARANCE_VALIDATION_TOLERANCE:
        raise RuntimeError(
            "Optimized policy violates the robust DT rotor-clearance constraint: "
            f"minimum={np.min(clearances) / ROTOR_RADIUS:.3f}R, "
            f"required={MIN_ACTUAL_ROTOR_CLEARANCE / ROTOR_RADIUS:.3f}R."
        )
    print(f"Robust validation costs: {np.array2string(performance_costs, precision=4)}")
    print(f"Robust clearances/R: {np.array2string(clearances / ROTOR_RADIUS, precision=3)}")
    return policy_np, history, optimized, performance_costs, clearances


def minimum_actual_rotor_clearance(config, data):
    """Minimum lowest-rotor clearance while the DT is above the obstacle."""
    state = np.asarray(jax.device_get(data["state"]), dtype=float)
    arm_xy = 0.5 * config.MOTOR_DISTANCE
    rotor_body = np.asarray([
        [ arm_xy, -arm_xy, config.ROTOR_PLANE_Z_ABOVE_COM],
        [-arm_xy, -arm_xy, config.ROTOR_PLANE_Z_ABOVE_COM],
        [-arm_xy,  arm_xy, config.ROTOR_PLANE_Z_ABOVE_COM],
        [ arm_xy,  arm_xy, config.ROTOR_PLANE_Z_ABOVE_COM],
    ])
    mask = (state[:, 0] >= OBSTACLE_X_START) & (state[:, 0] <= OBSTACLE_X_END)
    if not np.any(mask):
        raise RuntimeError("DT trajectory has no samples above the obstacle")
    values = []
    for sample in state[mask]:
        rotation = np.asarray(jax.device_get(quat_to_rot(jnp.asarray(sample[6:10]))))
        values.append(sample[2] + np.min((rotation @ rotor_body.T).T[:, 2]) - TABLE_HEIGHT_Z)
    return float(np.min(values))


def policy_metrics(data):
    state = np.asarray(jax.device_get(data["state"]), dtype=float)
    reference = np.asarray(jax.device_get(data["reference"]), dtype=float)
    total, components = performance_cost(
        state[:, 0], state[:, 2] - reference[:, 2]
    )
    return float(total), np.asarray(components, dtype=float)


def save_policy(
    path, velocity, height_r, ge_coefficients, x_policy, delta_z_policy,
    cost_history, baseline, optimized, source, identification_iteration="latest",
    experiment_iteration="iteration_000",
    extra_npz=None, extra_metadata=None,
):
    path.parent.mkdir(parents=True, exist_ok=True)
    base_cost, base_components = policy_metrics(baseline)
    opt_cost, opt_components = policy_metrics(optimized)
    config, _, _ = build_environment(
        HORIZONTAL_VELOCITY=velocity,
        HEIGHT_IN_ROTOR_RADII=height_r,
        use_spatial_trajectory=True,
    )
    minimum_clearance = minimum_actual_rotor_clearance(config, optimized)
    npz_payload = dict(
        x_policy=np.asarray(x_policy),
        delta_z_reference=np.asarray(delta_z_policy),
        horizontal_velocity=np.asarray(velocity),
        height_in_rotor_radii=np.asarray(height_r),
        GE_coeffs=np.asarray(ge_coefficients),
        GE_coefficient_source=np.asarray(GE_COEFFICIENT_SOURCE),
        cost_history=np.asarray(cost_history),
        baseline_performance_cost=np.asarray(base_cost),
        governed_performance_cost=np.asarray(opt_cost),
        baseline_reward=np.asarray(-base_cost),
        predicted_DT_reward=np.asarray(-opt_cost),
        minimum_actual_rotor_clearance_m=np.asarray(minimum_clearance),
        reward_version=np.asarray(PERFORMANCE_REWARD_VERSION),
        identification_iteration=np.asarray(identification_iteration),
        experiment_iteration=np.asarray(experiment_iteration),
        mission_type=np.asarray("GE_VERTICAL_REFERENCE_GOVERNOR"),
        trajectory_execution=np.asarray("spatial"),
        policy_source=np.asarray(source),
    )
    if extra_npz:
        npz_payload.update(extra_npz)
    np.savez(path, **npz_payload)
    metadata = {
        "mission_type": "GE_VERTICAL_REFERENCE_GOVERNOR",
        "policy_file": path.name,
        "policy_source": source,
        "horizontal_velocity": velocity,
        "height_in_rotor_radii": height_r,
        "identification_iteration": identification_iteration,
        "experiment_iteration": experiment_iteration,
        "GE_coeffs": np.asarray(ge_coefficients).tolist(),
        "GE_coefficient_source": GE_COEFFICIENT_SOURCE,
        "governed_quantity": "z reference only",
        "horizontal_reference_modified": False,
        "x_policy_start_m": float(x_policy[0]),
        "x_policy_end_m": float(x_policy[-1]),
        "delta_z_bounds_m": [float(DELTA_Z_MIN), float(DELTA_Z_MAX)],
        "minimum_actual_rotor_clearance_m": minimum_clearance,
        "minimum_actual_rotor_clearance_R": minimum_clearance / ROTOR_RADIUS,
        "required_actual_rotor_clearance_R": MIN_ACTUAL_ROTOR_CLEARANCE / ROTOR_RADIUS,
        "clearance_definition": "lowest tilted rotor while COM x is above obstacle",
        "clearance_constraint_weight": CLEARANCE_CONSTRAINT_WEIGHT,
        "first_policy_node_zero": True,
        "last_policy_node_zero": True,
        "iterations": int(len(cost_history)),
        "reward": {
            "version": PERFORMANCE_REWARD_VERSION,
            "definition": "negative mean squared normalized z tracking error",
            "obstacle_start_m": float(OBSTACLE_X_START),
            "scored_end_m": float(X_ZOOM_END),
            "rotor_radius_m": float(ROTOR_RADIUS),
        },
        "baseline_performance_cost": base_cost,
        "governed_performance_cost": opt_cost,
        "baseline_components": base_components.tolist(),
        "governed_components": opt_components.tolist(),
    }
    if extra_metadata:
        metadata.update(extra_metadata)
    path.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def plot_comparison(baseline, optimized, x_policy, delta_z_policy, output_path):
    state_b = np.asarray(jax.device_get(baseline["state"]))
    state_g = np.asarray(jax.device_get(optimized["state"]))
    ref = np.asarray(jax.device_get(optimized["reference"]))
    fig, axes = plt.subplots(2, 1, figsize=(5.2, 5.0), sharex=True)
    for ax in axes:
        ax.axvspan(OBSTACLE_X_START, OBSTACLE_X_END, color="0.92", zorder=0)
        ax.axvline(OBSTACLE_X_START, color="0.45", ls="--", lw=0.8)
        ax.axvline(OBSTACLE_X_END, color="0.45", ls="--", lw=0.8)
        ax.grid(True, alpha=0.15)
    axes[0].plot(state_b[:, 0], (state_b[:, 2]-ref[:, 2])/ROTOR_RADIUS, "r--", label="DT PID")
    axes[0].plot(state_g[:, 0], (state_g[:, 2]-ref[:, 2])/ROTOR_RADIUS, "k-", label="DT reference governor")
    axes[0].set_ylabel(r"$(z-z^*)/R$ [-]")
    axes[0].set_ylim(-2, 2)
    axes[0].legend(frameon=False)
    axes[1].plot(x_policy, delta_z_policy/ROTOR_RADIUS, color="tab:green")
    axes[1].set_ylabel(r"$\Delta z^*_{gov}/R$ [-]")
    axes[1].set_xlabel(r"$x$ [m]")
    axes[1].set_xlim(X_ZOOM_START, X_ZOOM_END)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    if SHOW_PLOT:
        plt.show()
    else:
        plt.close(fig)


def main():
    velocity, height_r, identification_iteration = selected_context()
    if GE_COEFFICIENT_SOURCE == "manual":
        identification_iteration = MANUAL_IDENTIFICATION_LABEL
    if not 0.0 < velocity <= MAX_HORIZONTAL_VELOCITY:
        raise ValueError(f"Velocity {velocity} outside supported domain")
    ge = load_ge_coefficients()
    ge_scenarios = build_ge_scenarios(ge)
    config, environment, initial_state = build_environment(
        HORIZONTAL_VELOCITY=velocity,
        HEIGHT_IN_ROTOR_RADII=height_r,
        use_spatial_trajectory=True,
    )
    x_policy = build_spatial_grid()
    baseline = run_pid(config, environment.trajectory, initial_state, ge)
    policy, history, optimized, scenario_costs, scenario_clearances = optimize_reference_governor(
        config, environment.trajectory, initial_state, x_policy, ge_scenarios,
        iterations=MPC_ITERATIONS,
        progress_label=f"RG vx={velocity:.2f}, h={height_r:g}R",
    )
    save_policy(
        MISSION_FILE, velocity, height_r, ge, x_policy, policy, history,
        baseline, optimized, source="model_based_policy",
        identification_iteration=identification_iteration,
        experiment_iteration=next_experiment_iteration_label(),
        extra_npz={
            "robust_GE_scenarios": np.asarray(ge_scenarios),
            "robust_scenario_performance_costs": scenario_costs,
            "robust_scenario_min_clearance_m": scenario_clearances,
            "robust_dispersion_weight": np.asarray(ROBUST_DISPERSION_WEIGHT),
            "robust_sigma_scale": np.asarray(ROBUST_SIGMA_SCALE),
            "robust_covariance_source": np.asarray(
                "not_used_nominal_only"
                if not ROBUST_MB_POLICY
                else str(MANUAL_GE_COVARIANCE_FILE)
                if GE_COEFFICIENT_SOURCE == "manual"
                else str(IDENTIFICATION_FILE)
            ),
        },
        extra_metadata={
            "robust_MB_policy": bool(ROBUST_MB_POLICY),
            "robust_GE_scenarios": np.asarray(ge_scenarios).tolist(),
            "robust_scenario_performance_costs": scenario_costs.tolist(),
            "robust_scenario_min_clearance_R": (scenario_clearances / ROTOR_RADIUS).tolist(),
            "robust_dispersion_weight": ROBUST_DISPERSION_WEIGHT,
            "robust_sigma_scale": ROBUST_SIGMA_SCALE,
            "robust_covariance_source": (
                "not_used_nominal_only"
                if not ROBUST_MB_POLICY
                else str(MANUAL_GE_COVARIANCE_FILE)
                if GE_COEFFICIENT_SOURCE == "manual"
                else str(IDENTIFICATION_FILE)
            ),
        },
    )
    archive = create_timestamped_directory(TEST_OUTPUT_DIR, "reference_governor")
    shutil.copy2(MISSION_FILE, archive / MISSION_FILE.name)
    shutil.copy2(MISSION_FILE.with_suffix(".json"), archive / MISSION_FILE.with_suffix(".json").name)
    plot_comparison(
        baseline, optimized, x_policy, policy,
        PLOT_FILE,
    )
    shutil.copy2(PLOT_FILE, archive / PLOT_FILE.name)
    print(f"Final experimental RG policy: {MISSION_FILE}")
    print(f"Archived tester run: {archive}")


if __name__ == "__main__":
    main()
