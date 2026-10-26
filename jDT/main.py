"""Construction and execution of the differentiable Crazyflie Digital Twin."""
from __future__ import annotations

import jax
import jax.numpy as jnp

from .controller import CrazyfliePIDController
from .params import (
    BATTERY_PERCENTAGE,
    GE_COEFFS,
    HEIGHT_IN_ROTOR_RADII,
    HORIZONTAL_VELOCITY,
    MISSION_LABEL,
    OUTPUT_DIR,
    POST_HOVER_TIME,
    PRE_HOVER_TIME,
    PROP_TO_COM,
    ROTOR_RADIUS,
    SHOW_FIGURES,
    TABLE_HEIGHT_Z,
    configure_jax_runtime,
    make_config,
)
from .simulator import DroneState, GETrajectory, SimulationEnvironment

configure_jax_runtime()


def build_environment(
    *,
    HORIZONTAL_VELOCITY: float = HORIZONTAL_VELOCITY,
    HEIGHT_IN_ROTOR_RADII: float = HEIGHT_IN_ROTOR_RADII,
    BATTERY_PERCENTAGE: float = BATTERY_PERCENTAGE,
    PRE_HOVER_TIME: float = PRE_HOVER_TIME,
    POST_HOVER_TIME: float = POST_HOVER_TIME,
    controller_class=CrazyfliePIDController,
    use_spatial_trajectory=None,
):
    """Build the physical model, controller, mission, and initial state."""
    propeller_height = (
        TABLE_HEIGHT_Z + float(HEIGHT_IN_ROTOR_RADII) * ROTOR_RADIUS
    )
    center_of_mass_height = propeller_height - PROP_TO_COM
    trajectory = GETrajectory(
        HORIZONTAL_VELOCITY,
        center_of_mass_height,
        PRE_HOVER_TIME,
        POST_HOVER_TIME,
        use_spatial_trajectory=use_spatial_trajectory,
    )
    config = make_config(
        battery_percentage=BATTERY_PERCENTAGE,
        forward_flight_time=trajectory.t3 - trajectory.t0,
        mission_label=MISSION_LABEL,
        horizontal_velocity=HORIZONTAL_VELOCITY,
        height_in_rotor_radii=HEIGHT_IN_ROTOR_RADII,
        xy_velocity_mode=trajectory.use_spatial,
    )
    controller = controller_class(config)
    environment = SimulationEnvironment(
        config, controller, trajectory, dt=config.DT,
    )

    rpm_hover = environment.vehicle.pwm_to_rpm(environment.vehicle.hover_pwm())
    initial_state = DroneState(
        trajectory.X_START, 0.0, trajectory.h_start,
        0.0, 0.0, 0.0,
        1.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0,
        rpm_hover, rpm_hover, rpm_hover, rpm_hover,
    )
    return config, environment, initial_state


def run_dt_data(
    theta_p,
    *,
    HORIZONTAL_VELOCITY: float = HORIZONTAL_VELOCITY,
    HEIGHT_IN_ROTOR_RADII: float = HEIGHT_IN_ROTOR_RADII,
    BATTERY_PERCENTAGE: float = BATTERY_PERCENTAGE,
    PRE_HOVER_TIME: float = PRE_HOVER_TIME,
    POST_HOVER_TIME: float = POST_HOVER_TIME,
    controller_class=CrazyfliePIDController,
):
    """Run one closed-loop virtual episode and return all simulated channels."""
    _, environment, initial_state = build_environment(
        HORIZONTAL_VELOCITY=HORIZONTAL_VELOCITY,
        HEIGHT_IN_ROTOR_RADII=HEIGHT_IN_ROTOR_RADII,
        BATTERY_PERCENTAGE=BATTERY_PERCENTAGE,
        PRE_HOVER_TIME=PRE_HOVER_TIME,
        POST_HOVER_TIME=POST_HOVER_TIME,
        controller_class=controller_class,
    )
    return environment.run(initial_state, theta_p)


def run_dt(theta_p, **mission_settings):
    """Run one episode and return the primary time, state, and command arrays."""
    data = run_dt_data(theta_p, **mission_settings)
    return data["time"], data["state"], data["pwm"]


def main() -> None:
    from .postprocessing import run_postprocessing

    config, environment, initial_state = build_environment()
    data = environment.run(initial_state, GE_COEFFS)
    metrics = run_postprocessing(
        data,
        OUTPUT_DIR,
        config=config,
        show_figures=SHOW_FIGURES,
    )

    print("Mission complete")
    print("theta_p:", jax.device_get(GE_COEFFS))
    print("Final position:", jax.device_get(data["state"][-1, 0:3]))
    print("Mean command:", float(jax.device_get(jnp.mean(data["pwm"]))))
    print("Metrics:", metrics)

    if SHOW_FIGURES:
        import matplotlib.pyplot as plt
        plt.show()


if __name__ == "__main__":
    main()
