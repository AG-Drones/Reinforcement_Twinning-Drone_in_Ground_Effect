from __future__ import annotations

"""Generate the next batch of informative vertical RG missions."""

from pathlib import Path
import json
import math
import os
import jax
import jax.numpy as jnp
from jax import config as jax_config
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import qmc

from jDT.controller import CrazyfliePIDController
from jDT.main import build_environment
from jDT.params import (OBSTACLE_X_END, OBSTACLE_X_START, ROTOR_RADIUS,
                        TABLE_HEIGHT_Z, X_ZOOM_END, X_ZOOM_START)
from jDT.simulator import SimulationEnvironment, quat_to_rot
from jDT.params import configure_jax_runtime

jax_config.update("jax_enable_x64", True)
configure_jax_runtime()

ROOT = Path(__file__).resolve().parent.parent
IDENTIFICATION_FILE = (
    ROOT / "identification_output" / "Warm_start" / "E12"
    / "adjoint_results.npz"
)
MISSION_FILE = ROOT / "mission_output" / "next_GE_mission_RG.npz"
PLOT_FILE = ROOT / "mission_output" / "reference_governor.pdf"

# USER SETTINGS
MPC_MODE = "information"
MPC_ITERATIONS = 300
LEARNING_RATE = 2.0e-2
NOMINAL_VELOCITY = 0.35
ROBUST_VELOCITIES = (0.35,)
NOMINAL_HEIGHT_R = 1.5
# "wide": previous 0.5R--6R design space, biased toward the wall.
# "near_wall": all reference knots vary continuously in 0.3R--1.5R.
REFERENCE_REGION_MODE = "near_wall"  # "wide" or "near_wall"
ROBUST_KAPPA = 0.5
INFORMATION_SCALE = 200.0
SHOW_PLOT = os.environ.get("GE_RG_BATCH_RUN") != "1"

KNOT_X = np.asarray([
    1.70,
    OBSTACLE_X_START - 0.10,
    2.30,
    0.5 * (OBSTACLE_X_START + OBSTACLE_X_END),
    2.90,
    OBSTACLE_X_END + 0.10,
    3.60,
    4.00,
])
N_KNOTS = len(KNOT_X)
# Reach the optimized entry height early, then hold it for one metre before
# the scientific-window entrance so that the vertical loop can settle.
ANCHOR_X = np.asarray([0.20, 0.70, *KNOT_X, 4.30])
if REFERENCE_REGION_MODE == "wide":
    MIN_ENDPOINT_R, MIN_INTERNAL_R, MAX_REFERENCE_R = 0.5, 0.5, 6.0
elif REFERENCE_REGION_MODE == "near_wall":
    MIN_ENDPOINT_R, MIN_INTERNAL_R, MAX_REFERENCE_R = 0.3, 0.3, 1.5
else:
    raise ValueError("REFERENCE_REGION_MODE must be 'wide' or 'near_wall'")
MIN_ACTUAL_CLEARANCE_R = 0.3
MIN_ACTUAL_ROTOR_CLEARANCE = MIN_ACTUAL_CLEARANCE_R * ROTOR_RADIUS
MAX_ABS_VZ_REF, MAX_ABS_AZ_REF = 0.5, 2.0
CONSTRAINT_WEIGHT = 1.0e5
N_INFORMATION_CANDIDATES = 64
N_INFORMATION_SAMPLES = 80
LIBRARY_SEED = 17
MIN_INFORMATION_FRACTION = 0.50
TOP_INFORMATION_FRACTION = 0.30
TOP_NOVELTY_FRACTION = 0.50
MIN_BATCH_NOVELTY = 0.30
N_PARAMETER_SAMPLES = 5
GE_NOVELTY_WEIGHT = 0.40
EXIT_NOVELTY_WEIGHT = 0.60
# Compatibility only for stale interactive namespaces; the current novelty
# metric uses z/R exclusively and never uses this scale.
NOVELTY_VZ_SCALE = 0.10
ADAPTIVE_LEVELS = ((0.30, 0.30), (0.40, 0.25), (0.50, 0.20),
                   (0.70, 0.15), (1.00, 0.00))
EXIT_X_END = OBSTACLE_X_END + 0.39
NOVELTY_X_START = OBSTACLE_X_END - 0.11
NOVELTY_X_END = OBSTACLE_X_END + 0.59


def load_experimental_response_library(evaluation_x):
    """Return measured h/R responses on a common x grid."""
    responses, labels = [], []
    clean_dir = ROOT / "EXP" / "CLEAN"
    for path in sorted(clean_dir.glob("EXP_*_clean.txt")):
        metadata_path = path.with_name(path.name.replace("_clean.txt", "_metadata.json"))
        if not metadata_path.exists():
            continue
        data = np.loadtxt(path, skiprows=1)
        if data.ndim == 1:
            data = data[None, :]
        x, clearance_r = data[:, 1], data[:, 2] / ROTOR_RADIUS
        responses.append(np.interp(evaluation_x, x, clearance_r))
        labels.append(path.stem.replace("_clean", ""))
    return np.asarray(responses), labels


def identification_iteration_label():
    return "E12"


def next_experiment_iteration_label():
    """Return the next experimental index, independently of adjoint reruns."""
    clean_dir = ROOT / "EXP" / "CLEAN"
    numbers = []
    for path in clean_dir.glob("EXP_*_metadata.json"):
        metadata = json.loads(path.read_text(encoding="utf-8"))
        value = metadata.get("iteration", metadata.get("legacy_iteration"))
        if value is not None:
            numbers.append(int(value))
    return f"iteration_{max(numbers, default=-1) + 1:03d}"


class SpatialVerticalReferenceGovernor(CrazyfliePIDController):
    def __init__(self, config, x_policy, delta_z_policy):
        super().__init__(config)
        self.x_policy, self.delta_z_policy = jnp.asarray(x_policy), jnp.asarray(delta_z_policy)

    def compute_control(self, state, ref, dt, controller_state, *, return_collective=False):
        dz = jnp.interp(state[0], self.x_policy, self.delta_z_policy, left=0.0, right=0.0)
        return super().compute_control(state, ref.at[2].add(dz), dt, controller_state,
                                       return_collective=return_collective)


def load_identification():
    with np.load(IDENTIFICATION_FILE, allow_pickle=False) as data:
        coeffs = np.asarray(data["GE_coeffs"], dtype=float)
        hessian = np.asarray(data["GE_hessian"], dtype=float)
    if coeffs.shape != (2,) or hessian.shape != (2, 2):
        raise ValueError("Run adjoint_identification.py with the static [A,p] model first.")
    hessian = 0.5 * (hessian + hessian.T)
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    hessian = eigenvectors @ np.diag(np.maximum(eigenvalues, 1.0e-8)) @ eigenvectors.T
    return coeffs, hessian


def parameter_ensemble(coeffs, covariance):
    """Deterministic sigma points for robust Fisher averaging."""
    values, vectors = np.linalg.eigh(0.5 * (covariance + covariance.T))
    directions = vectors @ np.diag(np.sqrt(np.maximum(values, 0.0)))
    samples = [np.asarray(coeffs, dtype=float)]
    for index in range(directions.shape[1]):
        samples.extend((coeffs + directions[:, index], coeffs - directions[:, index]))
    projected = []
    for sample in samples[:N_PARAMETER_SAMPLES]:
        A, p = float(sample[0]), float(np.clip(sample[1], 0.0, 6.0))
        minimum_A = (0.05 - 1.0) / (2.0**p)
        candidate = np.asarray([max(A, minimum_A), p])
        if not any(np.allclose(candidate, old) for old in projected):
            projected.append(candidate)
    return np.asarray(projected)


def dense_policy(knots_r, samples=181):
    x = jnp.linspace(ANCHOR_X[0], ANCHOR_X[-1], samples)
    values = jnp.concatenate((jnp.asarray([NOMINAL_HEIGHT_R, knots_r[0]]), knots_r,
                              jnp.asarray([NOMINAL_HEIGHT_R])))
    clearance_r = jnp.interp(x, jnp.asarray(ANCHOR_X), values)
    return x, (clearance_r - NOMINAL_HEIGHT_R) * ROTOR_RADIUS, clearance_r


def simulate(velocity, coeffs, x_policy, dz_policy):
    config, environment, initial_state = build_environment(
        HORIZONTAL_VELOCITY=float(velocity), HEIGHT_IN_ROTOR_RADII=NOMINAL_HEIGHT_R,
        use_spatial_trajectory=True)
    runner = SimulationEnvironment(
        config, SpatialVerticalReferenceGovernor(config, x_policy, dz_policy),
        environment.trajectory, dt=config.DT, t_final=environment.trajectory.T_total)
    return config, runner.run(initial_state, jnp.asarray(coeffs))


def lowest_rotor_clearance(config, state):
    arm = 0.5 * config.MOTOR_DISTANCE
    rotors = jnp.asarray([[arm, -arm, config.ROTOR_PLANE_Z_ABOVE_COM],
                          [-arm, -arm, config.ROTOR_PLANE_Z_ABOVE_COM],
                          [-arm, arm, config.ROTOR_PLANE_Z_ABOVE_COM],
                          [arm, arm, config.ROTOR_PLANE_Z_ABOVE_COM]])
    def one(sample):
        z = sample[2] + (quat_to_rot(sample[6:10]) @ rotors.T).T[:, 2]
        return jnp.min(z) - TABLE_HEIGHT_Z
    return jax.vmap(one)(state)


def information_gain(prior, clearance_r, coeffs):
    """Directional Bayesian D-optimality, independent of sensitivity magnitude."""
    u = 1.0 / jnp.maximum(clearance_r, MIN_INTERNAL_R)
    A, p = coeffs
    up = u**p
    basis = jnp.stack((up, A*up*jnp.log(jnp.maximum(u, 1.0e-12))), axis=1)
    eigenvalues, eigenvectors = jnp.linalg.eigh(prior)
    whitening = eigenvectors @ jnp.diag(
        1.0/jnp.sqrt(jnp.maximum(eigenvalues, 1.0e-8)))
    directions = basis @ whitening
    directions /= jnp.maximum(jnp.linalg.norm(directions, axis=1, keepdims=True), 1.0e-12)
    directional_fisher = (directions.T @ directions) / directions.shape[0]
    sign, score = jnp.linalg.slogdet(
        jnp.eye(2) + INFORMATION_SCALE*directional_fisher)
    return jnp.where(sign > 0, score, -1.0e6)


def fast_information_objective(knots_r, coeffs, prior):
    """D-optimal objective from the static GE basis; no DT differentiation."""
    x, dz, clearance_r = dense_policy(knots_r)
    scientific = (x >= X_ZOOM_START) & (x <= X_ZOOM_END)
    gain = information_gain(
        prior, jnp.where(scientific, clearance_r, MAX_REFERENCE_R), coeffs
    )
    dx = x[1]-x[0]
    velocity = NOMINAL_VELOCITY
    vz = velocity*jnp.diff(dz)/dx
    az = velocity**2*jnp.diff(dz, n=2)/dx**2
    violation = (jnp.mean(jax.nn.relu(jnp.abs(vz)-MAX_ABS_VZ_REF)**2)
                 + jnp.mean(jax.nn.relu(jnp.abs(az)-MAX_ABS_AZ_REF)**2)
                 + jnp.mean(jax.nn.relu(MIN_INTERNAL_R-clearance_r)**2)
                 + jnp.mean(jax.nn.relu(clearance_r-MAX_REFERENCE_R)**2))
    return -gain + CONSTRAINT_WEIGHT*violation, (gain, jnp.asarray(0.0))


def scenario_metrics(knots_r, velocity, coeffs, prior):
    x_policy, dz_policy, _ = dense_policy(knots_r)
    config, data = simulate(velocity, coeffs, x_policy, dz_policy)
    state, reference = data["state"], data["reference"]
    scientific = (state[:, 0] >= X_ZOOM_START) & (state[:, 0] <= X_ZOOM_END)
    obstacle = (state[:, 0] >= OBSTACLE_X_START) & (state[:, 0] <= OBSTACLE_X_END)
    actual_r = (
        state[:, 2] + config.ROTOR_PLANE_Z_ABOVE_COM - TABLE_HEIGHT_Z
    ) / ROTOR_RADIUS
    gain = information_gain(
        prior, jnp.where(scientific, actual_r, MAX_REFERENCE_R), coeffs
    )
    tracking = jnp.sum(scientific * ((state[:, 2] - reference[:, 2]) / ROTOR_RADIUS)**2)
    tracking /= jnp.maximum(jnp.sum(scientific), 1.0)
    rotor_r = lowest_rotor_clearance(config, state) / ROTOR_RADIUS
    safety = jnp.sum(obstacle * jax.nn.relu(MIN_ACTUAL_CLEARANCE_R - rotor_r)**2)
    safety /= jnp.maximum(jnp.sum(obstacle), 1.0)
    dx = x_policy[1] - x_policy[0]
    vz, az = velocity*jnp.diff(dz_policy)/dx, velocity**2*jnp.diff(dz_policy, n=2)/dx**2
    kinematics = (jnp.mean(jax.nn.relu(jnp.abs(vz)-MAX_ABS_VZ_REF)**2)
                  + jnp.mean(jax.nn.relu(jnp.abs(az)-MAX_ABS_AZ_REF)**2))
    monotonic = jnp.mean(jax.nn.relu(-jnp.diff(state[:, 0]))**2)
    complete = jax.nn.relu(X_ZOOM_END-jnp.max(state[:, 0]))**2
    pwm_fraction = data["pwm"] / config.PWM_MAX
    saturation = jnp.mean(jax.nn.relu(0.02-pwm_fraction)**2
                          + jax.nn.relu(pwm_fraction-0.98)**2)
    return gain, tracking, safety + kinematics + monotonic + complete + saturation


def objective(knots_r, coeffs, prior, mode):
    values = [scenario_metrics(knots_r, v, coeffs, prior) for v in ROBUST_VELOCITIES]
    gains, tracks, violations = (jnp.stack([x[i] for x in values]) for i in range(3))
    spread = jnp.std(gains) if len(ROBUST_VELOCITIES) > 1 else 0.0
    robust_gain = jnp.mean(gains) - ROBUST_KAPPA*spread
    core = -robust_gain if mode == "information" else jnp.mean(tracks)
    return core + CONSTRAINT_WEIGHT*jnp.mean(violations), (robust_gain, jnp.mean(tracks))


def optimize_policy(iterations=MPC_ITERATIONS, mode=MPC_MODE, initial_knots=None):
    coeffs, prior = load_identification()
    if initial_knots is None or not np.all(np.isfinite(initial_knots)):
        initial_knots = np.full(N_KNOTS, NOMINAL_HEIGHT_R)
    if mode == "information":
        vg = jax.jit(jax.value_and_grad(
            lambda nodes: fast_information_objective(nodes, coeffs, prior), has_aux=True))
        seeds = [
            np.asarray(initial_knots),
            np.asarray([1.0, 2.0, 4.0, 2.0, 1.0]),
            np.asarray([2.0, 1.0, 3.0, 5.0, 2.0]),
            np.asarray([1.0, 6.0, 2.0, 4.0, 1.0]),
        ]
    else:
        vg = jax.value_and_grad(
            lambda p: objective(p, coeffs, prior, mode), has_aux=True)
        seeds = [np.asarray(initial_knots)]
    lower = jnp.asarray([MIN_ENDPOINT_R, MIN_INTERNAL_R, MIN_INTERNAL_R,
                         MIN_INTERNAL_R, MIN_ENDPOINT_R])
    report_interval = max(1, int(iterations)//20)
    results = []
    for start, seed in enumerate(seeds, 1):
        knots = jnp.asarray(seed)
        m, v, history = jnp.zeros_like(knots), jnp.zeros_like(knots), []
        print(f"Starting MB optimization {start}/{len(seeds)}: "
              f"mode={mode}, iterations={iterations}", flush=True)
        for iteration in range(1, int(iterations)+1):
            (cost, diagnostics), grad = vg(knots)
            m, v = 0.9*m + 0.1*grad, 0.999*v + 0.001*grad**2
            knots -= LEARNING_RATE*(m/(1-0.9**iteration))/(jnp.sqrt(v/(1-0.999**iteration))+1e-8)
            knots = jnp.clip(knots, lower, MAX_REFERENCE_R)
            history.append([float(cost), float(diagnostics[0]), float(diagnostics[1])])
            if iteration == 1 or iteration % report_interval == 0 or iteration == int(iterations):
                nodes = ", ".join(f"{value:.2f}" for value in np.asarray(knots))
                print(f"start {start} | iteration {iteration:4d}/{iterations} | "
                      f"cost={float(cost):.4e} | D-opt={float(diagnostics[0]):.4f} | "
                      f"tracking={float(diagnostics[1]):.4e} | h/R=[{nodes}]", flush=True)
        results.append((float(history[-1][0]), np.asarray(knots), np.asarray(history)))
    _, best_knots, best_history = min(results, key=lambda item: item[0])
    print("Selected multi-start solution: h/R=["+
          ", ".join(f"{value:.2f}" for value in best_knots)+"]", flush=True)
    return best_knots, best_history, coeffs, prior


def screen_information_library():
    """Select GE, exit-dynamics, and discrepancy-novelty missions."""
    coeffs, prior = load_identification()
    with np.load(IDENTIFICATION_FILE, allow_pickle=False) as data:
        covariance = np.asarray(data["GE_covariance"], dtype=float)
        residual_variance = max(float(data["final_loss"]), 1.0e-8)
    parameter_scale = np.sqrt(np.maximum(np.diag(covariance), 1.0e-10))
    theta_samples = parameter_ensemble(coeffs, covariance)
    print(
        "Robust Fisher parameter ensemble: "
        + ", ".join(f"[A={row[0]:.3f}, p={row[1]:.3f}]" for row in theta_samples),
        flush=True,
    )

    x_policy = jnp.asarray(dense_policy(jnp.full(N_KNOTS, NOMINAL_HEIGHT_R))[0])
    evaluation_x = jnp.linspace(X_ZOOM_START, X_ZOOM_END, N_INFORMATION_SAMPLES)
    evaluation_x_np = np.asarray(evaluation_x)
    ge_mask = ((evaluation_x_np >= OBSTACLE_X_START)
               & (evaluation_x_np <= OBSTACLE_X_END))
    exit_mask = ((evaluation_x_np >= OBSTACLE_X_END)
                 & (evaluation_x_np <= EXIT_X_END))
    novelty_mask = ((evaluation_x_np >= NOVELTY_X_START)
                    & (evaluation_x_np <= NOVELTY_X_END))
    experimental_library, experimental_labels = load_experimental_response_library(
        evaluation_x_np)
    print(
        f"Novelty library: {len(experimental_labels)} measured trajectories "
        f"({', '.join(experimental_labels) or 'none'}).",
        flush=True,
    )
    config, environment, initial_state = build_environment(
        HORIZONTAL_VELOCITY=NOMINAL_VELOCITY,
        HEIGHT_IN_ROTOR_RADII=NOMINAL_HEIGHT_R,
        use_spatial_trajectory=True)

    def rollout(delta_z, ge):
        runner = SimulationEnvironment(
            config, SpatialVerticalReferenceGovernor(config, x_policy, delta_z),
            environment.trajectory, dt=config.DT,
            t_final=environment.trajectory.T_total)
        return runner.run(initial_state, ge)

    def sampled_observations(delta_z, ge):
        state = rollout(delta_z, ge)["state"]
        propeller_height_r = (
            state[:, 2] + config.ROTOR_PLANE_Z_ABOVE_COM - TABLE_HEIGHT_Z
        ) / ROTOR_RADIUS
        return jnp.interp(evaluation_x, state[:, 0], propeller_height_r)

    run_state = jax.jit(lambda delta_z, ge: rollout(delta_z, ge)["state"])
    sensitivity = jax.jit(jax.jacrev(sampled_observations, argnums=1))
    sensitivity_ensemble = jax.jit(
        jax.vmap(sensitivity, in_axes=(None, 0))
    )
    sobol = qmc.Sobol(d=N_KNOTS, scramble=True, seed=LIBRARY_SEED)
    unit_candidates = sobol.random_base2(int(np.log2(N_INFORMATION_CANDIDATES)))
    if REFERENCE_REGION_MODE == "wide":
        # Preserve the previous broad library: 60% below 2R, 25% in 2R--4R,
        # and 15% in 4R--6R.
        random_candidates = np.empty_like(unit_candidates)
        low = unit_candidates < 0.60
        medium = (unit_candidates >= 0.60) & (unit_candidates < 0.85)
        high = unit_candidates >= 0.85
        random_candidates[low] = 0.5 + unit_candidates[low] / 0.60 * 1.5
        random_candidates[medium] = 2.0 + (unit_candidates[medium] - 0.60) / 0.25 * 2.0
        random_candidates[high] = 4.0 + (unit_candidates[high] - 0.85) / 0.15 * 2.0
        structured_candidates = np.asarray([
            np.full(N_KNOTS, 1.5),
            [0.5, 0.5, 1.0, 2.0, 2.0, 1.0, 0.5, 0.5],
            [2.0, 2.0, 0.5, 3.0, 5.0, 4.0, 2.0, 2.0],
            [0.5, 0.5, 6.0, 3.0, 1.0, 4.0, 2.0, 0.5],
        ])
    else:
        random_candidates = 0.3 + 1.2 * unit_candidates
        structured_candidates = np.asarray([
            np.full(N_KNOTS, 1.5),
            [0.3, 0.3, 0.6, 1.2, 1.2, 0.6, 0.3, 0.3],
            [1.5, 1.5, 0.3, 0.9, 1.5, 1.2, 0.6, 0.6],
            [0.3, 0.3, 1.5, 0.9, 0.6, 1.2, 0.6, 0.3],
        ])
    candidates = np.vstack((
        structured_candidates,
        random_candidates,
    ))
    accepted, history = [], []
    print(
        f"Screening {len(candidates)} E-optimal candidate missions in "
        f"'{REFERENCE_REGION_MODE}' reference region "
        f"[{MIN_INTERNAL_R:.1f}R, {MAX_REFERENCE_R:.1f}R].",
        flush=True,
    )
    for number, knots in enumerate(candidates, 1):
        x, dz, clearance = dense_policy(jnp.asarray(knots))
        dx = float(x[1]-x[0])
        vz = NOMINAL_VELOCITY*np.diff(np.asarray(dz))/dx
        az = NOMINAL_VELOCITY**2*np.diff(np.asarray(dz), n=2)/dx**2
        if np.max(np.abs(vz)) > MAX_ABS_VZ_REF or np.max(np.abs(az)) > MAX_ABS_AZ_REF:
            continue
        state_jax = run_state(dz, jnp.asarray(coeffs))
        state = np.asarray(state_jax)
        if not np.all(np.isfinite(state)) or np.max(state[:, 0]) < X_ZOOM_END:
            continue
        obstacle = ((state[:, 0] >= OBSTACLE_X_START)
                    & (state[:, 0] <= OBSTACLE_X_END))
        rotor_clearance = np.asarray(lowest_rotor_clearance(config, state_jax))
        if (not np.any(obstacle)
                or np.min(rotor_clearance[obstacle]) < MIN_ACTUAL_ROTOR_CLEARANCE):
            continue
        sensitivities = (
            np.asarray(sensitivity_ensemble(dz, jnp.asarray(theta_samples)))
            * parameter_scale[None, None, :]
        )
        # Near-wall sigma-point rollouts can become numerically invalid for
        # extreme but still covariance-compatible (A, p) pairs. Such a
        # candidate has no meaningful robust Fisher score and must not enter
        # sorting, where NaN values would otherwise contaminate the batch.
        if not np.all(np.isfinite(sensitivities)):
            continue
        fisher_ge = np.mean([
            (S[ge_mask].T @ S[ge_mask])
            / (residual_variance * max(np.count_nonzero(ge_mask), 1))
            for S in sensitivities
        ], axis=0)
        fisher_exit = np.mean([
            (S[exit_mask].T @ S[exit_mask])
            / (residual_variance * max(np.count_nonzero(exit_mask), 1))
            for S in sensitivities
        ], axis=0)
        eig_ge = np.linalg.eigvalsh(0.5*(fisher_ge+fisher_ge.T))
        eig_exit = np.linalg.eigvalsh(0.5*(fisher_exit+fisher_exit.T))
        score_ge, score_exit = float(eig_ge[0]), float(eig_exit[0])
        if not np.all(np.isfinite([*eig_ge, *eig_exit, score_ge, score_exit])):
            continue
        actual_r = (state[:, 2]+config.ROTOR_PLANE_Z_ABOVE_COM-TABLE_HEIGHT_Z)/ROTOR_RADIUS
        response = np.interp(evaluation_x_np, state[:, 0], actual_r)
        if experimental_library.size:
            distances_ge = np.sqrt(np.mean(
                (experimental_library[:, ge_mask]
                 - response[None, ge_mask])**2, axis=1))
            distances_exit = np.sqrt(np.mean(
                (experimental_library[:, novelty_mask]
                 - response[None, novelty_mask])**2, axis=1))
            novelty_ge = float(np.min(distances_ge))
            novelty_exit = float(np.min(distances_exit))
            closest_historical = experimental_labels[int(np.argmin(
                GE_NOVELTY_WEIGHT*distances_ge
                + EXIT_NOVELTY_WEIGHT*distances_exit))]
        else:
            novelty_ge = novelty_exit = 0.0
            closest_historical = None
        novelty = GE_NOVELTY_WEIGHT*novelty_ge + EXIT_NOVELTY_WEIGHT*novelty_exit
        desired_r = np.interp(state[:, 0], np.asarray(x), np.asarray(clearance))
        mask = (state[:, 0] >= X_ZOOM_START) & (state[:, 0] <= X_ZOOM_END)
        tracking = float(np.mean((actual_r[mask]-desired_r[mask])**2))
        accepted.append(dict(
            ge_score=score_ge, exit_score=score_exit, novelty=novelty,
            novelty_ge=novelty_ge, novelty_exit=novelty_exit,
            closest_historical=closest_historical,
            knots=knots.copy(), tracking=tracking, ge_eigenvalues=eig_ge,
            exit_eigenvalues=eig_exit, fisher_ge=fisher_ge,
            fisher_exit=fisher_exit, number=number, response=response))
        history.append([-score_ge, score_ge, tracking, novelty, score_exit])
        if number == 1 or number % 8 == 0 or number == len(candidates):
            print(f"candidate {number:3d}/{len(candidates)} | safe={len(accepted):3d} | "
                  f"lambda_GE={score_ge:.3e} | lambda_exit={score_exit:.3e}",
                  flush=True)
    if not accepted:
        raise RuntimeError("No candidate in the E-optimal library passed the DT safety checks.")
    # Mission 1: from the top 30% by GE information, retain the newest 50%,
    # then select the most informative candidate in that novelty-qualified set.
    ge_ranked = sorted(accepted, key=lambda item: item["ge_score"], reverse=True)
    max_ge = ge_ranked[0]["ge_score"]
    ge_pool_count = max(1, math.ceil(TOP_INFORMATION_FRACTION*len(ge_ranked)))
    ge_pool = [item for item in ge_ranked[:ge_pool_count]
               if item["ge_score"] >= MIN_INFORMATION_FRACTION*max_ge]
    ge_pool = ge_pool or ge_ranked[:1]
    novelty_count = max(1, math.ceil(TOP_NOVELTY_FRACTION*len(ge_pool)))
    novelty_pool = sorted(
        ge_pool, key=lambda item: item["novelty_ge"], reverse=True
    )[:novelty_count]
    mission_ge = max(novelty_pool, key=lambda item: item["ge_score"])
    selected = [mission_ge]
    print(f"Batch mission 1 [GE]: candidate {mission_ge['number']}/{len(candidates)} | "
          f"lambda_GE={mission_ge['ge_score']:.4e} | "
          f"historical GE novelty={mission_ge['novelty_ge']:.3f}", flush=True)

    remaining = [item for item in accepted if item["number"] != mission_ge["number"]]
    # Mission 2: repeat the same two-stage gate using cumulative GE Fisher
    # information and novelty relative to both history and mission 1.
    complementary_ranked = []
    for item in remaining:
        joint_ge = float(np.linalg.eigvalsh(
            mission_ge["fisher_ge"] + item["fisher_ge"])[0])
        batch_ge = float(np.sqrt(np.mean(
            (item["response"][ge_mask] - mission_ge["response"][ge_mask])**2)))
        min_ge_novelty = min(item["novelty_ge"], batch_ge)
        complementary_ranked.append((joint_ge, min_ge_novelty, item))
    complementary_ranked.sort(key=lambda row: row[0], reverse=True)
    max_joint_ge = complementary_ranked[0][0]
    count = max(1, math.ceil(TOP_INFORMATION_FRACTION*len(complementary_ranked)))
    pool = [row for row in complementary_ranked[:count]
            if row[0] >= MIN_INFORMATION_FRACTION*max_joint_ge]
    pool = pool or complementary_ranked[:1]
    novelty_count = max(1, math.ceil(TOP_NOVELTY_FRACTION*len(pool)))
    novelty_pool = sorted(pool, key=lambda row: row[1], reverse=True)[:novelty_count]
    chosen_two = max(novelty_pool, key=lambda row: row[0])
    mission_exit = chosen_two[2]
    selected.append(mission_exit)
    print(f"Batch mission 2 [complementary GE]: candidate {mission_exit['number']}/{len(candidates)} | "
          f"joint lambda_GE={chosen_two[0]:.4e} | "
          f"minimum GE novelty={chosen_two[1]:.3f}", flush=True)

    remaining = [item for item in accepted
                 if item["number"] not in {x["number"] for x in selected}]
    base_ge = sum((item["fisher_ge"] for item in selected), np.zeros((2, 2)))
    base_exit = sum((item["fisher_exit"] for item in selected), np.zeros((2, 2)))
    novelty_ranked = []
    for item in remaining:
        joint_ge = float(np.linalg.eigvalsh(base_ge + item["fisher_ge"])[0])
        joint_exit = float(np.linalg.eigvalsh(base_exit + item["fisher_exit"])[0])
        distances = [item["novelty_exit"]] if experimental_library.size else []
        distances.extend(float(np.sqrt(np.mean(
            (item["response"][novelty_mask] - old["response"][novelty_mask])**2)))
                         for old in selected)
        novelty_ranked.append((joint_ge, joint_exit, min(distances), item))
    max_joint_ge = max(row[0] for row in novelty_ranked)
    max_joint_exit = max(row[1] for row in novelty_ranked)
    mission_novelty, novelty_gate = None, None
    for top_fraction, min_fraction in ADAPTIVE_LEVELS:
        eligible = [row for row in novelty_ranked
                    if row[0] >= min_fraction*max_joint_ge
                    and row[1] >= min_fraction*max_joint_exit]
        count = max(1, math.ceil(top_fraction*len(novelty_ranked)))
        eligible = sorted(
            eligible,
            key=lambda row: min(row[0]/max_joint_ge, row[1]/max_joint_exit),
            reverse=True)[:count]
        eligible = [row for row in eligible if row[2] >= MIN_BATCH_NOVELTY]
        if eligible:
            chosen = max(eligible, key=lambda row: (row[2], row[0], row[1]))
            mission_novelty, novelty_gate = chosen[3], (top_fraction, min_fraction)
            break
    if mission_novelty is None:
        chosen = max(novelty_ranked, key=lambda row: (row[2], row[0], row[1]))
        mission_novelty, novelty_gate = chosen[3], (1.0, 0.0)
        print("WARNING: novelty threshold unavailable; using maximum novelty.", flush=True)
    mission_novelty_distance = chosen[2]
    selected.append(mission_novelty)
    print(f"Batch mission 3 [discrepancy]: candidate {mission_novelty['number']}/{len(candidates)} | "
          f"response novelty={chosen[2]:.3f} | gate={novelty_gate}", flush=True)

    roles = ("robust GE identification", "complementary GE identification",
             "post-exit discrepancy novelty")
    selections, cumulative_ge, cumulative_exit = [], np.zeros((2, 2)), np.zeros((2, 2))
    for batch_number, (item, role) in enumerate(zip(selected, roles), 1):
        cumulative_ge += item["fisher_ge"]
        cumulative_exit += item["fisher_exit"]
        fisher = item["fisher_ge"] + item["fisher_exit"]
        metadata = {
            "batch_trajectory": batch_number,
            "selection_role": role,
            "selection_rule": ("maximum GE information in newest 50% of top-30% information pool" if batch_number == 1
                               else "maximum cumulative GE information in newest 50% of top-30% complementary pool" if batch_number == 2
                               else "maximum post-exit response novelty with GE and exit gates"),
            "minimum_batch_response_novelty": MIN_BATCH_NOVELTY,
            "minimum_information_fraction": MIN_INFORMATION_FRACTION,
            "top_information_fraction": TOP_INFORMATION_FRACTION,
            "top_novelty_fraction": TOP_NOVELTY_FRACTION,
            "adaptive_levels": [list(level) for level in ADAPTIVE_LEVELS],
            "novelty_x_range_m": [NOVELTY_X_START, NOVELTY_X_END],
            "GE_information_x_range_m": [OBSTACLE_X_START, OBSTACLE_X_END],
            "exit_information_x_range_m": [OBSTACLE_X_END, EXIT_X_END],
            "selected_GE_E_optimal_score": item["ge_score"],
            "selected_exit_E_optimal_score": item["exit_score"],
            "selected_joint_GE_score": float(np.linalg.eigvalsh(cumulative_ge)[0]),
            "selected_joint_exit_score": float(np.linalg.eigvalsh(cumulative_exit)[0]),
            "selected_information_fraction_of_maximum": item["ge_score"] / max(x["ge_score"] for x in accepted),
            "selected_novelty_R_rms": item["novelty"],
            "selected_GE_novelty_R_rms": item["novelty_ge"],
            "selected_exit_novelty_R_rms": item["novelty_exit"],
            "closest_historical_experiment": item["closest_historical"],
            "robust_parameter_samples": theta_samples.tolist(),
            "selected_batch_response_novelty": (
                mission_novelty_distance if batch_number == 3 else None),
            "selected_candidate_number": item["number"],
            "total_candidate_missions": len(candidates),
            "safe_candidates": len(accepted),
            "safe_candidate_knots_R": [x["knots"].tolist() for x in accepted],
            "novelty_reference_iterations": experimental_labels,
        }
        selections.append((item["knots"], fisher, metadata))
    return selections, np.asarray(history), coeffs, prior


def dt_safety_filter(knots_r, coeffs):
    """Retain the largest informative deformation that the nominal DT can fly."""
    nominal = np.full(N_KNOTS, NOMINAL_HEIGHT_R)
    for alpha in np.linspace(1.0, 0.0, 9):
        candidate = nominal + alpha*(np.asarray(knots_r)-nominal)
        x, dz, _ = dense_policy(jnp.asarray(candidate), samples=301)
        config, data = simulate(NOMINAL_VELOCITY, coeffs, x, dz)
        state = np.asarray(data["state"])
        if not np.all(np.isfinite(state)):
            continue
        mask = ((state[:, 0] >= OBSTACLE_X_START)
                & (state[:, 0] <= OBSTACLE_X_END))
        if not np.any(mask) or np.max(state[:, 0]) < X_ZOOM_END:
            continue
        clearance = np.asarray(lowest_rotor_clearance(config, data["state"]))
        safe = (np.min(clearance[mask]) >= MIN_ACTUAL_ROTOR_CLEARANCE-1.0e-5
                and np.max(np.abs(state[:, 2]-TABLE_HEIGHT_Z)) < 10.0*ROTOR_RADIUS
                and np.min(np.diff(state[:, 0])) > -1.0e-3)
        if safe:
            if alpha < 1.0:
                print(f"DT safety filter retained {100*alpha:.0f}% of the informative deformation.",
                      flush=True)
            return candidate
    raise RuntimeError("Even the nominal 1.5R mission fails the DT safety check.")


def save_generated_policy(knots_r, history, coeffs, prior, mode, source,
                          information_fisher=None, selection_metadata=None,
                          mission_file=MISSION_FILE):
    x, dz, _ = dense_policy(jnp.asarray(knots_r), samples=301)
    values = [scenario_metrics(jnp.asarray(knots_r), v, coeffs, prior) for v in ROBUST_VELOCITIES]
    minimum_clearance = np.inf
    for velocity in ROBUST_VELOCITIES:
        config, data = simulate(velocity, coeffs, x, dz)
        state = data["state"]
        mask = (state[:, 0] >= OBSTACLE_X_START) & (state[:, 0] <= OBSTACLE_X_END)
        clearances = lowest_rotor_clearance(config, state)
        minimum_clearance = min(minimum_clearance, float(jnp.min(jnp.where(mask, clearances, jnp.inf))))
    if minimum_clearance < MIN_ACTUAL_ROTOR_CLEARANCE-1.0e-5:
        raise RuntimeError(
            "Final DT safety check failed: lowest rotor clearance is "
            f"{minimum_clearance/ROTOR_RADIUS:.3f}R; "
            f"required {MIN_ACTUAL_CLEARANCE_R:.3f}R."
        )
    gains = np.asarray([float(item[0]) for item in values])
    tracks = np.asarray([float(item[1]) for item in values])
    spread = np.std(gains) if len(gains) > 1 else 0.0
    robust_gain = float(np.mean(gains)-ROBUST_KAPPA*spread)
    mission_file.parent.mkdir(parents=True, exist_ok=True)
    np.savez(mission_file, x_policy=np.asarray(x), delta_z_reference=np.asarray(dz),
             clearance_knots_R=knots_r, knot_x=KNOT_X,
             horizontal_velocity=np.asarray(NOMINAL_VELOCITY),
             height_in_rotor_radii=np.asarray(NOMINAL_HEIGHT_R), GE_coeffs=coeffs,
             GE_hessian=prior, cost_history=history, robust_d_opt_gain=robust_gain,
             minimum_actual_rotor_clearance_m=np.asarray(minimum_clearance),
             scenario_d_opt_gains=gains, scenario_tracking_costs=tracks,
             robust_velocities=np.asarray(ROBUST_VELOCITIES),
             identification_iteration=np.asarray(identification_iteration_label()),
             experiment_iteration=np.asarray(next_experiment_iteration_label()),
             mission_type=np.asarray("GE_VERTICAL_REFERENCE_GOVERNOR"),
             reference_region_mode=np.asarray(REFERENCE_REGION_MODE),
             trajectory_execution=np.asarray("spatial"), policy_source=np.asarray(source),
             optimization_mode=np.asarray(mode))
    if information_fisher is not None:
        with np.load(mission_file, allow_pickle=False) as saved:
            payload = {name: np.asarray(saved[name]) for name in saved.files}
        payload["E_optimal_Fisher"] = np.asarray(information_fisher)
        payload["E_optimal_score"] = np.asarray(
            np.min(np.linalg.eigvalsh(information_fisher)))
        if selection_metadata is not None:
            payload["novelty_R_rms"] = np.asarray(
                selection_metadata["selected_novelty_R_rms"])
            payload["GE_novelty_R_rms"] = np.asarray(
                selection_metadata["selected_GE_novelty_R_rms"])
            payload["exit_novelty_R_rms"] = np.asarray(
                selection_metadata["selected_exit_novelty_R_rms"])
            payload["robust_parameter_samples"] = np.asarray(
                selection_metadata["robust_parameter_samples"])
            payload["minimum_information_fraction"] = np.asarray(
                selection_metadata["minimum_information_fraction"])
            payload["top_information_fraction"] = np.asarray(
                selection_metadata["top_information_fraction"])
            payload["novelty_x_range_m"] = np.asarray(
                selection_metadata["novelty_x_range_m"])
            payload["selected_information_fraction_of_maximum"] = np.asarray(
                selection_metadata["selected_information_fraction_of_maximum"])
        np.savez(mission_file, **payload)
    metadata = {"mode": mode, "source": source,
                 "reference_region_mode": REFERENCE_REGION_MODE,
                 "identification_iteration": identification_iteration_label(),
                 "experiment_iteration": next_experiment_iteration_label(),
                "knot_x_m": KNOT_X.tolist(),
                "clearance_knots_R": knots_r.tolist(), "robust_d_opt_gain": robust_gain,
                "minimum_actual_rotor_clearance_m": minimum_clearance,
                "robust_velocities_m_s": list(ROBUST_VELOCITIES),
                "constraints": {"endpoint_min_R": MIN_ENDPOINT_R,
                                "internal_min_R": MIN_INTERNAL_R,
                                "maximum_R": MAX_REFERENCE_R,
                                "actual_rotor_min_R": MIN_ACTUAL_CLEARANCE_R,
                                "max_abs_vz_ref_m_s": MAX_ABS_VZ_REF,
                                "max_abs_az_ref_m_s2": MAX_ABS_AZ_REF}}
    if selection_metadata is not None:
        metadata["information_novelty_selection"] = selection_metadata
    mission_file.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return np.asarray(x), np.asarray(dz)


def plot_policy(x, dz, knots_r, history, coeffs, prior, mode,
                information_fisher=None, selection_metadata=None,
                plot_file=PLOT_FILE):
    fig, axes = plt.subplots(3, 1, figsize=(6.0, 8.0), constrained_layout=True)
    axis = axes[0]
    axis.axvspan(OBSTACLE_X_START, OBSTACLE_X_END, color="0.92")
    safe_knots = ([] if selection_metadata is None else
                  selection_metadata.get("safe_candidate_knots_R", []))
    for index, candidate_knots in enumerate(safe_knots):
        candidate_x, _, candidate_clearance = dense_policy(
            jnp.asarray(candidate_knots), samples=len(x))
        axis.plot(np.asarray(candidate_x), np.asarray(candidate_clearance),
                  color="tab:red", alpha=0.10, lw=0.65, zorder=1,
                  label="safe candidates" if index == 0 else None)
    desired = NOMINAL_HEIGHT_R + dz/ROTOR_RADIUS
    axis.plot(x, desired, color="black", lw=1.8, label="selected mission", zorder=4)
    axis.plot(KNOT_X, knots_r, "D", color="black", ms=4, zorder=5)
    candidate_information = []
    for velocity in ROBUST_VELOCITIES:
        _config, data = simulate(velocity, coeffs, jnp.asarray(x), jnp.asarray(dz))
        state = np.asarray(data["state"])
        clearance_r = (
            state[:, 2] + _config.ROTOR_PLANE_Z_ABOVE_COM - TABLE_HEIGHT_Z
        ) / ROTOR_RADIUS
        axis.plot(state[:, 0], clearance_r, lw=1.1, label=fr"DT $v_x={velocity:.2f}$ m/s")
        mask = (state[:, 0] >= X_ZOOM_START) & (state[:, 0] <= X_ZOOM_END)
        u = 1.0/np.maximum(clearance_r[mask], MIN_INTERNAL_R)
        up = u**coeffs[1]
        basis = np.column_stack((up, coeffs[0]*up*np.log(np.maximum(u, 1.0e-12))))
        candidate_information.append(INFORMATION_SCALE*(basis.T@basis)/max(len(u), 1))
    axis.set(xlabel=r"$x$ [m]", ylabel=r"$h/R$ [-]",
             xlim=(X_ZOOM_START, X_ZOOM_END), ylim=(-2, 6.2))
    axis.grid(alpha=0.15); axis.legend(frameon=False, fontsize=8, ncol=2)

    history = np.asarray(history)
    if mode == "information":
        axes[1].plot(history[:, 1], color="tab:blue", label=r"$\lambda_{\min}(F_{GE})$")
        if history.shape[1] >= 5:
            axes[1].plot(history[:, 4], color="tab:green",
                         label=r"$\lambda_{\min}(F_{exit})$")
        axes[1].set_ylabel(r"$\lambda_{\min}(F)$ [-]")
        axes[1].set_xlabel("Safe candidate evaluated")
        if history.shape[1] >= 4:
            novelty_axis = axes[1].twinx()
            novelty_axis.plot(history[:, 3], color="tab:orange", alpha=0.70,
                              label="novelty")
            novelty_axis.set_ylabel("response novelty RMS [-]", color="tab:orange")
        axes[1].legend(frameon=False, fontsize=8)
    else:
        axes[1].plot(history[:, 2], color="tab:blue")
        axes[1].set_ylabel(r"tracking cost [-]")
    if mode != "information":
        axes[1].set_xlabel("Iteration")
    axes[1].grid(alpha=0.15)

    def regularized_inverse(matrix):
        values, vectors = np.linalg.eigh(0.5*(matrix+matrix.T))
        return vectors @ np.diag(1.0/np.maximum(values, 1.0e-8)) @ vectors.T
    if information_fisher is not None:
        sigma_before = np.ones(2)
        sigma_after = np.sqrt(np.diag(
            np.linalg.inv(np.eye(2)+np.asarray(information_fisher))))
    else:
        information_new = np.mean(candidate_information, axis=0)
        sigma_before = np.sqrt(np.diag(regularized_inverse(prior)))
        sigma_after = np.sqrt(np.diag(regularized_inverse(prior+information_new)))
    positions = np.arange(2); width = 0.36
    axes[2].bar(positions-width/2, sigma_before, width, label="before")
    axes[2].bar(positions+width/2, sigma_after, width, label="after mission")
    axes[2].set_xticks(positions, (r"$A$", r"$p$"))
    axes[2].set_ylabel(r"normalized predicted $\sigma(a_i)$")
    axes[2].grid(axis="y", alpha=0.15); axes[2].legend(frameon=False)
    fig.savefig(plot_file, bbox_inches="tight")
    if SHOW_PLOT: plt.show()
    else: plt.close(fig)


def generate_policy(iterations=MPC_ITERATIONS, mode="information", source="informative_policy",
                    mission_file=MISSION_FILE, plot_file=PLOT_FILE):
    initial = None
    if mission_file.exists():
        with np.load(mission_file, allow_pickle=False) as data:
            if "clearance_knots_R" in data: initial = np.asarray(data["clearance_knots_R"])
    if mode == "information":
        selections, history, coeffs, prior = screen_information_library()
        outputs = []
        for batch_number, (knots, information_fisher, selection_metadata) in enumerate(selections, 1):
            batch_mission_file = mission_file.with_name(f"{mission_file.stem}_{batch_number}.npz")
            batch_plot_file = plot_file.with_name(f"{plot_file.stem}_{batch_number}.pdf")
            x, dz = save_generated_policy(
                knots, history, coeffs, prior, mode, source,
                information_fisher, selection_metadata, batch_mission_file)
            plot_policy(x, dz, knots, history, coeffs, prior, mode,
                        information_fisher, selection_metadata, batch_plot_file)
            outputs.append(str(batch_mission_file))
            print(f"Saved informative batch policy {batch_number}: {batch_mission_file}")
        mission_file.with_name(f"{mission_file.stem}_batch.json").write_text(
            json.dumps({"policies": outputs}, indent=2), encoding="utf-8")
        return
    else:
        knots, history, coeffs, prior = optimize_policy(iterations, mode, initial)
        knots = dt_safety_filter(knots, coeffs)
        information_fisher = None
        selection_metadata = None
    x, dz = save_generated_policy(knots, history, coeffs, prior, mode, source,
                                  information_fisher, selection_metadata, mission_file)
    plot_policy(x, dz, knots, history, coeffs, prior, mode,
                information_fisher, selection_metadata, plot_file)
    print(f"Saved {mode} policy: {mission_file}")


if __name__ == "__main__":
    generate_policy(mode="information", source="informative_policy")
