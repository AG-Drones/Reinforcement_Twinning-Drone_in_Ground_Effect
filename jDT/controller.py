# TAG R
from __future__ import annotations

from typing import NamedTuple

from jax import config as jax_config
from jax import lax
import jax.numpy as jnp

try:
    from .simulator import quat_to_rot, rot_to_euler_zyx
except ImportError:
    from simulator import quat_to_rot, rot_to_euler_zyx

jax_config.update("jax_enable_x64", True)


class ControllerState(NamedTuple):
    integral: jnp.ndarray
    prev_meas: jnp.ndarray
    has_prev: jnp.ndarray
    step: jnp.ndarray
    held_roll_cmd: jnp.ndarray
    held_pitch_cmd: jnp.ndarray
    held_thrust_pwm: jnp.ndarray


_PID_COUNT = 12
POS_X, POS_Y, POS_Z = 0, 1, 2
VEL_X, VEL_Y, VEL_Z = 3, 4, 5
ROLL, PITCH, YAW = 6, 7, 8
ROLL_RATE, PITCH_RATE, YAW_RATE = 9, 10, 11


def init_controller_state(base_thrust_pwm=36000.0) -> ControllerState:
    return ControllerState(
        integral=jnp.zeros(_PID_COUNT, dtype=jnp.float64),
        prev_meas=jnp.zeros(_PID_COUNT, dtype=jnp.float64),
        has_prev=jnp.zeros(_PID_COUNT, dtype=jnp.bool_),
        step=jnp.asarray(0, dtype=jnp.int32),
        held_roll_cmd=jnp.asarray(0.0, dtype=jnp.float64),
        held_pitch_cmd=jnp.asarray(0.0, dtype=jnp.float64),
        held_thrust_pwm=jnp.asarray(base_thrust_pwm, dtype=jnp.float64),
    )


def _pid_update(
    index: int,
    setpoint,
    measurement,
    dt,
    controller_state: ControllerState,
    gains: jnp.ndarray,
    i_limits: jnp.ndarray,
    out_limits: jnp.ndarray,
):
    dt_safe = jnp.maximum(jnp.asarray(dt, dtype=jnp.float64), 1e-9)
    error = setpoint - measurement

    i_limit = i_limits[index]
    out_limit = out_limits[index]
    kp, ki, kd = gains[index]

    integral_final = jnp.clip(
        controller_state.integral[index] + error * dt_safe,
        -i_limit,
        i_limit,
    )
    d_meas = jnp.where(
        controller_state.has_prev[index],
        (measurement - controller_state.prev_meas[index]) / dt_safe,
        0.0,
    )

    # Match firmware pid.c: clamp the integral, then clamp the total output.
    # There is no conditional integral rollback when the output saturates.
    u_final = jnp.clip(kp * error + ki * integral_final - kd * d_meas, -out_limit, out_limit)

    new_state = controller_state._replace(
        integral=controller_state.integral.at[index].set(integral_final),
        prev_meas=controller_state.prev_meas.at[index].set(measurement),
        has_prev=controller_state.has_prev.at[index].set(True),
    )
    return u_final, new_state


class CrazyfliePIDController:
    """JAX translation of the original cascaded Crazyflie PID controller."""

    def __init__(self, config):
        self.c = config
        self.gains = jnp.stack([
            config.POS_X_PID,
            config.POS_Y_PID,
            config.POS_Z_PID,
            config.VEL_X_PID,
            config.VEL_Y_PID,
            config.VEL_Z_PID,
            config.ROLL_PID,
            config.PITCH_PID,
            config.YAW_PID,
            config.ROLL_RATE_PID,
            config.PITCH_RATE_PID,
            config.YAW_RATE_PID,
        ]).astype(jnp.float64)
        self.i_limits = jnp.array([
            5000.0, 5000.0, 5000.0,
            5000.0, 5000.0, 5000.0,
            20.0, 20.0, 360.0,
            33.3, 33.3, 166.7,
        ], dtype=jnp.float64)
        self.out_limits = jnp.array([
            1.1, 1.1, 1.1,
            20.0, 20.0, 65535.0 / 2.0 / 1000.0,
            360.0, 360.0, 360.0,
            20000.0, 20000.0, 20000.0,
        ], dtype=jnp.float64)

        omega_h = jnp.sqrt((config.MASS * config.GRAVITY / 4.0) / config.KF)
        self.hover_rpm = omega_h * 60.0 / (2.0 * jnp.pi)
        self.base_thrust_pwm = jnp.asarray(
            config.CONTROLLER_THRUST_BASE,
            dtype=jnp.float64,
        )

        # The experimental mission starts after the vehicle has settled in
        # hover, so the vertical-velocity PID integrator has already supplied
        # the difference between ``thrustBase`` and the collective command
        # required to balance weight.  Starting the DT with all integrators at
        # zero produces an artificial fall and a long recovery transient.
        self.hover_collective_pwm = jnp.clip(
            (config.MASS * config.GRAVITY)
            / (4.0 * config.FIRMWARE_THRUST_MAX_PER_MOTOR)
            * config.PWM_MAX,
            config.CONTROLLER_THRUST_MIN,
            config.PWM_MAX,
        )

    def initial_state(self) -> ControllerState:
        state = init_controller_state(self.base_thrust_pwm)
        vz_ki = self.gains[VEL_Z, 1]
        equilibrium_vz_integral = jnp.where(
            jnp.abs(vz_ki) > 1.0e-12,
            (self.hover_collective_pwm - self.base_thrust_pwm)
            / (1000.0 * vz_ki),
            0.0,
        )
        equilibrium_vz_integral = jnp.clip(
            equilibrium_vz_integral,
            -self.i_limits[VEL_Z],
            self.i_limits[VEL_Z],
        )
        return state._replace(
            integral=state.integral.at[VEL_Z].set(equilibrium_vz_integral),
            held_thrust_pwm=self.hover_collective_pwm,
        )

    def correct_collective_thrust_pwm(self, thrust_pwm, state: jnp.ndarray):
        """Identity hook overridden by alternative controllers."""
        del state
        return thrust_pwm

    def compute_control(
        self,
        state: jnp.ndarray,
        ref: jnp.ndarray,
        dt,
        controller_state: ControllerState,
        *,
        return_collective: bool = False,
    ):
        rotation = quat_to_rot(state[6:10])
        roll_rad, pitch_rad, yaw_rad = rot_to_euler_zyx(rotation)
        roll_deg = jnp.rad2deg(roll_rad)
        pitch_deg = jnp.rad2deg(pitch_rad)
        yaw_deg = jnp.rad2deg(yaw_rad)
        rates_deg = jnp.rad2deg(state[10:13])

        # Firmware scheduling: position and velocity loops run at 100 Hz while
        # attitude and rate loops run at 500 Hz. Hold the outer-loop outputs
        # during the four intervening 2 ms simulation steps.
        def update_outer_loop(saved_state):
            outer_dt = 5.0 * dt
            if self.c.XY_VELOCITY_MODE:
                vx_cmd = ref[3]
                vy_cmd = ref[4]
                updated_state = saved_state
            else:
                vx_cmd, updated_state = _pid_update(
                    POS_X, ref[0], state[0], outer_dt, saved_state,
                    self.gains, self.i_limits, self.out_limits,
                )
                vy_cmd, updated_state = _pid_update(
                    POS_Y, ref[1], state[1], outer_dt, updated_state,
                    self.gains, self.i_limits, self.out_limits,
                )
            vz_cmd, updated_state = _pid_update(
                POS_Z, ref[2], state[2], outer_dt, updated_state,
                self.gains, self.i_limits, self.out_limits,
            )
            pitch_cmd_new, updated_state = _pid_update(
                VEL_X, vx_cmd, state[3], outer_dt, updated_state,
                self.gains, self.i_limits, self.out_limits,
            )
            roll_cmd_raw, updated_state = _pid_update(
                VEL_Y, vy_cmd, state[4], outer_dt, updated_state,
                self.gains, self.i_limits, self.out_limits,
            )
            thrust_delta, updated_state = _pid_update(
                VEL_Z, vz_cmd, state[5], outer_dt, updated_state,
                self.gains, self.i_limits, self.out_limits,
            )
            return updated_state._replace(
                held_roll_cmd=jnp.clip(-roll_cmd_raw, -20.0, 20.0),
                held_pitch_cmd=jnp.clip(pitch_cmd_new, -20.0, 20.0),
                held_thrust_pwm=jnp.clip(
                    self.base_thrust_pwm + 1000.0 * thrust_delta,
                    self.c.CONTROLLER_THRUST_MIN,
                    self.c.PWM_MAX,
                ),
            )

        controller_state = lax.cond(
            jnp.equal(jnp.mod(controller_state.step, 5), 0),
            update_outer_loop,
            lambda saved_state: saved_state,
            controller_state,
        )
        roll_cmd = controller_state.held_roll_cmd
        pitch_cmd = controller_state.held_pitch_cmd

        yaw_cmd = jnp.rad2deg(ref[9])
        roll_rate_cmd, controller_state = _pid_update(ROLL, roll_cmd, roll_deg, dt, controller_state, self.gains, self.i_limits, self.out_limits)
        pitch_rate_cmd, controller_state = _pid_update(PITCH, pitch_cmd, pitch_deg, dt, controller_state, self.gains, self.i_limits, self.out_limits)
        yaw_rate_cmd, controller_state = _pid_update(YAW, yaw_cmd, yaw_deg, dt, controller_state, self.gains, self.i_limits, self.out_limits)

        roll_pwm, controller_state = _pid_update(ROLL_RATE, roll_rate_cmd, rates_deg[0], dt, controller_state, self.gains, self.i_limits, self.out_limits)
        pitch_pwm, controller_state = _pid_update(PITCH_RATE, pitch_rate_cmd, rates_deg[1], dt, controller_state, self.gains, self.i_limits, self.out_limits)
        yaw_pwm, controller_state = _pid_update(YAW_RATE, yaw_rate_cmd, rates_deg[2], dt, controller_state, self.gains, self.i_limits, self.out_limits)

        thrust_pwm = controller_state.held_thrust_pwm
        thrust_pwm = self.correct_collective_thrust_pwm(thrust_pwm, state)

        r = 0.5 * roll_pwm
        p = 0.5 * pitch_pwm
        y = yaw_pwm
        pwm = jnp.array([
            thrust_pwm - r - p + y,
            thrust_pwm - r + p - y,
            thrust_pwm + r + p + y,
            thrust_pwm + r - p - y,
        ], dtype=jnp.float64)
        pwm = jnp.clip(pwm, self.c.PWM_MIN, self.c.PWM_MAX)
        controller_state = controller_state._replace(
            step=controller_state.step + jnp.asarray(1, dtype=jnp.int32)
        )

        if return_collective:
            return pwm, controller_state, thrust_pwm
        return pwm, controller_state
