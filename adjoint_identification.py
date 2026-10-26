# Post-campaign identification of the static GE model.
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import os
import re

from jax import config as jax_config
import jax
import jax.numpy as jnp
import numpy as np

from jDT.postprocessing import copy_existing, create_numbered_directory, timestamp_label
from jDT.controller import CrazyfliePIDController
from jDT.main import build_environment
from jDT.simulator import DroneState, SimulationEnvironment
from jDT.propulsion import rotor_thrust_to_legacy_command
from jDT.params import configure_jax_runtime
from jDT.params import (
    EXP_DIR,
    MAX_HORIZONTAL_VELOCITY,
    OBSTACLE_X_END,
    OBSTACLE_X_START,
    ROTOR_RADIUS,
    TABLE_HEIGHT_Z,
    CrazyflieConfig,
    X_ZOOM_END,
    X_ZOOM_START,
    X_SPATIAL_STOP,
)

jax_config.update("jax_enable_x64", True)
configure_jax_runtime()

# =============================================================================
# USER SETTINGS
# =============================================================================
# "warm_start": identify E00 from the baseline alone, then keep
#               that baseline in the replay set and add one informative
#               mission at a time. E01--E12 correspond to the chronological
#               informative missions listed below.
# "cold_start": one independent fit with the complete D4 dataset. The initial
#               coefficients are selected by COLD_START_INITIALIZATION below.
RUN_MODE = "warm_start"
# Used only when RUN_MODE == "cold_start":
#   "cheeseman_bennett" -> [A, p] = [1/16, 2]
#   "zero"              -> [A, p] = [0, 0]
COLD_START_INITIALIZATION = "zero"
# Used by warm start. Set to None to recompute the complete
# sequence, or to a completed stage name (for example "D2" or "E06") to
# continue from its saved converged coefficients.
WARM_START_RESUME_FROM_STAGE = None

# Chronological cumulative information batches. D0 contains only the recent
# baseline. D1--D3 add complete informative campaigns in acquisition order;
# D4 adds the final near-wall/legacy cases. The INT and MB cases remain independent
# validation cases and do not enter the identification objective.
IDENTIFICATION_BATCHES = {
    "D0": {"BL"},
    "D1": {"INF_01", "INF_02", "INF_03"},
    "D2": {"INF_04", "INF_05", "INF_06"},
    "D3": {"INF_07", "INF_08", "INF_09"},
    "D4": {"INF_10", "INF_11", "INF_12"},
}
FULL_IDENTIFICATION_CASES = set().union(*IDENTIFICATION_BATCHES.values())

# Sequential replay used to display the baseline identification followed by
# the evolution after every informative mission. E00 starts from the
# Cheeseman--Bennett prior and uses only the recent PID baseline. Because all
# stages are cumulative, the baseline then remains in every E01--E12 fit.
SEQUENTIAL_BASELINE_CASE = "BL"
SEQUENTIAL_INFORMATION_CASES = (
    "INF_01", "INF_02", "INF_03",
    "INF_04", "INF_05", "INF_06",
    "INF_07", "INF_08", "INF_09",
    "INF_10", "INF_11", "INF_12",
)
SEQUENTIAL_IDENTIFICATION_BATCHES = {
    "E00": {SEQUENTIAL_BASELINE_CASE},
    **{
        f"E{index:02d}": {case}
        for index, case in enumerate(SEQUENTIAL_INFORMATION_CASES, start=1)
    },
}
SEQUENTIAL_DATASET_BOUNDARIES = {
    "E03": "D1",
    "E06": "D2",
    "E09": "D3",
    "E12": "D4",
}
INCLUDED_CASES = set(FULL_IDENTIFICATION_CASES)

# The loss uses the z-only formulation, restricted to the
# physical region in which the table ground-effect model is active.
FIT_X_START = OBSTACLE_X_START
FIT_X_END = OBSTACLE_X_END

# D0 starts from the classical Cheeseman--Bennett first-order coefficients.
# Every later stage starts from the converged coefficients of the previous one.
CHEESEMAN_BENNETT_GE_COEFFS = jnp.asarray([1.0 / 16.0, 2.0], dtype=jnp.float64)
ZERO_GE_COEFFS = jnp.asarray([0.0, 0.0], dtype=jnp.float64)
INITIALIZATION = "Cheeseman-Bennett"
SEQUENTIAL_WARM_RUN_LABEL = "sequential_missions"
COLD_RUN_LABEL = "balanced_batches"
_RUN_MODE_NORMALIZED = RUN_MODE.strip().lower()
POST_RUN_LABEL = {
    "warm_start": SEQUENTIAL_WARM_RUN_LABEL,
    "cold_start": COLD_RUN_LABEL,
}.get(_RUN_MODE_NORMALIZED, SEQUENTIAL_WARM_RUN_LABEL)
COLD_START_GE_COEFFS = CHEESEMAN_BENNETT_GE_COEFFS
ORIGINAL_IDENTIFICATION_DIR = Path(__file__).resolve().parent / "identification_output"

# Two-parameter static model: f_GE = 1 + A*u^p, u=R/h.
# The first campaign uses the fallback. Later campaigns automatically start
# from the most recent valid identification result.
GE_COEFFS_FALLBACK = COLD_START_GE_COEFFS
P_MIN, P_MAX = 0.0, 6.0
MIN_MODEL_CLEARANCE_R = 0.5
MIN_F_GE = 0.05

# Optimization has no prescribed iteration ceiling. It advances by this many
# iterations at a time until the windowed convergence criterion is satisfied.
OPTIMIZATION_BLOCK_ITERATIONS = 200
LEARNING_RATE = 5.0e-3
# The identification objective contains only normalized vertical-position
# error. Other logged channels remain in CLEAN files but do not enter the fit.

# Automatic convergence requires every condition to remain satisfied over a
# full window. This avoids stopping at one of the oscillatory gradient minima.
CONVERGENCE_MIN_ITERATIONS = 100
CONVERGENCE_WINDOW = 25
CONVERGENCE_RELATIVE_LOSS_RANGE = 2.0e-4
CONVERGENCE_COEFFICIENT_RANGE = 1.0e-3
CONVERGENCE_GRADIENT_NORM = 5.0e-3

SHOW_ITERATION_PLOT = os.environ.get("GE_RG_BATCH_RUN") != "1"
PLOT_PAUSE_SECONDS = 0.10
CONVERGENCE_PLOT_UPDATE_INTERVAL = 25
# The block implementation is retained only as an opt-in benchmark. On the
# full multi-experiment objective it can increase XLA compilation and memory
# pressure, so the proven one-step loop remains the default.
ADJOINT_COMPILED_BLOCK_SIZE = 25
USE_COMPILED_ADJOINT_LOOP = os.environ.get("GE_RG_COMPILED_ADJOINT_LOOP") == "1"

# The simulation starts at X_ZOOM_START with the nominal forward speed. A
# modest margin beyond the kinematic crossing time is enough to cover the
# complete scientific window without integrating a long unused trajectory.
# The factor retains the complete scientific z window with a small margin.
SIMULATION_DURATION_FACTOR = 1.10
CHECKPOINT_INTERVAL = 500

# EXP--DT comparisons are generated only after the complete sequence.
FINAL_COMPARISON_PLOT_NAME = "adjoint_match_D0_D4.pdf"
FINAL_CONVERGENCE_PLOT_NAME = "adjoint_convergence.pdf"
if _RUN_MODE_NORMALIZED == "warm_start":
    STAGE_SUMMARY_FILENAME = "E00_E12_summary.json"
    STAGE_COMPARISON_NAME = "sequential_D1_D4"
else:
    STAGE_SUMMARY_FILENAME = "D0_D4_summary.json"
    STAGE_COMPARISON_NAME = "D0_D4"

# Same y-limits used by postprocessing.py.
# Paper-style plotting of the three identified outputs versus measured x.
DT_COLOR = "red"
EXP_COLOR = "black"
DT_LINEWIDTH = 1.55
EXP_LINEWIDTH = 1.20
GRID_ALPHA = 0.16
MINOR_GRID_ALPHA = 0.08
MINOR_GRID_LINEWIDTH = 0.40
_NOMINAL_CONFIG = CrazyflieConfig()


def load_initial_GE_coeffs():
    """Return the fixed physical initialization used by D1."""
    return CHEESEMAN_BENNETT_GE_COEFFS, None, None


def _windowed_convergence_status(
    iterations_history,
    total_loss_history,
    gradient_norm_history,
    a1_history,
    a2_history,
    a3_history,
):
    """Return convergence and diagnostics over the latest history window."""
    if (
        iterations_history[-1] < CONVERGENCE_MIN_ITERATIONS
        or len(iterations_history) < CONVERGENCE_WINDOW + 1
    ):
        return False, {}

    window = slice(-(CONVERGENCE_WINDOW + 1), None)
    losses = np.asarray(total_loss_history[window], dtype=float)
    gradients = np.asarray(gradient_norm_history[window], dtype=float)
    coefficients = np.column_stack(
        (
            np.asarray(a1_history[window], dtype=float),
            np.asarray(a2_history[window], dtype=float),
            np.asarray(a3_history[window], dtype=float),
        )
    )
    relative_loss_range = float(
        np.ptp(losses) / max(abs(float(losses[-1])), 1.0e-12)
    )
    coefficient_ranges = np.ptp(coefficients, axis=0)
    max_coefficient_range = float(np.max(coefficient_ranges))
    max_gradient_norm = float(np.max(gradients))
    diagnostics = {
        "relative_loss_range": relative_loss_range,
        "coefficient_ranges": coefficient_ranges.tolist(),
        "max_coefficient_range": max_coefficient_range,
        "max_gradient_norm": max_gradient_norm,
    }
    converged = (
        relative_loss_range <= CONVERGENCE_RELATIVE_LOSS_RANGE
        and max_coefficient_range <= CONVERGENCE_COEFFICIENT_RANGE
        and max_gradient_norm <= CONVERGENCE_GRADIENT_NORM
    )
    return converged, diagnostics

IDENTIFICATION_OUTPUT_ROOT = (
    Path(__file__).resolve().parent
    / "identification_output"
    / ("Warm_start" if _RUN_MODE_NORMALIZED == "warm_start" else "Cold_start")
)
COLD_START_CB_OUTPUT_ROOT = (
    Path(__file__).resolve().parent
    / "identification_output"
    / "Cold_start"
    / "Cheeseman_Bennett"
)
COLD_START_ZERO_OUTPUT_ROOT = (
    Path(__file__).resolve().parent
    / "identification_output"
    / "Cold_start"
)
IDENTIFICATION_OUTPUT_DIR = IDENTIFICATION_OUTPUT_ROOT
CHECKPOINT_PATH = IDENTIFICATION_OUTPUT_DIR / "adjoint_checkpoint.npz"
HESSIAN_REGULARIZATION = 1.0e-6
@dataclass(frozen=True)
class Experiment:
    CASE_NAME: str
    HORIZONTAL_VELOCITY: float
    HEIGHT_IN_ROTOR_RADII: float
    time: jnp.ndarray
    x: jnp.ndarray
    vx: jnp.ndarray
    z_error: jnp.ndarray
    scales: jnp.ndarray
    CONTROL_MODE: int
    feedforward_x: jnp.ndarray
    feedforward_pwm: jnp.ndarray
    reference_x: jnp.ndarray
    reference_delta_z: jnp.ndarray
    DATASET_INDEX: int
    ITERATION_INDEX: int
    TRAJECTORY_INDEX: int


def _experiment_signature(experiments: tuple[Experiment, ...]) -> str:
    """Hash the clean objective and physics constants that affect it."""
    digest = hashlib.sha256()
    digest.update(b"post_static_GE_A_p_z_only_x_to_3p7_v1")
    digest.update(np.asarray([FIT_X_START, FIT_X_END], dtype=np.float64).tobytes())
    digest.update(np.asarray([
        _NOMINAL_CONFIG.MASS,
        _NOMINAL_CONFIG.FIRMWARE_THRUST_MAX_PER_MOTOR,
    ], dtype=np.float64).tobytes())
    for experiment in experiments:
        digest.update(experiment.CASE_NAME.encode("utf-8"))
        digest.update(np.asarray([
            experiment.HORIZONTAL_VELOCITY,
            experiment.HEIGHT_IN_ROTOR_RADII,
            experiment.CONTROL_MODE,
            experiment.DATASET_INDEX,
            experiment.ITERATION_INDEX,
            experiment.TRAJECTORY_INDEX,
        ], dtype=np.float64).tobytes())
        for values in (
            experiment.time,
            experiment.x,
            experiment.vx,
            experiment.z_error,
            experiment.feedforward_x,
            experiment.feedforward_pwm,
            experiment.reference_x,
            experiment.reference_delta_z,
        ):
            digest.update(
                np.asarray(jax.device_get(values), dtype=np.float64).tobytes()
            )
    return digest.hexdigest()


def _load_checkpoint(experiments: tuple[Experiment, ...]):
    if not CHECKPOINT_PATH.exists():
        return None
    try:
        with np.load(CHECKPOINT_PATH, allow_pickle=False) as data:
            saved_signature = str(data["experiment_signature"].item())
            current_signature = _experiment_signature(experiments)
            if saved_signature != current_signature:
                print(
                    f"[Checkpoint ignored] clean inputs changed: {CHECKPOINT_PATH}"
                )
                return None
            return {name: np.asarray(data[name]).copy() for name in data.files}
    except (KeyError, OSError, ValueError) as exc:
        print(f"[Checkpoint ignored] invalid file {CHECKPOINT_PATH}: {exc}")
        return None


def _save_checkpoint(
    experiments,
    iteration,
    target_iteration,
    GE_coeffs,
    first_moment,
    second_moment,
    initial_GE_coeffs,
    iterations_history,
    total_loss_history,
    z_loss_history,
    gradient_norm_history,
    a1_history,
    a2_history,
    a3_history,
) -> None:
    IDENTIFICATION_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    temporary_path = CHECKPOINT_PATH.with_suffix(".tmp")
    with temporary_path.open("wb") as stream:
        np.savez_compressed(
            stream,
            experiment_signature=np.asarray(_experiment_signature(experiments)),
            iteration=np.asarray(iteration, dtype=np.int32),
            target_iteration=np.asarray(target_iteration, dtype=np.int32),
            GE_coeffs=np.asarray(jax.device_get(GE_coeffs), dtype=float),
            first_moment=np.asarray(jax.device_get(first_moment), dtype=float),
            second_moment=np.asarray(jax.device_get(second_moment), dtype=float),
            initial_GE_coeffs=np.asarray(jax.device_get(initial_GE_coeffs), dtype=float),
            iteration_history=np.asarray(iterations_history, dtype=np.int32),
            total_loss_history=np.asarray(total_loss_history, dtype=float),
            z_loss_history=np.asarray(z_loss_history, dtype=float),
            gradient_norm_history=np.asarray(gradient_norm_history, dtype=float),
            a1_history=np.asarray(a1_history, dtype=float),
            a2_history=np.asarray(a2_history, dtype=float),
            a3_history=np.asarray(a3_history, dtype=float),
        )
    temporary_path.replace(CHECKPOINT_PATH)
    print(f"Checkpoint saved at iteration {iteration}: {CHECKPOINT_PATH}")


class AppliedFeedforwardPIDController(CrazyfliePIDController):
    """PID controller with a measured spatial collective-PWM offset."""

    def __init__(self, config, feedforward_x, feedforward_pwm):
        super().__init__(config)
        self.feedforward_x = jnp.asarray(feedforward_x, dtype=jnp.float64)
        self.feedforward_pwm = jnp.asarray(feedforward_pwm, dtype=jnp.float64)

    def correct_collective_thrust_pwm(self, thrust_pwm, state: jnp.ndarray):
        offset = jnp.interp(
            state[0],
            self.feedforward_x,
            self.feedforward_pwm,
            left=0.0,
            right=0.0,
        )
        return jnp.clip(thrust_pwm + offset, self.c.PWM_MIN, self.c.PWM_MAX)


class AppliedVerticalReferenceGovernor(CrazyfliePIDController):
    """Replay the exact experimental z-reference policy versus measured x."""

    def __init__(self, config, reference_x, reference_delta_z):
        super().__init__(config)
        self.reference_x = jnp.asarray(reference_x, dtype=jnp.float64)
        self.reference_delta_z = jnp.asarray(reference_delta_z, dtype=jnp.float64)

    def compute_control(self, state, ref, dt, controller_state, *, return_collective=False):
        delta_z = jnp.interp(
            state[0], self.reference_x, self.reference_delta_z,
            left=self.reference_delta_z[0], right=self.reference_delta_z[-1],
        )
        return super().compute_control(
            state, ref.at[2].add(delta_z), dt, controller_state,
            return_collective=return_collective,
        )


def _velocity_label(HORIZONTAL_VELOCITY: float) -> str:
    return f"{HORIZONTAL_VELOCITY:.2f}".replace(".", "p")


def _control_mode_label(control_mode: int) -> str:
    return {0: "PID", 1: "FF", 2: "RG"}.get(int(control_mode), "UNKNOWN")


def _read_clean_txt(
    path: Path,
    HORIZONTAL_VELOCITY: float,
    HEIGHT_IN_ROTOR_RADII: float,
    *,
    control_mode: int = 0,
    feedforward_path: Path | None = None,
    dataset_index: int = 0,
    iteration_index: int = 0,
    trajectory_index: int = 0,
    case_name: str = "",
) -> Experiment:
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            values = tuple(float(value) for value in stripped.split())
            if len(values) < 6:
                raise ValueError(
                    f"Expected 6 legacy columns or 7 columns "
                    f"(t x z vx vz Tcmd pitch) in {path}, found "
                    f"{len(values)}. Run pp_EXP.py first."
                )
            rows.append(values)

    if not rows:
        raise ValueError(f"No experimental samples found in {path}")

    raw = jnp.asarray(rows, dtype=jnp.float64)
    time, x, z_clean, vx_clean, _vz_clean, _command_clean = (
        raw[:, index] for index in range(6)
    )

    mask = (x >= X_ZOOM_START) & (x <= X_ZOOM_END)
    indices = jnp.where(mask)[0]
    if indices.shape[0] < 2:
        raise ValueError(
            f"Insufficient samples in x=[{X_ZOOM_START}, "
            f"{X_ZOOM_END}] for {path}"
        )

    time = time[indices] - time[indices][0]
    x = x[indices]
    vx = vx_clean[indices]
    z_error = (
        z_clean[indices]
        - HEIGHT_IN_ROTOR_RADII * ROTOR_RADIUS
    )
    # Use one physical scale for every experiment: each case contributes one
    # mean squared vertical error expressed in rotor radii.
    scales = jnp.asarray([ROTOR_RADIUS], dtype=jnp.float64)

    if control_mode == 1:
        if feedforward_path is None or not feedforward_path.exists():
            raise FileNotFoundError(
                f"Missing FF replay profile for {path.name}: {feedforward_path}. "
                "Run pp_EXP.py on the corresponding raw FF test."
            )
        profile = np.loadtxt(feedforward_path, skiprows=1)
        if profile.ndim == 1:
            profile = profile[None, :]
        if profile.shape[0] < 2 or profile.shape[1] != 2:
            raise ValueError(f"Invalid FF replay profile: {feedforward_path}")
        if np.any(np.diff(profile[:, 0]) <= 0.0):
            raise ValueError(f"FF replay x must be strictly increasing: {feedforward_path}")
        feedforward_x = jnp.asarray(profile[:, 0], dtype=jnp.float64)
        feedforward_pwm = jnp.asarray(profile[:, 1], dtype=jnp.float64)
    else:
        feedforward_x = jnp.array([X_ZOOM_START, X_ZOOM_END], dtype=jnp.float64)
        feedforward_pwm = jnp.zeros(2, dtype=jnp.float64)

    reference_x = jnp.array([X_ZOOM_START, X_ZOOM_END], dtype=jnp.float64)
    reference_delta_z = jnp.zeros(2, dtype=jnp.float64)
    if control_mode == 2:
        if feedforward_path is None or not feedforward_path.exists():
            raise FileNotFoundError(
                f"Missing RG replay profile for {path.name}: {feedforward_path}. "
                "Run pp_EXP.py on the corresponding raw RG test."
            )
        profile = np.loadtxt(feedforward_path, skiprows=1)
        if profile.ndim == 1:
            profile = profile[None, :]
        if profile.shape[0] < 2 or profile.shape[1] != 2:
            raise ValueError(f"Invalid RG replay profile: {feedforward_path}")
        if np.any(np.diff(profile[:, 0]) <= 0.0):
            raise ValueError(f"RG replay x must be strictly increasing: {feedforward_path}")
        if profile[0, 0] > X_ZOOM_START + 1.0e-9:
            slope = ((profile[1, 1] - profile[0, 1])
                     / (profile[1, 0] - profile[0, 0]))
            first_delta = profile[0, 1] + slope * (X_ZOOM_START - profile[0, 0])
            profile = np.vstack(([X_ZOOM_START, first_delta], profile))
        reference_x = jnp.asarray(profile[:, 0], dtype=jnp.float64)
        reference_delta_z = jnp.asarray(profile[:, 1], dtype=jnp.float64)

    return Experiment(
        CASE_NAME=case_name,
        HORIZONTAL_VELOCITY=HORIZONTAL_VELOCITY,
        HEIGHT_IN_ROTOR_RADII=HEIGHT_IN_ROTOR_RADII,
        time=time,
        x=x,
        vx=vx,
        z_error=z_error,
        scales=scales,
        CONTROL_MODE=control_mode,
        feedforward_x=feedforward_x,
        feedforward_pwm=feedforward_pwm,
        reference_x=reference_x,
        reference_delta_z=reference_delta_z,
        DATASET_INDEX=dataset_index,
        ITERATION_INDEX=iteration_index,
        TRAJECTORY_INDEX=trajectory_index,
    )


def load_experiments(cases=None) -> tuple[Experiment, ...]:
    manifest_path = EXP_DIR.parent / "legacy_name_map.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    def legacy_tuple(label: str) -> tuple[int, int]:
        match = re.fullmatch(r"It(?P<iteration>[0-9]+)(?:_(?P<trajectory>[0-9]+))?", label)
        if match is None:
            raise ValueError(f"Invalid legacy case in {manifest_path}: {label}")
        return int(match.group("iteration")), int(match.group("trajectory") or 0)

    legacy_to_paper = {
        legacy_tuple(legacy): str(paper)
        for legacy, paper in manifest["cases"].items()
    }
    paper_to_legacy = {paper: legacy for legacy, paper in legacy_to_paper.items()}
    requested = INCLUDED_CASES if cases is None else set(cases)
    selected_cases = {
        paper_to_legacy[str(case).removeprefix("EXP_")]
        if isinstance(case, str) else tuple(case)
        for case in requested
    }
    experiments = []
    pattern = re.compile(r"^EXP_(?P<case>[A-Z0-9_]+)_clean\.txt$")
    candidates = []
    for path in EXP_DIR.glob("EXP_*_clean.txt"):
        match = pattern.fullmatch(path.name)
        if match is None:
            continue
        case_name = match.group("case")
        if case_name not in paper_to_legacy:
            continue
        iteration_index, trajectory_index = paper_to_legacy[case_name]
        if (iteration_index, trajectory_index) not in selected_cases:
            continue
        prefix = f"EXP_{case_name}"
        metadata_path = path.with_name(f"{prefix}_metadata.json")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Missing experiment metadata: {metadata_path}")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        velocity = float(metadata["horizontal_velocity"])
        height = float(metadata["height_in_rotor_radii"])
        mode_label = str(metadata["control_mode"]).upper()
        try:
            control_mode = {"PID": 0, "FF": 1, "RG": 2}[mode_label]
        except KeyError as error:
            raise ValueError(f"Unsupported control_mode={mode_label!r} in {metadata_path}") from error
        if velocity > MAX_HORIZONTAL_VELOCITY + 1.0e-9:
            print(
                f"[Skipped outside velocity domain] {path.name}: "
                f"vx={velocity:.2f} m/s > {MAX_HORIZONTAL_VELOCITY:.2f} m/s"
            )
            continue
        candidates.append((iteration_index, trajectory_index, case_name, velocity, height, control_mode, path))

    available_cases = {(item[0], item[1]) for item in candidates}
    missing_cases = sorted(selected_cases - available_cases)
    if missing_cases:
        labels = ", ".join(
            f"It{iteration}" + (f".{trajectory}" if trajectory else "")
            for iteration, trajectory in missing_cases
        )
        raise FileNotFoundError(
            "The post-adjoint dataset is incomplete. Missing CLEAN cases: " + labels
        )

    for dataset_index, (iteration_index, trajectory_index, case_name, velocity, height, control_mode, path) in enumerate(
        sorted(candidates, key=lambda item: (item[0], item[1])),
        start=1,
    ):
        feedforward_path = None
        prefix = f"EXP_{case_name}"
        if control_mode == 1:
            feedforward_path = path.with_name(f"{prefix}_FF_input.txt")
        elif control_mode == 2:
            feedforward_path = path.with_name(f"{prefix}_RG_input.txt")
        experiments.append(
            _read_clean_txt(
                path,
                velocity,
                height,
                control_mode=control_mode,
                feedforward_path=feedforward_path,
                dataset_index=dataset_index,
                iteration_index=iteration_index,
                trajectory_index=trajectory_index,
                case_name=case_name,
            )
        )

    if not experiments:
        raise FileNotFoundError(
            f"No matching experiments found in {EXP_DIR}"
        )

    return tuple(experiments)


def simulate_aligned(
    GE_coeffs: jnp.ndarray,
    experiment: Experiment,
    *,
    absolute_clearance: bool = False,
):
    config, base_environment, initial_state = build_environment(
        HORIZONTAL_VELOCITY=experiment.HORIZONTAL_VELOCITY,
        HEIGHT_IN_ROTOR_RADII=experiment.HEIGHT_IN_ROTOR_RADII,
        PRE_HOVER_TIME=0.0,
    )
    if experiment.CONTROL_MODE == 2:
        controller = AppliedVerticalReferenceGovernor(
            config, experiment.reference_x, experiment.reference_delta_z
        )
    else:
        controller = AppliedFeedforwardPIDController(
            config, experiment.feedforward_x, experiment.feedforward_pwm
        )
    simulation_duration = (
        SIMULATION_DURATION_FACTOR
        * (X_SPATIAL_STOP - X_ZOOM_START)
        / experiment.HORIZONTAL_VELOCITY
    )
    environment = SimulationEnvironment(
        config,
        controller,
        base_environment.trajectory,
        dt=config.DT,
        t_final=simulation_duration,
        ge_velocity_x=experiment.x,
        ge_velocity_vx=experiment.vx,
    )

    # Begin directly from the known steady out-of-ground-effect condition at
    # the start of the scientific window.
    pwm_oge = rotor_thrust_to_legacy_command(
        config.MASS * config.GRAVITY / 4.0,
        config.FIRMWARE_THRUST_MAX_PER_MOTOR,
    )
    rpm_oge_physical = environment.vehicle.pwm_to_rpm(pwm_oge)
    initial_delta_z = jnp.where(
        experiment.CONTROL_MODE == 2,
        experiment.reference_delta_z[0],
        0.0,
    )
    initial_state = DroneState(
        X_ZOOM_START,
        0.0,
        initial_state.z + initial_delta_z,
        experiment.HORIZONTAL_VELOCITY,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        rpm_oge_physical,
        rpm_oge_physical,
        rpm_oge_physical,
        rpm_oge_physical,
    )

    # Reproduce the experimental controller state at the entrance of the
    # scientific region. Before X_ZOOM_START the spatial FF law is zero, so
    # the PID has settled on the OGE collective command. The controller hook
    # then adds the measured FF profile without cancelling it in advance.
    pid_collective_at_start = pwm_oge
    thrust_delta = (pid_collective_at_start - controller.base_thrust_pwm) / 1000.0
    controller_state = controller.initial_state()
    velocity_z_ki = controller.gains[5, 1]
    velocity_z_integral = thrust_delta / jnp.maximum(velocity_z_ki, 1.0e-12)
    controller_state = controller_state._replace(
        integral=controller_state.integral.at[5].set(velocity_z_integral)
    )

    data = environment.run(
        initial_state,
        GE_coeffs,
        initial_controller_state=controller_state,
    )

    state = data["state"]
    reference = data["reference"]
    if "collective_pwm" not in data:
        raise KeyError(
            "DT output does not contain 'collective_pwm'. "
            "Use jDT/controller.py TAG R and jDT/simulator.py TAG X or newer."
        )
    # Keep static array extents inside the jitted objective. The experimental
    # queries already lie in the scientific window, so slicing the DT first is
    # unnecessary and would require data-dependent indices that XLA forbids.
    x_dt = state[:, 0]
    if absolute_clearance:
        z_clearance_dt = (
            state[:, 2] + config.ROTOR_PLANE_Z_ABOVE_COM - TABLE_HEIGHT_Z
        )
        return jnp.interp(experiment.x, x_dt, z_clearance_dt)
    z_error_dt = state[:, 2] - reference[:, 2]
    return jnp.interp(experiment.x, x_dt, z_error_dt)


def experiment_channel_losses(
    GE_coeffs: jnp.ndarray,
    experiment: Experiment,
) -> jnp.ndarray:
    z_dt = simulate_aligned(GE_coeffs, experiment)
    fit_mask = (
        (experiment.x >= FIT_X_START) & (experiment.x <= FIT_X_END)
    ).astype(jnp.float64)
    residual = (z_dt - experiment.z_error) / experiment.scales[0]
    return jnp.sum(residual**2 * fit_mask) / jnp.maximum(jnp.sum(fit_mask), 1.0)


def mean_channel_losses(
    GE_coeffs: jnp.ndarray,
    experiments: tuple[Experiment, ...],
) -> jnp.ndarray:
    mean_z_loss = jnp.mean(jnp.stack(
        [experiment_channel_losses(GE_coeffs, experiment) for experiment in experiments]
    ))
    return jnp.asarray([mean_z_loss])


def total_loss(
    GE_coeffs: jnp.ndarray,
    experiments: tuple[Experiment, ...],
) -> jnp.ndarray:
    loss, _ = total_loss_with_channels(GE_coeffs, experiments)
    return loss


def total_loss_with_channels(
    GE_coeffs: jnp.ndarray,
    experiments: tuple[Experiment, ...],
):
    """Return total and channel losses from the same DT simulations."""
    channel_losses = mean_channel_losses(GE_coeffs, experiments)
    return channel_losses[0], channel_losses


def project_GE_coeffs(coeffs: jnp.ndarray) -> jnp.ndarray:
    """Enforce decay with clearance and positive thrust over the safe domain."""
    p = jnp.clip(coeffs[1], P_MIN, P_MAX)
    max_u = 1.0 / MIN_MODEL_CLEARANCE_R
    minimum_A = (MIN_F_GE - 1.0) / max_u**p
    return jnp.asarray([jnp.maximum(coeffs[0], minimum_A), p])


def projected_gradient(coeffs: jnp.ndarray, gradient: jnp.ndarray) -> jnp.ndarray:
    """Remove gradient components that point outside active constraints."""
    p = coeffs[1]
    gp = jnp.where(
        ((p <= P_MIN) & (gradient[1] > 0.0))
        | ((p >= P_MAX) & (gradient[1] < 0.0)),
        0.0,
        gradient[1],
    )
    max_u = 1.0 / MIN_MODEL_CLEARANCE_R
    minimum_A = (MIN_F_GE - 1.0) / max_u**p
    gA = jnp.where(
        (coeffs[0] <= minimum_A) & (gradient[0] > 0.0),
        0.0,
        gradient[0],
    )
    return jnp.asarray([gA, gp])


class OneDecimalScalarFormatter:
    """Small wrapper created lazily to avoid importing Matplotlib at module import."""

    @staticmethod
    def make():
        from matplotlib.ticker import ScalarFormatter

        class _Formatter(ScalarFormatter):
            def _set_format(self):
                self.format = "%1.1f"
                if self._usetex or self._useMathText:
                    self.format = r"$\mathdefault{%1.1f}$"

        formatter = _Formatter(useMathText=True)
        formatter.set_scientific(True)
        formatter.set_powerlimits((0, 0))
        formatter.set_useOffset(False)
        return formatter


class CommonExponentLogFormatter:
    """Log-axis formatter with one common scientific multiplier."""

    @staticmethod
    def apply(axis, values):
        import numpy as np
        from matplotlib.ticker import FuncFormatter

        finite_positive = np.asarray(values, dtype=float)
        finite_positive = finite_positive[np.isfinite(finite_positive) & (finite_positive > 0.0)]
        if finite_positive.size == 0:
            return

        exponent = int(np.floor(np.log10(np.min(finite_positive))))
        scale = 10.0 ** exponent

        def _format(value, _position):
            if value <= 0.0:
                return ""
            scaled = value / scale
            if abs(scaled - round(scaled)) < 1.0e-8:
                return rf"$\mathdefault{{{int(round(scaled))}}}$"
            return rf"$\mathdefault{{{scaled:.1f}}}$"

        axis.yaxis.set_major_formatter(FuncFormatter(_format))
        axis.yaxis.get_offset_text().set_visible(False)
        axis.text(
            0.0,
            1.012,
            rf"$\times 10^{{{exponent}}}$",
            transform=axis.transAxes,
            ha="left",
            va="bottom",
            fontsize=10,
        )


def _configure_matplotlib(plt):
    plt.rcParams.update({
        "text.usetex": False,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman", "CMU Serif", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 12,
        "axes.linewidth": 0.8,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "axes.unicode_minus": False,
    })


def _style_axis(axis, ylabel, show_xlabel):
    axis.set_ylabel(ylabel)
    axis.set_xlabel(r"$x$ [m]" if show_xlabel else "")
    # Show the complete scientific window, including the pre-obstacle segment.
    # The loss itself is restricted to FIT_X_START <= x <= FIT_X_END.
    axis.set_xlim(float(X_ZOOM_START), float(X_ZOOM_END))
    axis.tick_params(axis="x", which="major", bottom=True, top=True, labelbottom=True)
    axis.minorticks_on()
    axis.tick_params(axis="both", which="minor", bottom=False, top=False, left=False, right=False)
    axis.grid(True, which="major", alpha=GRID_ALPHA, linewidth=0.55)
    axis.grid(True, which="minor", alpha=MINOR_GRID_ALPHA, linewidth=MINOR_GRID_LINEWIDTH)
    axis.yaxis.set_major_formatter(OneDecimalScalarFormatter.make())
    for spine in axis.spines.values():
        spine.set_linewidth(0.8)


class IterationPlot:
    """Live paper-style EXP-versus-DT monitor for the selected experiment."""

    def __init__(self, experiment: Experiment):
        import matplotlib.pyplot as plt

        _configure_matplotlib(plt)
        self.plt = plt
        self.experiment = experiment
        self.figure = None
        self.plt.ion()

    def update(
        self,
        iteration: int,
        GE_coeffs: jnp.ndarray,
        loss: jnp.ndarray,
        channel_losses: jnp.ndarray,
        aligned_signals,
    ) -> None:
        if self.figure is not None:
            self.plt.close(self.figure)

        self.figure, axis = self.plt.subplots(figsize=(4.6, 3.0), constrained_layout=True)
        x_plot = jax.device_get(self.experiment.x)
        axis.plot(x_plot, jax.device_get(aligned_signals / ROTOR_RADIUS), color=DT_COLOR,
                  linewidth=DT_LINEWIDTH, label="DT", zorder=3)
        exp_clearance = (
            self.experiment.z_error
            + self.experiment.HEIGHT_IN_ROTOR_RADII * ROTOR_RADIUS
        )
        axis.plot(x_plot, jax.device_get(exp_clearance / ROTOR_RADIUS),
                  color=EXP_COLOR, linewidth=EXP_LINEWIDTH, label="EXP", zorder=4)
        _style_axis(axis, r"$z/R$ [-]", show_xlabel=True)
        axis.set_ylim(-2.0, 6.5)
        axis.axvspan(OBSTACLE_X_START, OBSTACLE_X_END, color="0.92", zorder=0)
        for edge in (OBSTACLE_X_START, OBSTACLE_X_END):
            axis.axvline(edge, linestyle="--", color="black", linewidth=0.75, alpha=0.65)
        axis.legend(frameon=False, ncol=2)
        self.figure.suptitle(
            f"vx={self.experiment.HORIZONTAL_VELOCITY:.2f} m/s, "
            f"h={self.experiment.HEIGHT_IN_ROTOR_RADII:g}R | "
            f"{_control_mode_label(self.experiment.CONTROL_MODE)} | "
            f"Iteration {iteration} | loss={float(jax.device_get(loss)):.3e} | "
            f"GE=[A={float(jax.device_get(GE_coeffs[0])):.3f}, "
            f"p={float(jax.device_get(GE_coeffs[1])):.3f}]",
            y=1.02,
            fontsize=9,
        )

        self.plt.show(block=False)
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        self.plt.pause(PLOT_PAUSE_SECONDS)


def _update_live_comparisons(
    iteration_plots,
    experiments,
    iteration: int,
    GE_coeffs: jnp.ndarray,
    loss: jnp.ndarray,
    channel_losses: jnp.ndarray,
) -> None:
    """Update all EXP-DT comparison windows at one selected optimization snapshot."""
    for iteration_plot, experiment in zip(iteration_plots, experiments):
        aligned_signals = simulate_aligned(
            GE_coeffs,
            experiment,
            absolute_clearance=True,
        )
        iteration_plot.update(
            iteration,
            GE_coeffs,
            loss,
            channel_losses,
            aligned_signals,
        )


class ConvergencePlot:
    """Rebuild the convergence figure from scratch at every iteration."""

    def __init__(self):
        import matplotlib.pyplot as plt

        _configure_matplotlib(plt)
        self.plt = plt
        self.plt.ion()
        self.figure = None
        self.axis_loss = None
        self.axis_gradient = None
        self.axis_coeff = None

    def update(
        self,
        iterations,
        total_losses,
        z_losses,
        gradient_norms,
        a1_history,
        a2_history,
        a3_history,
    ) -> None:
        if self.figure is not None:
            self.plt.close(self.figure)

        self.figure, axes = self.plt.subplots(
            2,
            1,
            figsize=(5.8, 6.6),
            sharex=True,
            constrained_layout=True,
        )
        self.axis_loss = axes[0]
        self.axis_coeff = axes[1]
        self.axis_gradient = self.axis_loss.twinx()

        it = list(iterations)
        self.axis_loss.plot(
            it, total_losses, color="black", linestyle="-", linewidth=1.55, label=r"$J_p$"
        )
        self.axis_loss.plot(
            it, z_losses, color="magenta", linestyle="--", linewidth=1.25, label=r"$J_z$"
        )
        self.axis_gradient.plot(
            it, gradient_norms, color="dimgray", linestyle="--", linewidth=1.25,
            label=r"$\|\nabla_{\theta}J_p\|_2$",
        )

        self.axis_coeff.plot(
            it, a1_history, color="magenta", linestyle="-", linewidth=1.35, label=r"$A$"
        )
        self.axis_coeff.plot(
            it, a2_history, color="orange", linestyle="--", linewidth=1.35, label=r"$p$"
        )

        self.axis_loss.set_ylabel("Loss [-]")
        self.axis_gradient.set_ylabel(r"$\|\nabla_{\theta}J_p\|_2$ [-]")
        self.axis_coeff.set_ylabel(r"$\theta_{\mathrm{GE}}$ [-]")
        self.axis_coeff.set_xlabel("Iteration")

        xmax = max(int(iterations[-1]) if iterations else 1, 1)
        self.axis_loss.set_xlim(0, xmax)
        self.axis_loss.set_yscale("log")
        self.axis_gradient.set_yscale("log")

        # Keep iteration ticks visible on both panels, but only the lower panel
        # carries the shared x-axis label.
        self.axis_loss.tick_params(axis="x", which="major", labelbottom=True)
        self.axis_coeff.tick_params(axis="x", which="major", labelbottom=True)

        for axis in (self.axis_loss, self.axis_coeff):
            axis.minorticks_on()
            axis.grid(True, which="major", alpha=GRID_ALPHA, linewidth=0.55)
            axis.grid(
                True, which="minor", alpha=MINOR_GRID_ALPHA,
                linewidth=MINOR_GRID_LINEWIDTH,
            )
            axis.tick_params(direction="in", top=True, right=True)

        self.axis_gradient.tick_params(direction="in", right=True)

        # Free-flight-style compact scientific notation.  The logarithmic
        # loss axis uses one common multiplier (for example x10^-1) rather
        # than repeating scientific notation on every tick.
        CommonExponentLogFormatter.apply(
            self.axis_loss,
            list(total_losses) + list(z_losses),
        )
        self.axis_coeff.yaxis.set_major_formatter(OneDecimalScalarFormatter.make())

        handles_left, labels_left = self.axis_loss.get_legend_handles_labels()
        handles_right, labels_right = self.axis_gradient.get_legend_handles_labels()
        self.axis_loss.legend(
            handles_left + handles_right,
            labels_left + labels_right,
            frameon=False,
            ncol=3,
            loc="upper right",
        )
        self.axis_coeff.legend(frameon=False, ncol=3, loc="best")

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        self.plt.pause(PLOT_PAUSE_SECONDS)

    def save_final(self, output_path: Path) -> Path:
        """Save only the latest convergence view as a vector PDF."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.figure.savefig(output_path, bbox_inches="tight")
        print(f"Final convergence plot saved: {output_path}")
        return output_path


def _comparison_plot_name(experiment: Experiment) -> str:
    mode = _control_mode_label(experiment.CONTROL_MODE)
    suffix = (f"_{experiment.TRAJECTORY_INDEX}" if experiment.TRAJECTORY_INDEX else "")
    return f"adjoint_match_selected_iterations_It{experiment.ITERATION_INDEX}{suffix}_{mode}.pdf"


def _comparison_iterations(final_iteration: int) -> tuple[int, ...]:
    """Return automatic 0%, 5%, 50%, and 100% comparison iterations."""
    final_iteration = int(final_iteration)
    if final_iteration < 1:
        return (0,)
    requested = (
        0,
        int(round(0.05 * final_iteration)),
        int(round(0.50 * final_iteration)),
        final_iteration,
    )
    # Preserve order while avoiding duplicates for very short runs.
    return tuple(dict.fromkeys(requested))


def save_selected_iteration_comparison(
    experiment: Experiment,
    coefficient_history: dict[int, jnp.ndarray],
    final_iteration: int,
    *,
    output_name: str | None = None,
    keep_open: bool = False,
) -> Path:
    """Save the final paper-style comparison at 0, 5, 50 and 100% of the run."""
    import matplotlib.pyplot as plt

    _configure_matplotlib(plt)
    IDENTIFICATION_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    selected_iterations = _comparison_iterations(final_iteration)
    missing = [
        iteration
        for iteration in selected_iterations
        if iteration not in coefficient_history
    ]
    if missing:
        raise RuntimeError(
            f"Missing requested comparison coefficient snapshots: {missing}"
        )

    x_plot = jax.device_get(experiment.x)
    exp_z = (
        experiment.z_error
        + experiment.HEIGHT_IN_ROTOR_RADII * ROTOR_RADIUS
    ) / ROTOR_RADIUS

    palette = ("magenta", "orange", "darkred", "red")
    styles = (
        (0, (6.0, 2.0, 1.2, 2.0)),
        "-.",
        "--",
        "-",
    )
    style_by_iteration = {
        iteration: (palette[index], styles[index])
        for index, iteration in enumerate(selected_iterations)
    }

    # Compute only the DT signals needed for the final selected iterations.
    selected_signals = {}
    for iteration in selected_iterations:
        coeffs = coefficient_history[iteration]
        selected_signals[iteration] = simulate_aligned(
            coeffs,
            experiment,
            absolute_clearance=True,
        )

    figure, axis = plt.subplots(figsize=(5.25, 3.35), constrained_layout=True)
    axis.plot(x_plot, jax.device_get(exp_z), color="black", linewidth=1.35,
              label="EXP", zorder=5)
    for iteration in selected_iterations:
        coeffs_host = jax.device_get(coefficient_history[iteration])
        label = (rf"DT (It. {iteration}, $A={float(coeffs_host[0]):.3f}$, "
                 rf"$p={float(coeffs_host[1]):.3f}$)")
        color, linestyle = style_by_iteration[iteration]
        is_final = iteration == final_iteration
        axis.plot(x_plot, jax.device_get(selected_signals[iteration] / ROTOR_RADIUS),
                  color=color, linestyle=linestyle,
                  linewidth=1.60 if is_final else 1.35, label=label,
                  zorder=4 if is_final else 3)
    _style_axis(axis, r"$z/R$ [-]", show_xlabel=True)
    axis.set_ylim(-2.0, 6.5)
    axis.axvspan(OBSTACLE_X_START, OBSTACLE_X_END, color="0.92", zorder=0)
    for edge in (OBSTACLE_X_START, OBSTACLE_X_END):
        axis.axvline(edge, linestyle="--", color="black", linewidth=0.70, alpha=0.55)
    axis.legend(frameon=False, fontsize=7.5)

    if output_name is None:
        output_name = FINAL_COMPARISON_PLOT_NAME
    output_path = IDENTIFICATION_OUTPUT_DIR / output_name
    figure.savefig(output_path, bbox_inches="tight")
    if keep_open:
        plt.show(block=False)
        figure.canvas.draw()
        figure.canvas.flush_events()
    else:
        plt.close(figure)
    print(f"Selected-iteration comparison saved: {output_path}")

    comparison_data = {
        "iterations": jnp.asarray(selected_iterations, dtype=jnp.int32),
        "coefficients": jnp.stack([coefficient_history[it] for it in selected_iterations]),
        "x": jnp.asarray(experiment.x, dtype=jnp.float64),
        "exp_z_norm": jnp.asarray(exp_z, dtype=jnp.float64),
        "dt_z_norm": jnp.stack([selected_signals[it] / ROTOR_RADIUS for it in selected_iterations]),
        "obstacle_start_x": jnp.asarray(OBSTACLE_X_START, dtype=jnp.float64),
        "obstacle_end_x": jnp.asarray(OBSTACLE_X_END, dtype=jnp.float64),
    }
    return output_path, comparison_data


def _ask_for_additional_iterations() -> int:
    """Ask whether the user wants to extend the current Adam optimization."""
    if os.environ.get("ADJOINT_AUTO_NO") == "1" or os.environ.get("GE_RG_BATCH_RUN") == "1":
        print("Automatic response: no additional adjoint iterations requested.")
        return 0
    while True:
        answer = input("Vuoi aggiungere altre iterazioni? [si/no]: ").strip().lower()
        if answer in {"no", "n"}:
            return 0
        if answer in {"si", "sì", "s"}:
            while True:
                raw = input("Quante iterazioni vuoi aggiungere? ").strip()
                try:
                    additional = int(raw)
                except ValueError:
                    print("Inserisci un numero intero positivo.")
                    continue
                if additional <= 0:
                    print("Inserisci un numero intero positivo.")
                    continue
                return additional
        print("Risposta non valida. Scrivi 'si' oppure 'no'.")


def optimize(
    experiments: tuple[Experiment, ...],
    initial_coefficients: jnp.ndarray,
    initialization_label: str,
):
    # Close over the fixed experimental dataset before JIT compilation. This
    # compiles the complete differentiable DT once; subsequent Adam iterations
    # reuse the executable and receive only [A, p].
    value_channels_and_grad = jax.jit(
        jax.value_and_grad(
            lambda coeffs: total_loss_with_channels(coeffs, experiments),
            has_aux=True,
        )
    )

    GE_coeffs = jnp.asarray(initial_coefficients, dtype=jnp.float64)
    warm_start_path = initialization_label
    previous_loss = None
    GE_coeffs = project_GE_coeffs(GE_coeffs)
    initial_GE_coeffs = jnp.array(GE_coeffs)
    checkpoint = _load_checkpoint(experiments)
    resumed_iteration = 0
    if checkpoint is not None:
        GE_coeffs = project_GE_coeffs(
            jnp.asarray(checkpoint["GE_coeffs"], dtype=jnp.float64)
        )
        initial_GE_coeffs = jnp.asarray(
            checkpoint["initial_GE_coeffs"], dtype=jnp.float64
        )
        resumed_iteration = int(checkpoint["iteration"].item())
        warm_start_path = CHECKPOINT_PATH
        previous_loss = float(checkpoint["total_loss_history"][-1])
        print(
            f"Resuming exact Adam checkpoint from iteration "
            f"{resumed_iteration}: {CHECKPOINT_PATH}"
        )
    warm_start_used = True
    if checkpoint is None:
        print(
            "Warm start from "
            f"{warm_start_path}: GE_coeffs="
            f"[A={float(GE_coeffs[0]):.6f}, "
            f"p={float(GE_coeffs[1]):.6f}]"
        )
        print(
            "The initial loss is recomputed because the experimental dataset "
            "and therefore the objective may have changed."
        )

    # A normal warm start resets Adam because the objective may have changed.
    # An exact crash checkpoint restores both optimizer moments below.
    first_moment = jnp.zeros_like(GE_coeffs)
    second_moment = jnp.zeros_like(GE_coeffs)
    if checkpoint is not None:
        first_moment = jnp.asarray(checkpoint["first_moment"], dtype=jnp.float64)
        second_moment = jnp.asarray(checkpoint["second_moment"], dtype=jnp.float64)
    beta1, beta2, epsilon = 0.9, 0.999, 1.0e-8

    print("Compiling the adjoint loss and digital twin with JAX; the first iteration may take several minutes.", flush=True)
    (
        initial_loss,
        initial_channel_losses,
    ), gradient = value_channels_and_grad(
        GE_coeffs,
    )
    gradient = projected_gradient(GE_coeffs, gradient)
    # EXP-versus-DT plots are intentionally deferred until all D-stages have
    # converged, so no trajectory comparison is shown during D0--D4.
    iteration_plots = []
    convergence_plot = ConvergencePlot() if SHOW_ITERATION_PLOT else None

    if checkpoint is None:
        iterations_history = [0]
        total_loss_history = [float(jax.device_get(initial_loss))]
        z_loss_history = [float(jax.device_get(initial_channel_losses[0]))]
        gradient_norm_history = [float(jax.device_get(jnp.linalg.norm(gradient)))]
        a1_history = [float(jax.device_get(GE_coeffs[0]))]
        a2_history = [float(jax.device_get(GE_coeffs[1]))]
        a3_history = [0.0]
    else:
        iterations_history = checkpoint["iteration_history"].astype(int).tolist()
        total_loss_history = checkpoint["total_loss_history"].astype(float).tolist()
        z_loss_history = checkpoint["z_loss_history"].astype(float).tolist()
        gradient_norm_history = checkpoint["gradient_norm_history"].astype(float).tolist()
        a1_history = checkpoint["a1_history"].astype(float).tolist()
        a2_history = checkpoint["a2_history"].astype(float).tolist()
        a3_history = checkpoint["a3_history"].astype(float).tolist()
    # Store the three static coefficients per iteration. The final DT signals are
    # recomputed once the user decides the actual final iteration count.
    coefficient_history = {
        int(iteration): jnp.asarray([a1, a2], dtype=jnp.float64)
        for iteration, a1, a2, a3 in zip(
            iterations_history, a1_history, a2_history, a3_history,
        )
    }

    current_iteration = resumed_iteration
    # There is deliberately no maximum number of iterations. The target is
    # extended block by block until the convergence window is satisfied.
    target_iteration = (
        int(OPTIMIZATION_BLOCK_ITERATIONS)
        if resumed_iteration == 0
        else int(checkpoint["target_iteration"].item())
        if "target_iteration" in checkpoint
        else resumed_iteration + OPTIMIZATION_BLOCK_ITERATIONS
    )
    stopping_reason = "running_until_convergence"
    convergence_diagnostics = {}

    if iteration_plots:
        _update_live_comparisons(
            iteration_plots,
            experiments,
            current_iteration,
            GE_coeffs,
            initial_loss,
            initial_channel_losses,
        )

    if convergence_plot is not None:
        convergence_plot.update(
            iterations_history,
            total_loss_history,
            z_loss_history,
            gradient_norm_history,
            a1_history,
            a2_history,
            a3_history,
        )

    print(
        f"iteration={current_iteration:04d} | "
        f"loss={float(jax.device_get(initial_loss)):.3e} | "
        f"loss_z={float(jax.device_get(initial_channel_losses[0])):.3e} | "
        "GE=["
        f"A={float(jax.device_get(GE_coeffs[0])):.3f}, "
        f"p={float(jax.device_get(GE_coeffs[1])):.3f}] | "
        f"gradient_norm={gradient_norm_history[-1]:.3e}"
    )

    def adjoint_adam_step(carry, iteration):
        coefficients, moment_1, moment_2, current_gradient = carry
        moment_1 = beta1 * moment_1 + (1.0 - beta1) * current_gradient
        moment_2 = beta2 * moment_2 + (1.0 - beta2) * current_gradient**2
        first_unbiased = moment_1 / (1.0 - beta1**iteration)
        second_unbiased = moment_2 / (1.0 - beta2**iteration)
        coefficients = coefficients - (
            LEARNING_RATE * first_unbiased / (jnp.sqrt(second_unbiased) + epsilon)
        )
        coefficients = project_GE_coeffs(coefficients)
        (loss_value, channel_values), next_gradient = value_channels_and_grad(
            coefficients
        )
        next_gradient = projected_gradient(coefficients, next_gradient)
        next_carry = (coefficients, moment_1, moment_2, next_gradient)
        output = (
            coefficients, moment_1, moment_2, loss_value,
            channel_values, next_gradient,
        )
        return next_carry, output

    compiled_adjoint_block = jax.jit(
        lambda carry, iteration_values: jax.lax.scan(
            adjoint_adam_step, carry, iteration_values
        )
    )

    while True:
        while current_iteration < target_iteration:
            block_end = min(
                current_iteration + (
                    ADJOINT_COMPILED_BLOCK_SIZE
                    if USE_COMPILED_ADJOINT_LOOP else 1
                ),
                target_iteration,
            )
            block_iterations = jnp.arange(current_iteration + 1, block_end + 1)
            initial_carry = (GE_coeffs, first_moment, second_moment, gradient)
            if USE_COMPILED_ADJOINT_LOOP:
                _, block_output = compiled_adjoint_block(
                    initial_carry, block_iterations
                )
            else:
                carry = initial_carry
                outputs = []
                for legacy_iteration in range(current_iteration + 1, block_end + 1):
                    carry, output = adjoint_adam_step(
                        carry, jnp.asarray(legacy_iteration)
                    )
                    outputs.append(output)
                block_output = tuple(
                    jnp.stack(items) for items in zip(*outputs)
                )

            (
                block_coefficients,
                block_first_moments,
                block_second_moments,
                block_losses,
                block_channel_losses,
                block_gradients,
            ) = tuple(np.asarray(jax.device_get(item)) for item in block_output)

            converged_inside_block = False
            for offset, iteration in enumerate(
                range(current_iteration + 1, block_end + 1)
            ):
                GE_coeffs = jnp.asarray(block_coefficients[offset])
                first_moment = jnp.asarray(block_first_moments[offset])
                second_moment = jnp.asarray(block_second_moments[offset])
                updated_loss = jnp.asarray(block_losses[offset])
                updated_channel_losses = jnp.asarray(block_channel_losses[offset])
                gradient = jnp.asarray(block_gradients[offset])
                gradient_norm = float(np.linalg.norm(block_gradients[offset]))

                iterations_history.append(iteration)
                total_loss_history.append(float(block_losses[offset]))
                z_loss_history.append(float(block_channel_losses[offset, 0]))
                gradient_norm_history.append(gradient_norm)
                a1_history.append(float(block_coefficients[offset, 0]))
                a2_history.append(float(block_coefficients[offset, 1]))
                a3_history.append(0.0)
                coefficient_history[iteration] = jnp.array(GE_coeffs)

                print(
                    f"iteration={iteration:04d} | "
                    f"loss={float(updated_loss):.3e} | "
                    f"loss_z={float(updated_channel_losses[0]):.3e} | "
                    f"GE=[A={float(GE_coeffs[0]):.3f}, "
                    f"p={float(GE_coeffs[1]):.3f}] | "
                    f"gradient_norm={gradient_norm:.3e}"
                )

                live_comparison_iterations = _comparison_iterations(target_iteration)
                if iteration_plots and iteration in live_comparison_iterations:
                    _update_live_comparisons(
                        iteration_plots, experiments, iteration, GE_coeffs,
                        updated_loss, updated_channel_losses,
                    )

                if (
                    convergence_plot is not None
                    and iteration % CONVERGENCE_PLOT_UPDATE_INTERVAL == 0
                ):
                    convergence_plot.update(
                        iterations_history, total_loss_history, z_loss_history,
                        gradient_norm_history,
                        a1_history, a2_history, a3_history,
                    )

                current_iteration = iteration
                if iteration % CHECKPOINT_INTERVAL == 0:
                    _save_checkpoint(
                        experiments, iteration, target_iteration, GE_coeffs,
                        first_moment, second_moment, initial_GE_coeffs,
                        iterations_history, total_loss_history, z_loss_history,
                        gradient_norm_history,
                        a1_history, a2_history, a3_history,
                    )
                converged, diagnostics = _windowed_convergence_status(
                    iterations_history, total_loss_history, gradient_norm_history,
                    a1_history, a2_history, a3_history,
                )
                if diagnostics:
                    convergence_diagnostics = diagnostics
                if converged:
                    stopping_reason = "automatic_windowed_convergence"
                    print(
                        "Automatic convergence reached at iteration "
                        f"{iteration}: relative loss range="
                        f"{diagnostics['relative_loss_range']:.3e}, "
                        "max coefficient range="
                        f"{diagnostics['max_coefficient_range']:.3e}, "
                        "max gradient norm="
                        f"{diagnostics['max_gradient_norm']:.3e}."
                    )
                    converged_inside_block = True
                    break

            if converged_inside_block:
                break

        if stopping_reason == "automatic_windowed_convergence":
            break
        current_iteration = target_iteration
        target_iteration += OPTIMIZATION_BLOCK_ITERATIONS
        print(
            f"Optimization extended to iteration {target_iteration}. "
            "Adam state is preserved; execution continues automatically until "
            "the convergence criterion is satisfied."
        )

    if convergence_plot is None:
        # Batch mode suppresses live windows, but still saves the final plot.
        convergence_plot = ConvergencePlot()
    if convergence_plot is not None:
        # Ensure that an automatic stop between display intervals is visible
        # and that the saved figure always contains the final iteration.
        convergence_plot.update(
            iterations_history,
            total_loss_history,
            z_loss_history,
            gradient_norm_history,
            a1_history,
            a2_history,
            a3_history,
        )
        convergence_plot.save_final(
            IDENTIFICATION_OUTPUT_DIR / FINAL_CONVERGENCE_PLOT_NAME
        )

    selected_iterations = tuple()
    comparison_data = {
        "coefficients": jnp.empty((0, 2), dtype=jnp.float64),
        "x": jnp.empty((0,), dtype=jnp.float64),
        "exp_z_norm": jnp.empty((0,), dtype=jnp.float64),
        "dt_z_norm": jnp.empty((0, 0), dtype=jnp.float64),
        "obstacle_start_x": jnp.asarray(OBSTACLE_X_START, dtype=jnp.float64),
        "obstacle_end_x": jnp.asarray(OBSTACLE_X_END, dtype=jnp.float64),
    }

    history = {
        "initial_GE_coeffs": initial_GE_coeffs,
        "initialization_label": initialization_label,
        "warm_start_used": jnp.asarray(warm_start_used),
        "previous_objective_loss": jnp.asarray(
            np.nan if previous_loss is None else previous_loss,
            dtype=jnp.float64,
        ),
        "iteration": jnp.asarray(iterations_history, dtype=jnp.int32),
        "total_loss": jnp.asarray(total_loss_history, dtype=jnp.float64),
        "z_loss": jnp.asarray(z_loss_history, dtype=jnp.float64),
        "gradient_norm": jnp.asarray(
            gradient_norm_history,
            dtype=jnp.float64,
        ),
        "a1_history": jnp.asarray(a1_history, dtype=jnp.float64),
        "a2_history": jnp.asarray(a2_history, dtype=jnp.float64),
        "a3_history": jnp.asarray(a3_history, dtype=jnp.float64),
        "stopping_reason": stopping_reason,
        "convergence_diagnostics": convergence_diagnostics,
        "comparison_iterations": jnp.asarray(
            selected_iterations,
            dtype=jnp.int32,
        ),
        "comparison_coefficients": comparison_data["coefficients"],
        "comparison_x": comparison_data["x"],
        "comparison_exp_z_norm": comparison_data["exp_z_norm"],
        "comparison_dt_z_norm": comparison_data["dt_z_norm"],
        "comparison_obstacle_start_x": comparison_data["obstacle_start_x"],
        "comparison_obstacle_end_x": comparison_data["obstacle_end_x"],
    }

    return (
        GE_coeffs,
        total_loss(GE_coeffs, experiments),
        mean_channel_losses(GE_coeffs, experiments),
        history,
    )



def export_identification_results(
    GE_coeffs: jnp.ndarray,
    loss: jnp.ndarray,
    channel_losses: jnp.ndarray,
    experiments: tuple[Experiment, ...],
    history: dict[str, jnp.ndarray],
) -> None:
    """Save coefficients, local Hessian/covariance and propagated GE uncertainty."""
    import numpy as np

    IDENTIFICATION_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    hessian = jax.hessian(total_loss)(GE_coeffs, experiments)
    hessian = 0.5 * (hessian + hessian.T)
    eigenvalues, eigenvectors = jnp.linalg.eigh(hessian)
    regularized_eigenvalues = jnp.maximum(eigenvalues, HESSIAN_REGULARIZATION)
    hessian_regularized = (
        eigenvectors
        @ jnp.diag(regularized_eigenvalues)
        @ eigenvectors.T
    )

    # The inverse Hessian gives the local shape of the parameter uncertainty.
    # Scaling by the final normalized residual keeps the magnitude tied to the fit.
    covariance = jnp.maximum(loss, 1.0e-12) * jnp.linalg.inv(hessian_regularized)
    coefficient_sigma = jnp.sqrt(jnp.maximum(jnp.diag(covariance), 0.0))
    zero_compatible = jnp.abs(GE_coeffs) <= 2.0 * coefficient_sigma
    negligible_contribution = jnp.asarray(
        [jnp.abs(GE_coeffs[0]) <= 0.01, False], dtype=bool
    )

    npz_path = IDENTIFICATION_OUTPUT_DIR / "adjoint_results.npz"
    np.savez(
        npz_path,
        GE_coeffs=np.asarray(jax.device_get(GE_coeffs), dtype=float),
        initial_GE_coeffs=np.asarray(
            jax.device_get(history["initial_GE_coeffs"]),
            dtype=float,
        ),
        warm_start_used=np.asarray(
            bool(jax.device_get(history["warm_start_used"]))
        ),
        previous_objective_loss=np.asarray(
            float(jax.device_get(history["previous_objective_loss"]))
        ),
        GE_hessian=np.asarray(jax.device_get(hessian), dtype=float),
        GE_covariance=np.asarray(jax.device_get(covariance), dtype=float),
        coefficient_sigma=np.asarray(jax.device_get(coefficient_sigma), dtype=float),
        zero_compatible_2sigma=np.asarray(jax.device_get(zero_compatible), dtype=bool),
        negligible_max_contribution=np.asarray(jax.device_get(negligible_contribution), dtype=bool),
        final_loss=np.asarray(float(jax.device_get(loss))),
        channel_losses=np.asarray(jax.device_get(channel_losses), dtype=float),
        iteration_history=np.asarray(jax.device_get(history["iteration"]), dtype=int),
        total_loss_history=np.asarray(jax.device_get(history["total_loss"]), dtype=float),
        z_loss_history=np.asarray(jax.device_get(history["z_loss"]), dtype=float),
        gradient_norm_history=np.asarray(jax.device_get(history["gradient_norm"]), dtype=float),
        stopping_reason=np.asarray(history["stopping_reason"]),
        convergence_relative_loss_range=np.asarray(
            history["convergence_diagnostics"].get("relative_loss_range", np.nan)
        ),
        convergence_coefficient_ranges=np.asarray(
            history["convergence_diagnostics"].get(
                "coefficient_ranges", [np.nan, np.nan, np.nan]
            ),
            dtype=float,
        ),
        convergence_max_gradient_norm=np.asarray(
            history["convergence_diagnostics"].get("max_gradient_norm", np.nan)
        ),
        a1_history=np.asarray(jax.device_get(history["a1_history"]), dtype=float),
        a2_history=np.asarray(jax.device_get(history["a2_history"]), dtype=float),
        a3_history=np.asarray(jax.device_get(history["a3_history"]), dtype=float),
        comparison_iterations=np.asarray(jax.device_get(history["comparison_iterations"]), dtype=int),
        comparison_coefficients=np.asarray(jax.device_get(history["comparison_coefficients"]), dtype=float),
        comparison_x=np.asarray(jax.device_get(history["comparison_x"]), dtype=float),
        comparison_exp_z_norm=np.asarray(jax.device_get(history["comparison_exp_z_norm"]), dtype=float),
        comparison_dt_z_norm=np.asarray(jax.device_get(history["comparison_dt_z_norm"]), dtype=float),
        comparison_obstacle_start_x=np.asarray(float(jax.device_get(history["comparison_obstacle_start_x"]))),
        comparison_obstacle_end_x=np.asarray(float(jax.device_get(history["comparison_obstacle_end_x"]))),
        fit_x_start=np.asarray(FIT_X_START, dtype=float),
        fit_x_end=np.asarray(FIT_X_END, dtype=float),
        included_cases=np.asarray(sorted(INCLUDED_CASES), dtype="U32"),
    )

    metadata = {
        "GE_coeffs": np.asarray(jax.device_get(GE_coeffs), dtype=float).tolist(),
        "initial_GE_coeffs": np.asarray(
            jax.device_get(history["initial_GE_coeffs"]),
            dtype=float,
        ).tolist(),
        "warm_start_used": bool(jax.device_get(history["warm_start_used"])),
        "previous_objective_loss": (
            None
            if np.isnan(float(jax.device_get(history["previous_objective_loss"])))
            else float(jax.device_get(history["previous_objective_loss"]))
        ),
        "optimizer_moments_restarted": True,
        "optimizer_method": "ADAM",
        "stopping_reason": history["stopping_reason"],
        "convergence_settings": {
            "maximum_iterations": None,
            "execution": "automatic blocks until windowed convergence",
            "minimum_iterations": CONVERGENCE_MIN_ITERATIONS,
            "window": CONVERGENCE_WINDOW,
            "relative_loss_range_tolerance": CONVERGENCE_RELATIVE_LOSS_RANGE,
            "coefficient_range_tolerance": CONVERGENCE_COEFFICIENT_RANGE,
            "gradient_norm_tolerance": CONVERGENCE_GRADIENT_NORM,
        },
        "convergence_diagnostics": history["convergence_diagnostics"],
        "final_loss": float(jax.device_get(loss)),
        "channel_losses": np.asarray(jax.device_get(channel_losses), dtype=float).tolist(),
        "channel_loss_order": ["z_error"],
        "identified_outputs": ["z_error"],
        "outputs_not_in_loss": ["vz", "Tcmd", "episode_reward"],
        "post_identification": True,
        "post_run_label": POST_RUN_LABEL,
        "initialization_mode": history["initialization_label"],
        "original_identification_directory": str(ORIGINAL_IDENTIFICATION_DIR),
        "included_cases": sorted(INCLUDED_CASES),
        "loss_normalization": "common physical scale R; equal mean weight per experiment",
        "loss_spatial_interval_m": [float(FIT_X_START), float(FIT_X_END)],
        "simulation_duration_factor": SIMULATION_DURATION_FACTOR,
        "experimental_vx_replay": (
            "clean vx(x) is retained for trajectory alignment; the DT "
            "horizontal state and controller remain autonomous"
        ),
        "ground_effect_model": (
            "f_GE=1+A*(R/h)^p"
        ),
        "GE_parameter_order": ["A", "p"],
        "GE_parameter_constraints": {
            "A": "free sign, constrained only by minimum f_GE",
            "p": [P_MIN, P_MAX],
            "minimum_f_GE": MIN_F_GE,
            "minimum_model_clearance_R": MIN_MODEL_CLEARANCE_R,
        },
        "coefficient_sigma": np.asarray(jax.device_get(coefficient_sigma), dtype=float).tolist(),
        "zero_compatible_2sigma": np.asarray(jax.device_get(zero_compatible), dtype=bool).tolist(),
        "negligible_max_contribution": np.asarray(jax.device_get(negligible_contribution), dtype=bool).tolist(),
        "pruning_rule": "assess A and p from their two-parameter covariance and predictive validation",
        "hessian_eigenvalues": np.asarray(jax.device_get(eigenvalues), dtype=float).tolist(),
        "hessian_regularization": HESSIAN_REGULARIZATION,
        "uncertainty_definition": "local inverse-Hessian covariance propagated to f_GE(h)",
        "number_of_experiments": len(experiments),
        "number_of_pid_experiments": sum(
            experiment.CONTROL_MODE == 0 for experiment in experiments
        ),
        "number_of_feedforward_experiments": sum(
            experiment.CONTROL_MODE == 1 for experiment in experiments
        ),
        "number_of_reference_governor_experiments": sum(
            experiment.CONTROL_MODE == 2 for experiment in experiments
        ),
        "feedforward_handling": "measured applied PWM offset replayed versus simulated x",
        "reference_governor_handling": (
            "recorded delta_z_ref(x) replayed unchanged inside the DT controller; "
            "the governor is not re-optimized during identification"
        ),
        "optimization_iterations": int(jax.device_get(history["iteration"][-1])),
        "comparison_snapshot_iterations": np.asarray(jax.device_get(history["comparison_iterations"]), dtype=int).tolist(),
        "height_grid_definition": "h_grid_R and h_grid_rotor_R denote physical propeller-plane clearance divided by R",
    }
    (IDENTIFICATION_OUTPUT_DIR / "adjoint_results.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    archive_dir = create_numbered_directory(
        IDENTIFICATION_OUTPUT_DIR / "history",
        "iteration",
    )
    results_dir = archive_dir / "results"
    clean_dir = archive_dir / "clean_inputs"
    raw_dir = archive_dir / "raw_inputs"
    code_dir = archive_dir / "code_snapshot"

    archived_results = copy_existing(
        IDENTIFICATION_OUTPUT_DIR.glob("adjoint_*"),
        results_dir,
    )
    clean_inputs = []
    raw_inputs = []
    for experiment in experiments:
        prefix = f"EXP_{experiment.CASE_NAME}"
        selected_clean = [
            EXP_DIR / f"{prefix}_clean.txt",
            EXP_DIR / f"{prefix}_metadata.json",
        ]
        if experiment.CONTROL_MODE == 1:
            selected_clean.append(EXP_DIR / f"{prefix}_FF_input.txt")
        elif experiment.CONTROL_MODE == 2:
            selected_clean.append(EXP_DIR / f"{prefix}_RG_input.txt")
        clean_inputs.extend(copy_existing(selected_clean, clean_dir))
        raw_inputs.extend(copy_existing(EXP_DIR.parent.glob(f"{prefix}_*.txt"), raw_dir))
        raw_inputs.extend(copy_existing([EXP_DIR.parent / f"{prefix}_metadata.json"], raw_dir))

    project_root = Path(__file__).resolve().parent
    code_paths = [
        project_root / "adjoint_identification.py",
        project_root / "design_next_experiment.py",
        project_root / "next_mission_design" / "informative_policy.py",
        project_root / "next_mission_design" / "model_based_policy.py",
        project_root / "pp_EXP.py",
        project_root / "run_next_experiment.py",
        project_root / "jDT" / "params.py",
        project_root / "jDT" / "postprocessing.py",
        project_root / "jDT" / "GE_correction.py",
        project_root / "jDT" / "controller.py",
        project_root / "jDT" / "simulator.py",
        project_root / "jDT" / "main.py",
    ]
    code_snapshot = copy_existing(code_paths, code_dir)
    archive_manifest = {
        **metadata,
        "iteration": archive_dir.name,
        "archived_at": timestamp_label(),
        "archived_results": archived_results,
        "clean_inputs": clean_inputs,
        "raw_inputs": raw_inputs,
        "code_snapshot": code_snapshot,
    }
    (archive_dir / "iteration_manifest.json").write_text(
        json.dumps(archive_manifest, indent=2),
        encoding="utf-8",
    )

    print(f"Identification results saved: {npz_path}")
    print(f"Complete identification iteration archived: {archive_dir}")


def save_D_stage_comparisons(
    experiments: tuple[Experiment, ...],
    stage_coefficients: dict[str, jnp.ndarray],
    *,
    output_root: Path = IDENTIFICATION_OUTPUT_ROOT,
    comparison_name: str = STAGE_COMPARISON_NAME,
) -> None:
    """Plot EXP once and the requested final DT coefficient snapshots."""
    import matplotlib.pyplot as plt

    _configure_matplotlib(plt)
    output_dir = output_root / f"final_{comparison_name}_comparisons"
    output_dir.mkdir(parents=True, exist_ok=True)
    colors = {
        "D0": "#4D4D4D", "D1": "#7B2CBF", "D2": "#F28E2B",
        "D3": "#2A9D8F", "D4": "#D62728",
    }
    styles = {"D0": (0, (1, 1)), "D1": ":", "D2": "-.", "D3": "--", "D4": "-"}

    for experiment in experiments:
        x_plot = np.asarray(jax.device_get(experiment.x), dtype=float)
        exp_z_R = np.asarray(jax.device_get(
            experiment.z_error
            + experiment.HEIGHT_IN_ROTOR_RADII * ROTOR_RADIUS
        ), dtype=float) / ROTOR_RADIUS
        figure, axis = plt.subplots(figsize=(5.25, 3.35), constrained_layout=True)
        axis.plot(x_plot, exp_z_R, color="black", linewidth=1.35,
                  label="EXP", zorder=6)
        for stage, coefficients in stage_coefficients.items():
            signal = simulate_aligned(
                coefficients, experiment, absolute_clearance=True
            ) / ROTOR_RADIUS
            host = np.asarray(jax.device_get(coefficients), dtype=float)
            axis.plot(
                x_plot,
                np.asarray(jax.device_get(signal), dtype=float),
                color=colors.get(stage, "#D62728"),
                linestyle=styles.get(stage, "-"),
                linewidth=1.65 if stage in {"D4", "cold start"} else 1.30,
                label=rf"DT {stage} ($A={host[0]:.3f}$, $p={host[1]:.3f}$)",
                zorder=5 if stage in {"D4", "cold start"} else 3,
            )
        _style_axis(axis, r"$z/R$ [-]", show_xlabel=True)
        axis.set_ylim(-2.0, 6.5)
        axis.axvspan(OBSTACLE_X_START, OBSTACLE_X_END,
                    color="0.92", zorder=0)
        axis.legend(frameon=False, fontsize=7.2)
        output_path = output_dir / (
            f"EXP_{experiment.CASE_NAME}_{comparison_name}.pdf"
        )
        figure.savefig(output_path, bbox_inches="tight")
        if SHOW_ITERATION_PLOT:
            plt.show(block=False)
        else:
            plt.close(figure)
        print(f"Final {comparison_name} comparison saved: {output_path}")


def run_cold_start() -> None:
    """Fit the complete D4 dataset once from the selected fixed initialization."""
    global INCLUDED_CASES, IDENTIFICATION_OUTPUT_DIR, CHECKPOINT_PATH

    initialization = COLD_START_INITIALIZATION.strip().lower()
    if initialization == "cheeseman_bennett":
        initial_coefficients = CHEESEMAN_BENNETT_GE_COEFFS
        initialization_label = "Cheeseman--Bennett cold start [A=1/16, p=2]"
        output_root = COLD_START_CB_OUTPUT_ROOT
    elif initialization == "zero":
        initial_coefficients = ZERO_GE_COEFFS
        initialization_label = "zero cold start [A=0, p=0]"
        output_root = COLD_START_ZERO_OUTPUT_ROOT
    else:
        raise ValueError(
            "COLD_START_INITIALIZATION must be 'cheeseman_bennett' or 'zero'."
        )

    INCLUDED_CASES = set(FULL_IDENTIFICATION_CASES)
    IDENTIFICATION_OUTPUT_DIR = output_root
    CHECKPOINT_PATH = IDENTIFICATION_OUTPUT_DIR / "adjoint_checkpoint.npz"
    experiments = load_experiments(INCLUDED_CASES)

    print("\n" + "=" * 78)
    print(
        "COLD START: complete D4 dataset initialized from "
        f"{initialization_label}"
    )
    print("Included cases: " + ", ".join(sorted(INCLUDED_CASES)))
    coefficients, loss, channel_losses, history = optimize(
        experiments,
        initial_coefficients,
        initialization_label,
    )
    export_identification_results(
        coefficients, loss, channel_losses, experiments, history
    )
    if CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()
        print(f"Completed-run checkpoint removed: {CHECKPOINT_PATH}")

    summary = {
        "run_mode": "cold_start",
        "cold_start_initialization": initialization,
        "included_cases": sorted(INCLUDED_CASES),
        "initial_coefficients": np.asarray(
            jax.device_get(initial_coefficients), dtype=float
        ).tolist(),
        "GE_coeffs": np.asarray(jax.device_get(coefficients), dtype=float).tolist(),
        "final_loss": float(jax.device_get(loss)),
        "iterations": int(jax.device_get(history["iteration"][-1])),
        "stopping_reason": history["stopping_reason"],
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "cold_start_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    save_D_stage_comparisons(
        experiments,
        {"cold start": jnp.array(coefficients)},
        output_root=output_root,
        comparison_name="cold_start",
    )
    print(
        "Cold-start identification complete: "
        f"A={float(coefficients[0]):.6f}, p={float(coefficients[1]):.6f}, "
        f"loss={float(loss):.6e}"
    )


def main() -> None:
    global INCLUDED_CASES, IDENTIFICATION_OUTPUT_DIR, CHECKPOINT_PATH

    run_mode = RUN_MODE.strip().lower()
    if run_mode == "cold_start":
        run_cold_start()
        if SHOW_ITERATION_PLOT:
            import matplotlib.pyplot as plt

            plt.ioff()
            plt.show()
        return
    if run_mode == "warm_start":
        identification_batches = SEQUENTIAL_IDENTIFICATION_BATCHES
        base_cases = set()
    else:
        raise ValueError(
            "RUN_MODE must be 'warm_start' or 'cold_start'."
        )

    cumulative_cases = set(base_cases)
    stage_coefficients = {}
    stage_summary = {}
    initial_coefficients = CHEESEMAN_BENNETT_GE_COEFFS
    final_experiments = None
    stage_names = list(identification_batches)
    resume_stage = WARM_START_RESUME_FROM_STAGE

    if resume_stage is None:
        stages_to_run = stage_names
    else:
        resume_stage = str(resume_stage).strip().upper()
        if resume_stage not in stage_names:
            raise ValueError(
                "WARM_START_RESUME_FROM_STAGE must be None or one of "
                f"{stage_names}."
            )
        resume_index = stage_names.index(resume_stage)
        existing_summary_path = IDENTIFICATION_OUTPUT_ROOT / STAGE_SUMMARY_FILENAME
        existing_summary = (
            json.loads(existing_summary_path.read_text(encoding="utf-8"))
            if existing_summary_path.exists() else {}
        )
        for completed_stage in stage_names[:resume_index + 1]:
            cumulative_cases.update(identification_batches[completed_stage])
            result_path = (
                IDENTIFICATION_OUTPUT_ROOT
                / completed_stage
                / "adjoint_results.npz"
            )
            if not result_path.exists():
                raise FileNotFoundError(
                    f"Cannot resume after {resume_stage}: missing {result_path}"
                )
            with np.load(result_path, allow_pickle=False) as result:
                completed_coefficients = np.asarray(
                    result["GE_coeffs"], dtype=float
                )
                completed_loss = float(result["final_loss"])
                completed_iterations = int(result["iteration_history"][-1])
                completed_stopping_reason = str(result["stopping_reason"].item())
            stage_coefficients[completed_stage] = jnp.asarray(
                completed_coefficients, dtype=jnp.float64
            )
            stage_summary[completed_stage] = existing_summary.get(
                completed_stage,
                {
                    "included_cases": sorted(cumulative_cases),
                    "GE_coeffs": completed_coefficients.tolist(),
                    "final_loss": completed_loss,
                    "iterations": completed_iterations,
                    "stopping_reason": completed_stopping_reason,
                },
            )
        initial_coefficients = jnp.array(stage_coefficients[resume_stage])
        stages_to_run = stage_names[resume_index + 1:]
        print(
            f"Warm sequence resumed after {resume_stage}: "
            f"A={float(initial_coefficients[0]):.6f}, "
            f"p={float(initial_coefficients[1]):.6f}. "
            f"Stages to run: {stages_to_run}"
        )
        if not stages_to_run:
            raise ValueError(
                f"No stage remains after {resume_stage}. Choose an earlier stage."
            )

    for stage in stages_to_run:
        added_cases = identification_batches[stage]
        cumulative_cases.update(added_cases)
        INCLUDED_CASES = set(cumulative_cases)
        IDENTIFICATION_OUTPUT_DIR = IDENTIFICATION_OUTPUT_ROOT / stage
        CHECKPOINT_PATH = IDENTIFICATION_OUTPUT_DIR / "adjoint_checkpoint.npz"
        experiments = load_experiments(INCLUDED_CASES)
        final_experiments = experiments

        print("\n" + "=" * 78)
        print(
            f"{stage}: cumulative identification with {len(experiments)} experiments"
        )
        print("Included cases: " + ", ".join(sorted(INCLUDED_CASES)))
        for experiment in experiments:
            mode = _control_mode_label(experiment.CONTROL_MODE)
            print(
                f"  {experiment.CASE_NAME}, "
                f"vx={experiment.HORIZONTAL_VELOCITY:.2f} m/s, "
                f"h={experiment.HEIGHT_IN_ROTOR_RADII:g}R, mode={mode}"
            )

        initialization_label = (
            "Cheeseman--Bennett [A=1/16, p=2]"
            if stage == stage_names[0]
            else f"converged {list(stage_coefficients)[-1]}"
        )
        coefficients, loss, channel_losses, history = optimize(
            experiments,
            initial_coefficients,
            initialization_label,
        )
        export_identification_results(
            coefficients, loss, channel_losses, experiments, history
        )
        if CHECKPOINT_PATH.exists():
            CHECKPOINT_PATH.unlink()
            print(f"Completed-stage checkpoint removed: {CHECKPOINT_PATH}")

        stage_coefficients[stage] = jnp.array(coefficients)
        stage_summary[stage] = {
            "included_cases": sorted(INCLUDED_CASES),
            "added_cases": sorted(added_cases),
            "dataset_boundary": SEQUENTIAL_DATASET_BOUNDARIES.get(stage),
            "initial_coefficients": np.asarray(
                jax.device_get(initial_coefficients), dtype=float
            ).tolist(),
            "GE_coeffs": np.asarray(jax.device_get(coefficients), dtype=float).tolist(),
            "final_loss": float(jax.device_get(loss)),
            "iterations": int(jax.device_get(history["iteration"][-1])),
            "stopping_reason": history["stopping_reason"],
        }
        initial_coefficients = jnp.array(coefficients)
        print(
            f"{stage} converged: A={float(coefficients[0]):.6f}, "
            f"p={float(coefficients[1]):.6f}, loss={float(loss):.6e}"
        )

    if final_experiments is None:
        raise RuntimeError("No warm-start stage was configured.")

    IDENTIFICATION_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    (IDENTIFICATION_OUTPUT_ROOT / STAGE_SUMMARY_FILENAME).write_text(
        json.dumps(stage_summary, indent=2), encoding="utf-8"
    )
    comparison_coefficients = stage_coefficients
    if run_mode == "warm_start":
        comparison_coefficients = {
            dataset: stage_coefficients[episode]
            for episode, dataset in SEQUENTIAL_DATASET_BOUNDARIES.items()
            if episode in stage_coefficients
        }
    save_D_stage_comparisons(final_experiments, comparison_coefficients)

    print(f"\n{stage_names[0]}--{stage_names[-1]} identification complete.")
    for stage, values in stage_summary.items():
        print(
            f"  {stage}: A={values['GE_coeffs'][0]:.6f}, "
            f"p={values['GE_coeffs'][1]:.6f}, "
            f"iterations={values['iterations']}"
        )

    if SHOW_ITERATION_PLOT:
        import matplotlib.pyplot as plt

        plt.ioff()
        plt.show()


if __name__ == "__main__":
    main()



