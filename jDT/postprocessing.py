"""Compact numerical post-processing for Digital-Twin episodes."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
import shutil
import jax
import jax.numpy as jnp
import numpy as np

from .params import OBSTACLE_X_END, OBSTACLE_X_START, ROTOR_RADIUS, X_ZOOM_END, X_ZOOM_START

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


REWARD_VERSION = "vertical_tracking_v1"


@dataclass(frozen=True)
class RewardSettings:
    """Weights used by the common experimental/DT tracking reward."""

    rms_weight: float = 1.0
    post_obstacle_weight: float = 1.0
    peak_weight: float = 0.25
    numerical_floor: float = 1.0e-12


DEFAULT_REWARD_SETTINGS = RewardSettings()


def timestamp_label() -> str:
    """Return the timestamp format used by reproducibility snapshots."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def copy_existing(paths, destination: str | Path) -> list[str]:
    """Copy existing files into a snapshot directory and return their names."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    copied = []
    for source in paths:
        source = Path(source)
        if not source.is_file():
            continue
        target = destination / source.name
        shutil.copy2(source, target)
        copied.append(target.name)
    return copied


def create_numbered_directory(parent: str | Path, prefix: str) -> Path:
    """Create the first available ``prefix_NNN`` directory."""
    parent = Path(parent)
    parent.mkdir(parents=True, exist_ok=True)
    index = 1
    while (parent / f"{prefix}_{index:03d}").exists():
        index += 1
    path = parent / f"{prefix}_{index:03d}"
    path.mkdir()
    return path


def create_timestamped_directory(parent: str | Path, prefix: str) -> Path:
    """Create a timestamped output directory without overwriting an existing one."""
    parent = Path(parent)
    parent.mkdir(parents=True, exist_ok=True)
    stem = f"{prefix}_{timestamp_label()}"
    path = parent / stem
    suffix = 1
    while path.exists():
        path = parent / f"{stem}_{suffix:02d}"
        suffix += 1
    path.mkdir()
    return path


def reward_settings_dict(settings: RewardSettings = DEFAULT_REWARD_SETTINGS):
    """Return a serializable description of the reward definition."""
    payload = asdict(settings)
    payload.update(
        version=REWARD_VERSION,
        obstacle_start_m=float(OBSTACLE_X_START),
        obstacle_end_m=float(OBSTACLE_X_END),
        scored_end_m=float(X_ZOOM_END),
        rotor_radius_m=float(ROTOR_RADIUS),
    )
    return payload


def vertical_performance_cost(
    x,
    z_error,
    settings: RewardSettings = DEFAULT_REWARD_SETTINGS,
):
    """Return the vertical-tracking cost and its three components."""
    x = jnp.asarray(x, dtype=jnp.float64)
    z_error_r = jnp.asarray(z_error, dtype=jnp.float64) / ROTOR_RADIUS
    scored = ((x >= OBSTACLE_X_START) & (x <= X_ZOOM_END)).astype(jnp.float64)
    post = ((x >= OBSTACLE_X_END) & (x <= X_ZOOM_END)).astype(jnp.float64)
    scored_count = jnp.maximum(jnp.sum(scored), 1.0)
    post_count = jnp.maximum(jnp.sum(post), 1.0)
    squared = z_error_r**2
    rms = jnp.sum(scored * squared) / scored_count
    post_rms = jnp.sum(post * squared) / post_count
    peak = jnp.max(jnp.where(scored > 0.0, squared, 0.0))
    components = jnp.asarray([rms, post_rms, peak], dtype=jnp.float64)
    total = (
        settings.rms_weight * rms
        + settings.post_obstacle_weight * post_rms
        + settings.peak_weight * peak
    )
    return total, components


def vertical_reward(x, z_error, settings: RewardSettings = DEFAULT_REWARD_SETTINGS):
    """Return the reward shared by experimental replay and virtual design."""
    cost, _ = vertical_performance_cost(x, z_error, settings)
    return -cost


def compute_metrics(data: dict) -> dict:
    """Return the tracking metrics of one virtual episode."""
    time = jnp.asarray(data["time"], dtype=jnp.float64)
    state = jnp.asarray(data["state"], dtype=jnp.float64)
    reference = jnp.asarray(data["reference"], dtype=jnp.float64)
    position_error = jnp.linalg.norm(state[:, :3] - reference[:, :3], axis=1)
    velocity_error = jnp.linalg.norm(state[:, 3:6] - reference[:, 3:6], axis=1)
    metrics = {
        "rmse_position": float(jax.device_get(jnp.sqrt(jnp.mean(position_error**2)))),
        "maximum_position_error": float(jax.device_get(jnp.max(position_error))),
        "final_position_error": float(jax.device_get(position_error[-1])),
        "rmse_velocity": float(jax.device_get(jnp.sqrt(jnp.mean(velocity_error**2)))),
        "duration": float(jax.device_get(time[-1] - time[0])),
        "crashed": bool(data.get("crashed", False)),
    }
    if metrics["crashed"]:
        metrics["crash_time"] = float(data.get("crash_time", jnp.nan))
    return metrics


def _output_value(value: float, decimals: int | None = None) -> str:
    text = f"{float(value):g}" if decimals is None else f"{float(value):.{decimals}f}"
    return text.replace("-", "m").replace(".", "p")


def _mission_suffix(config) -> str:
    velocity = getattr(config, "HORIZONTAL_VELOCITY", None)
    clearance = getattr(config, "HEIGHT_IN_ROTOR_RADII", None)
    if velocity is None or clearance is None:
        return ""
    return f"_{_output_value(velocity, 2)}ms_{_output_value(clearance)}R"


def save_forward_flight_txt(data: dict, output_dir: str | Path, config=None) -> Path | None:
    """Export the moving segment using the experimental log layout."""
    reference_velocity = np.asarray(data["reference"][:, 3:6], dtype=float)
    indices = np.flatnonzero(np.linalg.norm(reference_velocity, axis=1) > 1e-10)
    if indices.size == 0:
        return None
    i0, i1 = max(int(indices[0]) - 1, 0), min(int(indices[-1]) + 1, len(reference_velocity) - 1)
    sl = slice(i0, i1 + 1)
    time = np.asarray(data["time"][sl], dtype=float)
    state = np.asarray(data["state"][sl], dtype=float)
    reference = np.asarray(data["reference"][sl], dtype=float)
    euler = np.rad2deg(np.asarray(data["euler"][sl], dtype=float))
    euler[:, 1] *= -1.0
    rates = np.rad2deg(state[:, 10:13])
    rates[:, 1] *= -1.0
    acceleration = np.asarray(data.get("acceleration", np.zeros((len(data["time"]), 3)))[sl])
    motors = np.asarray(data.get("pwm", data.get("pwm_command"))[sl], dtype=float)
    collective = data.get("collective_pwm")
    thrust = np.asarray(collective[sl]) if collective is not None else np.mean(motors, axis=1)
    voltage = float("nan")
    if config is not None:
        voltage = float(np.interp(
            float(config.BATTERY_PERCENTAGE),
            np.asarray(config.BATTERY_SOC_LOOKUP),
            np.asarray(config.BATTERY_VOLTAGE_LOOKUP),
        ))
    output = np.column_stack((
        time, state[:, 0], reference[:, 0], state[:, 1], reference[:, 1],
        state[:, 2], reference[:, 2], state[:, 3], reference[:, 3],
        state[:, 4], reference[:, 4], state[:, 5], reference[:, 5],
        euler, rates, acceleration[:, 0], reference[:, 6],
        acceleration[:, 1], reference[:, 7], acceleration[:, 2], reference[:, 8],
        np.full_like(time, voltage), thrust, motors, state[:, 13:17],
    ))
    header = (
        "t x x_des y y_des z z_des vx vx_des vy vy_des vz vz_des "
        "roll pitch yaw roll_rate pitch_rate yaw_rate ax ax_des ay ay_des az az_des "
        "vbat thrust motor_m1 motor_m2 motor_m3 motor_m4 rpm_m1 rpm_m2 rpm_m3 rpm_m4"
    )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    label = getattr(config, "MISSION_LABEL", "DT") if config is not None else "DT"
    battery = int(round(getattr(config, "BATTERY_PERCENTAGE", 100.0)))
    path = output_dir / f"DT_{label}{_mission_suffix(config)}_{battery}_zoomed.txt"
    np.savetxt(path, output, fmt="%.6f", header=header, comments="")
    return path


def plot_signals(data: dict, output_dir=None) -> None:
    """Plot the normalized vertical tracking error over the paper domain."""
    if plt is None:
        return
    state = np.asarray(jax.device_get(data["state"]), dtype=float)
    reference = np.asarray(jax.device_get(data["reference"]), dtype=float)
    x = state[:, 0]
    mask = (x >= X_ZOOM_START) & (x <= X_ZOOM_END)
    if np.count_nonzero(mask) < 2:
        return
    x_over_r = (x[mask] - X_ZOOM_START) / ROTOR_RADIUS
    fig, ax = plt.subplots(figsize=(5.0, 3.0), constrained_layout=True)
    ax.plot(x_over_r, (state[mask, 2] - reference[mask, 2]) / ROTOR_RADIUS,
            color="tab:red", label="DT")
    ax.axvspan((OBSTACLE_X_START - X_ZOOM_START) / ROTOR_RADIUS,
               (OBSTACLE_X_END - X_ZOOM_START) / ROTOR_RADIUS,
               color="0.85", zorder=0)
    ax.set(xlabel=r"$x/R$", ylabel=r"$(z-z^*)/R$")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False)
    if output_dir is not None:
        fig.savefig(Path(output_dir) / "DT_vertical_response.pdf", bbox_inches="tight")


def run_postprocessing(data: dict, output_dir: str | Path, config=None,
                       show_figures: bool = True) -> dict:
    """Compute metrics, export the virtual log, and optionally plot the run."""
    metrics = compute_metrics(data)
    save_forward_flight_txt(data, output_dir, config=config)
    if show_figures:
        plot_signals(data, output_dir=output_dir)
    return metrics
