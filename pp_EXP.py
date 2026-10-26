# TAG U
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np
from scipy.signal import butter, filtfilt, medfilt

PROJECT_ROOT = Path(__file__).resolve().parent

from jDT import params
from jDT.propulsion import collective_command_to_thrust
from jDT.postprocessing import (
    REWARD_VERSION, reward_settings_dict, vertical_reward,
)


# -----------------------------------------------------------------------------
# Paper-oriented case names, for example ``["BL", "MB", "EI_09"]``.
# ``None`` processes every raw case currently retained in EXP.
MISSION_LIST = None
# -----------------------------------------------------------------------------



EXP_DIR = str(PROJECT_ROOT / "EXP")
CLEAN_DIR = str(PROJECT_ROOT / "EXP" / "CLEAN")

OBSTACLE_X_START = params.OBSTACLE_X_START
OBSTACLE_X_END = params.OBSTACLE_X_END
FF_X_START = params.FF_X_START
X_ZOOM_START = params.X_ZOOM_START
X_ZOOM_END = params.X_ZOOM_END
X_START = params.X_START
X_SPATIAL_STOP = params.X_SPATIAL_STOP
TABLE_HEIGHT = params.TABLE_HEIGHT_Z
LIGHTHOUSE_DECK_TO_PROP = params.LIGHTHOUSE_DECK_TO_PROP
ROTOR_RADIUS = params.ROTOR_RADIUS

MEDIAN_KERNEL = 5
LOWPASS_CUTOFF_HZ = 1.5
EXP_PATTERN = "EXP_*_*_zoomed.txt"

PAPER_CASE_ORDER = (
    *(f"INF_{index:02d}" for index in range(1, 13)),
    "BL", "INT_01", "INT_02", "MB",
    *(f"ALPHA_{index:02d}" for index in range(1, 8)),
    *(f"EI_{index:02d}" for index in range(1, 11)),
    "BL_V020_Z25", "MB_V020_Z25", "EI_TR_V020_Z25",
    "BL_V050_Z10", "MB_V050_Z10", "EI_TR_V050_Z10",
    "EI_01_V050_Z10", "EI_STAR_V050_Z10",
)
PAPER_CASE_INDEX = {name: index for index, name in enumerate(PAPER_CASE_ORDER)}


EXP_COLOR = "black"
EXP_LINEWIDTH = 1.20
GRID_ALPHA = 0.16
MINOR_GRID_ALPHA = 0.08
MINOR_GRID_LINEWIDTH = 0.40
NORMALIZED_TIME_TICKS = np.linspace(0.0, 1.0, 6)

_CLEAN_ARCHIVE_DIR = None

plt.rcParams.update({
    "text.usetex": False,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman", "CMU Serif", "DejaVu Serif"],
    "mathtext.fontset": "cm",
    "axes.labelsize": 10,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 6,
    "axes.linewidth": 0.8,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "axes.unicode_minus": False,
})


class OneDecimalScalarFormatter(ScalarFormatter):
    def _set_format(self):
        self.format = "%1.1f"
        if self._usetex or self._useMathText:
            self.format = r"$\mathdefault{%1.1f}$"


def style_axis(ax, ylabel, show_xlabel):
    ax.set_ylabel(ylabel)
    ax.set_xlabel(r"$\tau$" if show_xlabel else "")
    ax.set_xlim(0.0, 1.0)
    ax.set_xticks(NORMALIZED_TIME_TICKS)
    ax.tick_params(axis="x", which="major", bottom=True, top=True, labelbottom=True)
    ax.minorticks_on()
    ax.tick_params(axis="both", which="minor", bottom=False, top=False, left=False, right=False)
    ax.grid(True, which="major", alpha=GRID_ALPHA, linewidth=0.55)
    ax.grid(True, which="minor", alpha=MINOR_GRID_ALPHA, linewidth=MINOR_GRID_LINEWIDTH)
    formatter = OneDecimalScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((0, 0))
    formatter.set_useOffset(False)
    ax.yaxis.set_major_formatter(formatter)
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)


def collective_pwm_to_tcmd(pwm):
    return np.asarray(collective_command_to_thrust(pwm), dtype=float)


def load_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as stream:
        header = stream.readline().strip().split()
    data = np.loadtxt(file_path, skiprows=1)
    if data.ndim == 1:
        data = data[None, :]
    out = {name: np.asarray(data[:, i], dtype=float) for i, name in enumerate(header)}
    required = [
        "t", "x", "z", "z_des", "vx", "vz", "vz_des", "pitch", "thrust"
    ]
    for key in required:
        if key not in out:
            raise KeyError(f"Required column {key!r} missing in {file_path}")
    # A reference governor does not add a motor command.  stabilizer.thrust is
    # therefore already the complete collective command issued by the PID.
    out["tcmd"] = collective_pwm_to_tcmd(np.asarray(out["thrust"], dtype=float))
    return out


def parse_test_parameters(file_path):
    name = Path(file_path).name
    match = re.fullmatch(
        r"EXP_(?P<batch>[A-Z0-9_]+)_(?P<rep>[A-Z]+)_zoomed\.txt",
        name)
    if match is None:
        raise ValueError(f"Unable to extract paper case from filename: {name}")
    batch = match.group("batch")
    metadata_path = Path(file_path).with_name(f"EXP_{batch}_metadata.json")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    mode = str(metadata.get("control_mode", "")).upper()
    if mode not in {"PID", "RG"}:
        raise ValueError(f"{name} has unsupported control mode {mode!r}")
    vel = f"{float(metadata['horizontal_velocity']):.2f}ms".replace(".", "p")
    R = f"{float(metadata['height_in_rotor_radii']):g}R".replace(".", "p")
    return vel, R, batch, mode


def velocity_from_label(vel):
    return float(vel.replace("ms", "").replace("p", "."))


def radius_count(R):
    return float(R.replace("R", "").replace("p", "."))


def mission_is_selected(batch):
    """Return whether a paper-oriented case was explicitly selected."""
    if MISSION_LIST is None:
        return True
    selected = {
        str(value).strip().upper().removeprefix("EXP_")
        for value in MISSION_LIST
    }
    return batch.upper() in selected


def find_rg_files(exp_dir, vel, R, batch):
    if batch is None:
        return []
    pattern = os.path.join(exp_dir, f"EXP_{batch}_*_zoomed.txt")
    return sorted(Path(path) for path in glob.glob(pattern))


def discover_missions(exp_dir, requested_file=None):
    if requested_file is not None:
        requested = Path(requested_file)
        if not requested.exists():
            raise FileNotFoundError(f"RG file not found: {requested}")
        vel, R, batch, mode = parse_test_parameters(requested)
        if velocity_from_label(vel) > params.MAX_HORIZONTAL_VELOCITY + 1.0e-9:
            raise ValueError(
                f"Requested RG file has vx={velocity_from_label(vel):.2f} m/s, "
                f"above the configured maximum {params.MAX_HORIZONTAL_VELOCITY:.2f} m/s."
            )
        files = find_rg_files(exp_dir, vel, R, batch)
        return [(vel, R, batch, mode, files)]

    groups = {}
    for path_text in glob.glob(os.path.join(exp_dir, EXP_PATTERN)):
        path = Path(path_text)
        try:
            vel, R, batch, mode = parse_test_parameters(path)
        except ValueError:
            continue
        if velocity_from_label(vel) > params.MAX_HORIZONTAL_VELOCITY + 1.0e-9:
            continue
        if not mission_is_selected(batch):
            continue
        groups.setdefault((vel, R, batch, mode), []).append(path)
    return [
        (vel, R, batch, mode, sorted(files))
        for (vel, R, batch, mode), files in sorted(
            groups.items(),
            key=lambda item: (
                PAPER_CASE_INDEX.get(item[0][2], len(PAPER_CASE_INDEX)),
                item[0][2],
            ),
        )
    ]


def discover_existing_clean_results(excluded_batches=()):
    """Load selected clean-only missions whose raw repetitions are unavailable."""
    excluded = set(excluded_batches)
    results = []
    for clean_path in sorted(Path(CLEAN_DIR).glob("EXP_*_clean.txt")):
        match = re.fullmatch(
            r"EXP_(?P<batch>[A-Z0-9_]+)_clean\.txt",
            clean_path.name,
        )
        if match is None:
            continue
        batch = match.group("batch")
        if batch in excluded or not mission_is_selected(batch):
            continue
        metadata_path = Path(CLEAN_DIR) / f"EXP_{batch}_metadata.json"
        reward_path = Path(CLEAN_DIR) / f"EXP_{batch}_reward.json"
        metadata = (
            json.loads(metadata_path.read_text(encoding="utf-8"))
            if metadata_path.exists() else {}
        )
        reward_data = (
            json.loads(reward_path.read_text(encoding="utf-8"))
            if reward_path.exists() else {}
        )
        mode = str(metadata.get("control_mode", "RG")).upper()
        if mode not in {"PID", "RG"}:
            mode = "RG"
        reward = reward_data.get("mean_experimental_reward")
        results.append({
            "clean": load_clean_file(clean_path),
            "batch": batch,
            "mode": mode,
            "reward": None if reward is None else float(reward),
        })
        print(f"Loaded existing clean-only mission: {clean_path.name}")
    return results


def lowpass(signal, dt, cutoff=LOWPASS_CUTOFF_HZ):
    if signal.size < 10:
        raise ValueError("Signal too short for low-pass filtering.")
    fs = 1.0 / dt
    b, a = butter(3, cutoff / (0.5 * fs), btype="low")
    return filtfilt(b, a, signal)


def align_runs(runs):
    t_ref = np.asarray(runs[0]["t"], dtype=float)
    x_ref = np.asarray(runs[0]["x"], dtype=float)
    t_event_ref = t_ref[np.argmin(np.abs(x_ref - OBSTACLE_X_START))]
    aligned = []
    for run in runs:
        x = np.asarray(run["x"], dtype=float)
        t = np.asarray(run["t"], dtype=float)
        t_event = t[np.argmin(np.abs(x - OBSTACLE_X_START))]
        copy = {key: np.asarray(value, dtype=float).copy() for key, value in run.items()}
        copy["t"] = t - (t_event - t_event_ref)
        aligned.append(copy)
    return aligned


def average_runs(runs):
    aligned = align_runs(runs)
    t_ref = np.asarray(aligned[0]["t"], dtype=float)
    keys = ["x", "z", "z_des", "vx", "vz", "tcmd", "pitch"]
    pid_keys = [
        "pid_target_vz", "pid_z_p", "pid_z_i", "pid_z_d",
        "pid_vz_p", "pid_vz_i", "pid_vz_d", "pid_vz_ff",
    ]
    keys.extend(key for key in pid_keys if any(key in run for run in aligned))
    means = {
        key: np.mean(
            np.array([
                np.interp(t_ref, run["t"], run[key])
                for run in aligned if key in run
            ]),
            axis=0,
        )
        for key in keys
    }
    means["t"] = t_ref
    return means


def repetition_rms(clean_repetitions, mean_clean):
    """Compute pointwise RMS bands around the saved mean experiment."""
    t_ref = np.asarray(mean_clean["t"], dtype=float)
    rms = {"t": t_ref, "x": np.asarray(mean_clean["x"], dtype=float)}
    for key in ("z", "vx", "vz", "tcmd", "pitch"):
        aligned = np.asarray([
            np.interp(t_ref, repeat["t"], repeat[key])
            for repeat in clean_repetitions
        ])
        rms[key] = np.sqrt(np.mean((aligned - mean_clean[key][None, :]) ** 2, axis=0))
    return rms


def save_rms_file(batch, rms):
    """Save all repeatability bands needed by the paper plots."""
    path = Path(CLEAN_DIR) / f"EXP_{batch}_rms.txt"
    data = np.column_stack([
        rms["t"], rms["x"], rms["z"], rms["vx"], rms["vz"],
        rms["tcmd"], rms["pitch"],
    ])
    np.savetxt(
        path, data,
        header="t x z_rms vx_rms vz_rms Tcmd_collective_rms pitch_rms_deg",
    )
    print(f"Saved experimental RMS: {path}")
    return path


def clean_rg_run(run):
    t = np.asarray(run["t"], dtype=float)
    dt = float(np.median(np.diff(t)))
    clean = {
        "t": t,
        "x": np.asarray(run["x"], dtype=float),
        "z": lowpass(
            medfilt(
                np.asarray(run["z"], dtype=float)
                - TABLE_HEIGHT
                + LIGHTHOUSE_DECK_TO_PROP,
                MEDIAN_KERNEL,
            ),
            dt,
        ),
        "vx": lowpass(medfilt(np.asarray(run["vx"], dtype=float), MEDIAN_KERNEL), dt),
        "vz": lowpass(medfilt(np.asarray(run["vz"], dtype=float), MEDIAN_KERNEL), dt),
        "tcmd": lowpass(medfilt(np.asarray(run["tcmd"], dtype=float), MEDIAN_KERNEL), dt),
        "pitch": lowpass(
            medfilt(np.asarray(run["pitch"], dtype=float), MEDIAN_KERNEL), dt
        ),
        "z_des": lowpass(
            medfilt(np.asarray(run["z_des"], dtype=float), MEDIAN_KERNEL), dt
        ),
    }
    for key in [
        "pid_target_vz", "pid_z_p", "pid_z_i", "pid_z_d",
        "pid_vz_p", "pid_vz_i", "pid_vz_d", "pid_vz_ff",
    ]:
        if key in run:
            clean[key] = lowpass(
                medfilt(np.asarray(run[key], dtype=float), MEDIAN_KERNEL), dt
            )
    return clean


def batch_suffix(batch):
    return "" if batch is None else f"_{batch}"


def save_clean_file(vel, R, batch, clean, mode):
    os.makedirs(CLEAN_DIR, exist_ok=True)
    path = Path(CLEAN_DIR) / f"EXP_{batch}_clean.txt"
    pid_keys = [
        "pid_target_vz", "pid_z_p", "pid_z_i", "pid_z_d",
        "pid_vz_p", "pid_vz_i", "pid_vz_d", "pid_vz_ff",
    ]
    present_pid_keys = [key for key in pid_keys if key in clean]
    columns = [
        clean["t"], clean["x"], clean["z"], clean["vx"],
        clean["vz"], clean["tcmd"], clean["pitch"],
    ]
    header = [
        "t", "x", "z_clean", "vx_clean", "vz_clean",
        "Tcmd_collective_clean", "pitch_clean_deg",
    ]
    # Keep the established PID CLEAN format unchanged. RG needs the
    # additional varying reference column for policy replay.
    if mode == "RG":
        columns.append(clean["z_des"])
        header.append("z_ref_lighthouse_clean")
    columns.extend(clean[key] for key in present_pid_keys)
    header.extend(present_pid_keys)
    data = np.column_stack(columns)
    np.savetxt(
        path,
        data,
        header=" ".join(header),
    )
    metadata_source = Path(EXP_DIR) / f"EXP_{batch}_metadata.json"
    shutil.copy2(metadata_source, Path(CLEAN_DIR) / metadata_source.name)
    print(f"Saved: {path}")
    return path


def full_raw_path(zoomed_path):
    zoomed_path = Path(zoomed_path)
    if not zoomed_path.name.endswith("_zoomed.txt"):
        raise ValueError(f"Expected an RG zoomed file, received: {zoomed_path}")
    return zoomed_path.with_name(zoomed_path.name.removesuffix("_zoomed.txt") + ".txt")


def extract_reference_profile(zoomed_path):
    # The zoomed log starts with the controlled scientific passage. The full
    # raw log also contains takeoff and the transfer to point A; its first
    # visit to each x is therefore not the applied RG policy.
    raw = load_txt(zoomed_path)
    x = np.asarray(raw["x"], dtype=float)
    height_r = radius_count(parse_test_parameters(zoomed_path)[1])
    nominal_lighthouse_z = TABLE_HEIGHT + height_r * ROTOR_RADIUS - LIGHTHOUSE_DECK_TO_PROP
    ff = np.asarray(raw["z_des"], dtype=float) - nominal_lighthouse_z
    finite = np.isfinite(x) & np.isfinite(ff)
    x = x[finite]
    ff = ff[finite]
    in_mission = (x >= X_ZOOM_START) & (x <= X_ZOOM_END)
    x = x[in_mission]
    ff = ff[in_mission]
    if x.size < 2:
        raise ValueError(f"Insufficient RG profile samples in {zoomed_path}")

    # Keep the first forward passage through each x position. This removes
    # repeated stationary samples without mixing them with the braking phase.
    previous_max = np.maximum.accumulate(np.r_[-np.inf, x[:-1]])
    forward = x > previous_max + 1.0e-6
    x = x[forward]
    ff = ff[forward]
    if x.size < 2:
        raise ValueError(f"RG profile is not increasing in x: {zoomed_path}")

    return x, ff


def save_reference_profile(vel, R, batch, zoomed_paths):
    """Average the actually commanded z-reference profiles for DT replay."""
    profiles = [extract_reference_profile(path) for path in zoomed_paths]
    overlap_start = max(float(x[0]) for x, _ in profiles)
    overlap_end = min(float(x[-1]) for x, _ in profiles)
    x_ref = profiles[0][0]
    x_ref = x_ref[(x_ref >= overlap_start) & (x_ref <= overlap_end)]
    if x_ref.size < 2:
        raise ValueError("RG repetitions have no common increasing x interval.")
    ff = np.mean(
        np.array([np.interp(x_ref, x, values) for x, values in profiles]),
        axis=0,
    )
    if x_ref[0] > X_ZOOM_START + 1.0e-9:
        slope = (ff[1] - ff[0]) / (x_ref[1] - x_ref[0])
        first_ff = ff[0] + slope * (X_ZOOM_START - x_ref[0])
        x_ref = np.r_[X_ZOOM_START, x_ref]
        ff = np.r_[first_ff, ff]

    profile_path = Path(CLEAN_DIR) / f"EXP_{batch}_RG_input.txt"
    np.savetxt(
        profile_path,
        np.column_stack((x_ref, ff)),
        header="x delta_z_reference_m",
    )
    print(f"Saved DT reference-governor replay profile: {profile_path}")
    return profile_path


def load_clean_file(path):
    with open(path, "r", encoding="utf-8") as stream:
        header = stream.readline().strip().lstrip("#").split()
    data = np.loadtxt(path, skiprows=1)
    if data.ndim == 1:
        data = data[None, :]
    if data.shape[1] < 6:
        raise ValueError(
            f"Invalid clean file {path}: expected at least 6 columns. "
            "Run pp_EXP.py first."
        )
    command = np.asarray(data[:, 5], dtype=float)
    command_header = header[5].lower() if len(header) > 5 else "pwm_clean"
    if "tcmd" not in command_header and "thrust" not in command_header:
        command = collective_pwm_to_tcmd(command)
    return {
        "t": data[:, 0],
        "x": data[:, 1],
        "z": data[:, 2],
        "vx": data[:, 3],
        "vz": data[:, 4],
        "tcmd": command,
        "pitch": data[:, 6] if data.shape[1] >= 7 else None,
        "z_des": data[:, 7] if data.shape[1] >= 8 else None,
    }


def find_equivalent_pid_clean(vel, R):
    path = Path(CLEAN_DIR) / f"EXP_{vel}_{R}_clean.txt"
    return path if path.exists() else None


def normalized_time(t):
    t = np.asarray(t, dtype=float)
    return (t - t[0]) / max(float(t[-1] - t[0]), 1.0e-12)


def normalized_outputs(clean, n_radii, velocity):
    del n_radii, velocity
    # CLEAN z is already the propeller-plane clearance above the table.
    return (clean["z"] / ROTOR_RADIUS,)


def mission_plot_label(batch, mode, reward=None):
    metadata_path = Path(CLEAN_DIR) / f"EXP_{batch}_metadata.json"
    phase = ""
    if metadata_path.exists():
        phase = str(json.loads(metadata_path.read_text(encoding="utf-8")).get(
            "mission_phase", ""
        ))
    phase = phase or mode.lower()
    label = f"{batch} ({phase})"
    if reward is not None and np.isfinite(reward):
        label += rf", $\mathcal{{R}}^{{EXP}}={reward:.3f}$"
    return label


def plot_results(results):
    """Overlay every selected, averaged mission on one spatial plot."""
    fig, ax = plt.subplots(figsize=(4.5, 3.0), constrained_layout=True)
    colors = plt.cm.jet(np.linspace(0.08, 0.92, max(len(results), 2)))
    for color, item in zip(colors, results):
        clean, batch, mode = item["clean"], item["batch"], item["mode"]
        x = np.asarray(clean["x"])
        ax.plot(
            x, clean["z"] / ROTOR_RADIUS,
            color=color, linewidth=EXP_LINEWIDTH,
            label=mission_plot_label(batch, mode, item.get("reward")),
        )
        if clean.get("z_des") is not None:
            reference_height_r = (
                np.asarray(clean["z_des"]) + LIGHTHOUSE_DECK_TO_PROP - TABLE_HEIGHT
            ) / ROTOR_RADIUS
            ax.plot(x, reference_height_r, color=color, linestyle="--",
                    linewidth=0.85, alpha=0.65)
    ax.axvspan(OBSTACLE_X_START, OBSTACLE_X_END, color="0.92", zorder=0)
    for edge in (OBSTACLE_X_START, OBSTACLE_X_END):
        ax.axvline(edge, linestyle="--", color="black", linewidth=0.75, alpha=0.55)
    ax.set_xlabel(r"$x$ [m]")
    ax.set_ylabel(r"$z/R$")
    ax.set_xlim(X_ZOOM_START, X_ZOOM_END)
    ax.set_ylim(-2.0, 6.5)
    ax.minorticks_on()
    ax.grid(True, which="major", alpha=GRID_ALPHA, linewidth=0.55)
    ax.grid(True, which="minor", alpha=MINOR_GRID_ALPHA,
            linewidth=MINOR_GRID_LINEWIDTH)
    ax.legend(frameon=False, ncol=min(3, max(1, len(results))))
    plt.show()


def main():
    global _CLEAN_ARCHIVE_DIR
    _CLEAN_ARCHIVE_DIR = None
    Path(CLEAN_DIR).mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser(description="Average and clean repeated PID/RG experiments.")
    parser.add_argument("experiment_file", nargs="?", default=None)
    parser.add_argument(
        "--no-plot", action="store_true",
        help="Generate clean datasets without opening the summary figure.",
    )
    args = parser.parse_args()

    missions = discover_missions(EXP_DIR, args.experiment_file)
    plotted_results = []
    processed_batches = set()
    for vel, R, batch, mode, rg_files in missions:
        print(
            f"\nDetected {mode} mission: velocity={vel}, height={R}, "
            f"batch={batch or 'legacy'}"
        )
        print(f"Averaging {len(rg_files)} repetition(s):")
        for path in rg_files:
            print(f"  - {path.name}")

        rg_runs = [load_txt(path) for path in rg_files]
        imposed_velocity = velocity_from_label(vel)
        for path, run in zip(rg_files, rg_runs):
            vx_rms = float(np.sqrt(np.mean((run["vx"] - imposed_velocity) ** 2)))
            print(
                f"vx RMS | {path.name}: {vx_rms:.5f} m/s "
                f"({100.0 * vx_rms / imposed_velocity:.2f}% of imposed speed)"
            )

        rg_mean = average_runs(rg_runs)
        if mode == "PID":
            nominal_propeller_height = TABLE_HEIGHT + radius_count(R) * ROTOR_RADIUS
            expected_lighthouse_height = nominal_propeller_height - LIGHTHOUSE_DECK_TO_PROP
            incompatible = [
                path.name for path, run in zip(rg_files, rg_runs)
                if abs(float(np.median(run["z_des"])) - expected_lighthouse_height) > 1.0e-3
            ]
            if incompatible:
                raise ValueError(
                    "PID repetitions have a non-nominal z reference: "
                    f"{incompatible}"
                )
            # Preserve the established constant-height PID processing.
            rg_mean["z_des"] = np.full_like(rg_mean["z"], expected_lighthouse_height)
        rg_clean = clean_rg_run(rg_mean)
        clean_path = save_clean_file(vel, R, batch, rg_clean, mode)
        cleaned_repetitions = [clean_rg_run(run) for run in rg_runs]
        save_rms_file(batch, repetition_rms(cleaned_repetitions, rg_clean))
        if mode == "RG":
            save_reference_profile(vel, R, batch, rg_files)

        repetition_rewards = []
        for cleaned_repeat in cleaned_repetitions:
            reward = vertical_reward(
                cleaned_repeat["x"],
                cleaned_repeat["z"] - radius_count(R) * ROTOR_RADIUS,
            )
            repetition_rewards.append(float(reward))
        reward_path = clean_path.with_name(clean_path.stem.replace("_clean", "_reward") + ".json")
        reward_path.write_text(
            json.dumps({
                "reward_version": REWARD_VERSION,
                "settings": reward_settings_dict(),
                "repetition_rewards": repetition_rewards,
                "mean_experimental_reward": float(np.mean(repetition_rewards)),
                "standard_deviation": float(np.std(repetition_rewards)),
                "number_of_repetitions": len(repetition_rewards),
            }, indent=2),
            encoding="utf-8",
        )
        print(f"Saved experimental reward: {reward_path}")

        pid_path = find_equivalent_pid_clean(vel, R)
        if pid_path is None:
            print("Equivalent PID clean file not found. Plotting RG result only.")
        else:
            print(f"Equivalent PID clean file: {pid_path}")

        plotted_results.append({
            "clean": rg_clean,
            "batch": batch,
            "mode": mode,
            "reward": float(np.mean(repetition_rewards)),
        })
        processed_batches.add(batch)

    plotted_results.extend(discover_existing_clean_results(processed_batches))
    if not plotted_results:
        raise FileNotFoundError(
            f"No raw or clean mission matches MISSION_LIST={MISSION_LIST}."
        )
    if not args.no_plot:
        plot_results(plotted_results)


if __name__ == "__main__":
    main()



