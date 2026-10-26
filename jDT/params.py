# TAG V
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from jax import config as jax_config
import jax.numpy as jnp

jax_config.update("jax_enable_x64", True)


def configure_jax_runtime() -> Path:
    """Enable the persistent JAX compilation cache used by all workflows."""
    cache_dir = Path(__file__).resolve().parents[1] / ".jax_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    jax_config.update("jax_compilation_cache_dir", str(cache_dir))
    return cache_dir

# =============================================================================
# USER SETTINGS: standard validation run (python -m jDT.main)
# =============================================================================
HEIGHT_IN_ROTOR_RADII = 1.5
HORIZONTAL_VELOCITY = 0.35
MAX_HORIZONTAL_VELOCITY = 0.60
BATTERY_PERCENTAGE = 100.0
# Final sequential informative-phase identification (E12).
GE_COEFFS = jnp.array(
    [0.121002330940913, 1.98041643105715], dtype=jnp.float64,
)
SHOW_FIGURES = True
MASS = 0.03242  # [kg], complete vehicle measured on a precision scale
KT = 2.879933e-8
# Effective command-to-thrust slope calibrated from the measured mass and the
# pre-obstacle steady-hover collective command. The firmware platform value
# (0.12 N) is nominal and overestimates this vehicle's effective thrust by
# about 4.3%.
FIRMWARE_THRUST_MAX_PER_MOTOR = 0.1148

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXP_DIR = PROJECT_ROOT / "EXP" / "CLEAN"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

# =============================================================================
# MISSION CONSTANTS: normally not edited by the user
# =============================================================================
PRE_HOVER_TIME = 2.0
POST_HOVER_TIME = 2.0
MISSION_LABEL = "GE_PID_BL_identified"
PLOT_VIEW_PLANE = "xz"

FLIGHT_RANGE_X = 4.40
TABLE_LENGTH_X = 3.21 - 2.40
TABLE_HEIGHT_Z = 0.63
TABLE_WIDTH_Y = 1.0
# Vertical geometry for a level vehicle. Positive values point upward.
# The Lighthouse deck is 7 mm above the COM; the propeller plane is another
# 1.5 mm above the Lighthouse deck.
LIGHTHOUSE_DECK_TO_COM = 0.007
LIGHTHOUSE_DECK_TO_PROP = 0.0015
PROP_TO_COM = LIGHTHOUSE_DECK_TO_COM + LIGHTHOUSE_DECK_TO_PROP
ROTOR_RADIUS = 0.023

X_START = 0.20
OBSTACLE_X_START = 2.20
OBSTACLE_X_END = OBSTACLE_X_START + TABLE_LENGTH_X
# Spatial acceleration reaches the requested speed at x=0.90 m, leaving a
# longer settling section before the obstacle.
X_ACCEL_END = 1.10
# Keep 0.50 m of OGE data before the obstacle.
X_ZOOM_START = OBSTACLE_X_START - 0.50
# The interval X_ZOOM_START..FF_X_START is a PID-only OGE baseline.
FF_X_START = 2.00
# Keep the 2.30 m scientific window and leave 0.20 m for sharp deceleration.
X_ZOOM_END = 4.00
X_CONSTANT_END = X_ZOOM_END
X_END = FLIGHT_RANGE_X
# Spatial mission: references are generated from measured x instead of time.
USE_SPATIAL_TRAJECTORY = True
X_SPATIAL_DECEL_START = X_ZOOM_END
X_SPATIAL_STOP = 4.20
SPATIAL_MIN_FORWARD_SPEED = 0.05
SPATIAL_COMMAND_HZ = 50.0
SPATIAL_POSITION_LOG_PERIOD_MS = 20
SPATIAL_LOG_TIMEOUT = 0.35
SPATIAL_FINAL_HOLD_TIME = 0.50

SPATIAL_Y_KP = 1.0
SPATIAL_MAX_LATERAL_SPEED = 0.15

@dataclass
class CrazyflieConfig:
    # Physics: values follow the Richardson2025 Crazyflie2.1 model.
    DT: float = 0.002
    MASS: float = MASS
    GRAVITY: float = 9.81
    # Distance between opposite motors. For the X configuration this gives
    # 0.065/sqrt(2) ~= 0.046 m from the COM along each body-plane arm axis.
    MOTOR_DISTANCE: float = 0.065
    I_MATRIX: jnp.ndarray | None = None
    KT: float = KT
    KQ: float = 7.23850e-10
    FIRMWARE_THRUST_MAX_PER_MOTOR: float = FIRMWARE_THRUST_MAX_PER_MOTOR
    PWM_MIN: float = 0.0
    PWM_MAX: float = 65535.0
    CONTROLLER_THRUST_BASE: float = 36000.0
    CONTROLLER_THRUST_MIN: float = 20000.0

    # Battery / motors
    INCLUDE_BATTERY_CORRECTION: bool = True
    BATTERY_PERCENTAGE: float = 100.0
    BATTERY_SOC_LOOKUP: jnp.ndarray | None = None
    BATTERY_VOLTAGE_LOOKUP: jnp.ndarray | None = None
    BATTERY_VOLTAGE_REFERENCE: float = 4.20
    TAU_RPM: float = 0.02
    RPM_DOT_MAX: float = 2.0e5

    # Free-flight aerodynamics
    CD: jnp.ndarray | None = None
    AIR_DENSITY: float = 1.225

    # Controller gains [P, I, D]
    POS_X_PID: jnp.ndarray | None = None
    POS_Y_PID: jnp.ndarray | None = None
    POS_Z_PID: jnp.ndarray | None = None
    VEL_X_PID: jnp.ndarray | None = None
    VEL_Y_PID: jnp.ndarray | None = None
    VEL_Z_PID: jnp.ndarray | None = None
    ROLL_PID: jnp.ndarray | None = None
    PITCH_PID: jnp.ndarray | None = None
    YAW_PID: jnp.ndarray | None = None
    ROLL_RATE_PID: jnp.ndarray | None = None
    PITCH_RATE_PID: jnp.ndarray | None = None
    YAW_RATE_PID: jnp.ndarray | None = None

    # Geometry / plotting
    TABLE_HEIGHT_Z: float = TABLE_HEIGHT_Z
    TABLE_WIDTH_Y: float = TABLE_WIDTH_Y
    OBSTACLE_X_START: float = OBSTACLE_X_START
    OBSTACLE_X_END: float = OBSTACLE_X_END
    FF_X_START: float = FF_X_START
    BODY_LENGTH: float = 0.09 * 0.66
    BODY_WIDTH: float = 0.09 * 0.66
    BODY_HEIGHT: float = 0.015
    # X-layout motor coordinates are (+/-a,+/-a), with radial arm 0.046 m.
    ROTOR_SKETCH_ARM_XY: float = 0.5 * MOTOR_DISTANCE
    ROTOR_PLANE_Z_ABOVE_COM: float = PROP_TO_COM
    ROTOR_RADIUS: float = 0.023
    ARM_LENGTH: float = 0.5 * MOTOR_DISTANCE
    ROTOR_BODY_CLEARANCE: float = 0.010
    ROTOR_BODY_VERTICAL_CLEARANCE: float = 0.006
    SHOW_DRONE_BOUNDING_BOX: bool = False
    DRONE_BOUNDING_BOX_EXPANSION: float = 1.0
    PLOT_VIEW_PLANE: str = "xz"
    RPM_MIN: float = 0.0
    RPM_MAX: float = 22000.0
    RPM_COLORBAR_LEVELS: int = 64

    # Mission metadata / output naming
    FORWARD_FLIGHT_TIME: float = 6.0
    MISSION_LABEL: str = "FF"
    HORIZONTAL_VELOCITY: float | None = None
    HEIGHT_IN_ROTOR_RADII: float | None = None
    OBSTACLE_WORLD: object | None = None
    XY_VELOCITY_MODE: bool = False

    def __post_init__(self) -> None:
        self.I_MATRIX = (
            jnp.array([
                [16.57171, 0.830806, 0.718277],
                [0.830806, 16.55602, 1.800197],
                [0.718277, 1.800197, 29.26165],
            ], dtype=jnp.float64) * 1e-6
            if self.I_MATRIX is None
            else jnp.asarray(self.I_MATRIX, dtype=jnp.float64)
        )
        self.KF = self.KT
        self.KM = self.KQ
        self.CD = jnp.zeros(3, dtype=jnp.float64) if self.CD is None else jnp.asarray(self.CD, dtype=jnp.float64)
        self.BATTERY_SOC_LOOKUP = (
            jnp.array([0.0, 20.0, 50.0, 80.0, 100.0], dtype=jnp.float64)
            if self.BATTERY_SOC_LOOKUP is None
            else jnp.asarray(self.BATTERY_SOC_LOOKUP, dtype=jnp.float64)
        )
        self.BATTERY_VOLTAGE_LOOKUP = (
            jnp.array([3.30, 3.65, 3.85, 4.00, 4.20], dtype=jnp.float64)
            if self.BATTERY_VOLTAGE_LOOKUP is None
            else jnp.asarray(self.BATTERY_VOLTAGE_LOOKUP, dtype=jnp.float64)
        )

        self.POS_X_PID = jnp.array([2.0, 0.0, 0.0]) if self.POS_X_PID is None else jnp.asarray(self.POS_X_PID, dtype=jnp.float64)
        self.POS_Y_PID = jnp.array([2.0, 0.0, 0.0]) if self.POS_Y_PID is None else jnp.asarray(self.POS_Y_PID, dtype=jnp.float64)
        self.POS_Z_PID = jnp.array([2.0, 0.5, 0.0]) if self.POS_Z_PID is None else jnp.asarray(self.POS_Z_PID, dtype=jnp.float64)
        self.VEL_X_PID = jnp.array([25.0, 1.0, 0.0]) if self.VEL_X_PID is None else jnp.asarray(self.VEL_X_PID, dtype=jnp.float64)
        self.VEL_Y_PID = jnp.array([25.0, 1.0, 0.0]) if self.VEL_Y_PID is None else jnp.asarray(self.VEL_Y_PID, dtype=jnp.float64)
        self.VEL_Z_PID = jnp.array([25.0, 15.0, 0.0]) if self.VEL_Z_PID is None else jnp.asarray(self.VEL_Z_PID, dtype=jnp.float64)
        self.ROLL_PID = jnp.array([6.0, 3.0, 0.0]) if self.ROLL_PID is None else jnp.asarray(self.ROLL_PID, dtype=jnp.float64)
        self.PITCH_PID = jnp.array([6.0, 3.0, 0.0]) if self.PITCH_PID is None else jnp.asarray(self.PITCH_PID, dtype=jnp.float64)
        self.YAW_PID = jnp.array([6.0, 1.0, 0.35]) if self.YAW_PID is None else jnp.asarray(self.YAW_PID, dtype=jnp.float64)
        self.ROLL_RATE_PID = jnp.array([250.0, 500.0, 2.5]) if self.ROLL_RATE_PID is None else jnp.asarray(self.ROLL_RATE_PID, dtype=jnp.float64)
        self.PITCH_RATE_PID = jnp.array([250.0, 500.0, 2.5]) if self.PITCH_RATE_PID is None else jnp.asarray(self.PITCH_RATE_PID, dtype=jnp.float64)
        self.YAW_RATE_PID = jnp.array([120.0, 16.67, 0.0]) if self.YAW_RATE_PID is None else jnp.asarray(self.YAW_RATE_PID, dtype=jnp.float64)


def make_config(
    *,
    plot_plane: str = "xz",
    battery_percentage: float = 100.0,
    forward_flight_time: float = 6.0,
    mission_label: str = "FF",
    horizontal_velocity: float | None = None,
    height_in_rotor_radii: float | None = None,
    xy_velocity_mode: bool = False,
) -> CrazyflieConfig:
    return CrazyflieConfig(
        PLOT_VIEW_PLANE=plot_plane,
        BATTERY_PERCENTAGE=float(battery_percentage),
        FORWARD_FLIGHT_TIME=float(forward_flight_time),
        MISSION_LABEL=str(mission_label),
        HORIZONTAL_VELOCITY=None if horizontal_velocity is None else float(horizontal_velocity),
        HEIGHT_IN_ROTOR_RADII=None if height_in_rotor_radii is None else float(height_in_rotor_radii),
        XY_VELOCITY_MODE=bool(xy_velocity_mode),
    )
