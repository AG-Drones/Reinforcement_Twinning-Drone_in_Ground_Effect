# TAG X
from __future__ import annotations

from dataclasses import dataclass

from jax import config as jax_config
from jax import lax
import jax.numpy as jnp

try:
    from .GE_correction import apply_ge
    from .propulsion import (
        legacy_command_to_rotor_thrust,
        rotor_thrust_to_legacy_command,
    )
    from .params import (
        SPATIAL_MAX_LATERAL_SPEED, SPATIAL_MIN_FORWARD_SPEED, SPATIAL_Y_KP,
        USE_SPATIAL_TRAJECTORY, X_START, X_ACCEL_END, X_CONSTANT_END, X_END,
        X_SPATIAL_DECEL_START, X_SPATIAL_STOP,
    )
except ImportError:
    from GE_correction import apply_ge
    from propulsion import (
        legacy_command_to_rotor_thrust,
        rotor_thrust_to_legacy_command,
    )
    from params import (
        SPATIAL_MAX_LATERAL_SPEED, SPATIAL_MIN_FORWARD_SPEED, SPATIAL_Y_KP,
        USE_SPATIAL_TRAJECTORY, X_START, X_ACCEL_END, X_CONSTANT_END, X_END,
        X_SPATIAL_DECEL_START, X_SPATIAL_STOP,
    )

jax_config.update("jax_enable_x64", True)


def _crazyflie_go_to_poly7(tau):
    tau = jnp.clip(tau, 0.0, 1.0)
    return (
        35.0*tau**4 - 84.0*tau**5 + 70.0*tau**6 - 20.0*tau**7,
        140.0*tau**3 - 420.0*tau**4 + 420.0*tau**5 - 140.0*tau**6,
        420.0*tau**2 - 1680.0*tau**3 + 2100.0*tau**4 - 840.0*tau**5,
    )


@dataclass
class DroneState:
    x: float; y: float; z: float
    vx: float; vy: float; vz: float
    qw: float; qx: float; qy: float; qz: float
    p: float; q: float; r: float
    rpm1: float; rpm2: float; rpm3: float; rpm4: float

    def as_vector(self):
        return jnp.array([
            self.x, self.y, self.z, self.vx, self.vy, self.vz,
            self.qw, self.qx, self.qy, self.qz,
            self.p, self.q, self.r,
            self.rpm1, self.rpm2, self.rpm3, self.rpm4,
        ], dtype=jnp.float64)

    @staticmethod
    def from_vector(v):
        values = [float(x) for x in v[:17]]
        return DroneState(*values)


def normalize_quat(q):
    q = jnp.asarray(q, dtype=jnp.float64)
    norm = jnp.linalg.norm(q)
    safe_norm = jnp.where(norm > 1e-12, norm, 1.0)
    normalized = q / safe_norm
    normalized = jnp.where(norm > 1e-12, normalized, jnp.array([1.0, 0.0, 0.0, 0.0], dtype=jnp.float64))
    return jnp.where(normalized[0] < 0.0, -normalized, normalized)


def quat_to_rot(q):
    qw, qx, qy, qz = normalize_quat(q)
    return jnp.array([
        [1 - 2*(qy*qy + qz*qz), 2*(qx*qy - qz*qw), 2*(qx*qz + qy*qw)],
        [2*(qx*qy + qz*qw), 1 - 2*(qx*qx + qz*qz), 2*(qy*qz - qx*qw)],
        [2*(qx*qz - qy*qw), 2*(qy*qz + qx*qw), 1 - 2*(qx*qx + qy*qy)],
    ], dtype=jnp.float64)


def rot_to_euler_zyx(rotation):
    theta = jnp.arcsin(jnp.clip(-rotation[2, 0], -1.0, 1.0))
    return jnp.array([
        jnp.arctan2(rotation[2, 1], rotation[2, 2]),
        theta,
        jnp.arctan2(rotation[1, 0], rotation[0, 0]),
    ], dtype=jnp.float64)


def quat_dot(q, omega_body):
    qw, qx, qy, qz = q
    p, qv, r = omega_body
    return 0.5 * jnp.array([
        -qx*p - qy*qv - qz*r,
        qw*p + qy*r - qz*qv,
        qw*qv - qx*r + qz*p,
        qw*r + qx*qv - qy*p,
    ], dtype=jnp.float64)


def _poly7_coeff(T, x0, v0, a0, j0, x1, v1, a1, j1):
    c = jnp.zeros(8, dtype=jnp.float64)
    c = c.at[0].set(x0)
    c = c.at[1].set(v0)
    c = c.at[2].set(0.5*a0)
    c = c.at[3].set(j0/6.0)
    matrix = jnp.array([
        [T**4, T**5, T**6, T**7],
        [4*T**3, 5*T**4, 6*T**5, 7*T**6],
        [12*T**2, 20*T**3, 30*T**4, 42*T**5],
        [24*T, 60*T**2, 120*T**3, 210*T**4],
    ], dtype=jnp.float64)
    kp = c[0] + c[1]*T + c[2]*T**2 + c[3]*T**3
    kv = c[1] + 2*c[2]*T + 3*c[3]*T**2
    ka = 2*c[2] + 6*c[3]*T
    kj = 6*c[3]
    rhs = jnp.array([x1-kp, v1-kv, a1-ka, j1-kj], dtype=jnp.float64)
    return c.at[4:8].set(jnp.linalg.solve(matrix, rhs))


class GETrajectory:
    mission_type = "ge_tracking"

    def __init__(
        self,
        v,
        h,
        t_hover_pre,
        t_hover_post,
        use_spatial_trajectory=None,
    ):
        self.v = float(v)
        # h is the COM world-z reference already mapped from the experimental
        # Lighthouse-deck setpoint by build_environment().
        self.h = float(h)
        self.h_start = self.h
        self.X_START = X_START
        self.X_ACCEL_END = X_ACCEL_END
        self.X_CONSTANT_END = X_CONSTANT_END
        self.X_END = X_END
        self.X_SPATIAL_DECEL_START = X_SPATIAL_DECEL_START
        self.X_SPATIAL_STOP = X_SPATIAL_STOP
        self.use_spatial = bool(
            USE_SPATIAL_TRAJECTORY
            if use_spatial_trajectory is None
            else use_spatial_trajectory
        )
        self.mission_type = "ge_spatial_tracking" if self.use_spatial else "ge_tracking"
        self.t0 = float(t_hover_pre)
        self.t_acc = 2.0*(self.X_ACCEL_END-self.X_START)/self.v
        self.t_const = (self.X_CONSTANT_END-self.X_ACCEL_END)/self.v
        self.t_dec = 2.0*(self.X_END-self.X_CONSTANT_END)/self.v
        self.t1 = self.t0 + self.t_acc
        self.t2 = self.t1 + self.t_const
        self.t3 = self.t2 + self.t_dec
        self.t_mission_spatial = 3.0*(self.X_SPATIAL_STOP-self.X_START)/self.v
        if self.use_spatial:
            self.t1 = self.t0 + self.t_mission_spatial
            self.t2 = self.t1
            self.t3 = self.t1
        self.tf = self.t3 + float(t_hover_post)
        self.T_total = self.tf
        self.c_acc = _poly7_coeff(
            self.t_acc, self.X_START, 0.0, 0.0, 0.0,
            self.X_ACCEL_END, self.v, 0.0, 0.0,
        )
        self.c_z_acc = _poly7_coeff(
            self.t_acc, self.h_start, 0.0, 0.0, 0.0,
            self.h, 0.0, 0.0, 0.0,
        )
        self.c_dec = _poly7_coeff(self.t_dec, self.X_CONSTANT_END, self.v, 0.0, 0.0, self.X_END, 0.0, 0.0, 0.0)

    @staticmethod
    def _eval(coefficients, local_time):
        powers = jnp.arange(8, dtype=jnp.float64)
        x = jnp.sum(coefficients * local_time**powers)
        vx = jnp.sum(jnp.where(powers >= 1.0, powers * coefficients * local_time**jnp.maximum(powers-1.0, 0.0), 0.0))
        ax = jnp.sum(jnp.where(powers >= 2.0, powers*(powers-1.0)*coefficients*local_time**jnp.maximum(powers-2.0, 0.0), 0.0))
        return x, vx, ax

    @staticmethod
    def _smoothstep(value):
        u = jnp.clip(value, 0.0, 1.0)
        return u**3 * (10.0 - 15.0*u + 6.0*u**2)

    def _spatial_velocity(self, x):
        minimum_speed = jnp.minimum(self.v, float(SPATIAL_MIN_FORWARD_SPEED))
        accel_progress = (x-self.X_START)/(self.X_ACCEL_END-self.X_START)
        decel_progress = (
            (x-self.X_SPATIAL_DECEL_START)
            /(self.X_SPATIAL_STOP-self.X_SPATIAL_DECEL_START)
        )
        accel_blend = self._smoothstep(accel_progress)
        decel_blend = self._smoothstep(decel_progress)
        speed_range_squared = self.v**2-minimum_speed**2
        vx_accel = jnp.sqrt(minimum_speed**2+speed_range_squared*accel_blend)
        vx_decel = jnp.sqrt(minimum_speed**2+speed_range_squared*(1.0-decel_blend))
        return jnp.where(
            x < self.X_ACCEL_END,
            vx_accel,
            jnp.where(
                x < self.X_SPATIAL_DECEL_START,
                self.v,
                jnp.where(x < self.X_SPATIAL_STOP, vx_decel, 0.0),
            ),
        )

    def get_reference_vector(self, t, state=None):
        if self.use_spatial:
            x = self.X_START if state is None else state[0]
            y = 0.0 if state is None else state[1]
            mission_active = (t >= self.t0) & (t < self.t1)
            z_reference = jnp.where(t < self.t0, self.h_start, self.h)
            vx = jnp.where(mission_active, self._spatial_velocity(x), 0.0)
            vy = jnp.where(
                mission_active,
                jnp.clip(-float(SPATIAL_Y_KP)*y, -float(SPATIAL_MAX_LATERAL_SPEED), float(SPATIAL_MAX_LATERAL_SPEED)),
                0.0,
            )
            return jnp.array([
                x, 0.0, z_reference,
                vx, vy, 0.0,
                0.0, 0.0, 0.0,
                0.0,
            ], dtype=jnp.float64)

        def pre_hover(_):
            return jnp.array([self.X_START, 0.0, 0.0], dtype=jnp.float64)

        def acceleration(_):
            return jnp.stack(self._eval(self.c_acc, t-self.t0))

        def constant(_):
            dt = t-self.t1
            return jnp.array([self.X_ACCEL_END+self.v*dt, self.v, 0.0], dtype=jnp.float64)

        def deceleration(_):
            return jnp.stack(self._eval(self.c_dec, t-self.t2))

        def post_hover(_):
            return jnp.array([self.X_END, 0.0, 0.0], dtype=jnp.float64)

        x_vx_ax = lax.cond(
            t < self.t0,
            pre_hover,
            lambda _: lax.cond(
                t < self.t1,
                acceleration,
                lambda __: lax.cond(
                    t < self.t2,
                    constant,
                    lambda ___: lax.cond(t < self.t3, deceleration, post_hover, operand=None),
                    operand=None,
                ),
                operand=None,
            ),
            operand=None,
        )
        z_vz_az = lax.cond(
            t < self.t0,
            lambda _: jnp.array([self.h_start, 0.0, 0.0], dtype=jnp.float64),
            lambda _: lax.cond(
                t < self.t1,
                lambda __: jnp.stack(self._eval(self.c_z_acc, t-self.t0)),
                lambda __: jnp.array([self.h, 0.0, 0.0], dtype=jnp.float64),
                operand=None,
            ),
            operand=None,
        )
        return jnp.array([
            x_vx_ax[0], 0.0, z_vz_az[0],
            x_vx_ax[1], 0.0, z_vz_az[1],
            x_vx_ax[2], 0.0, z_vz_az[2],
            0.0,
        ], dtype=jnp.float64)

    def get_reference(self, t, state=None):
        ref = self.get_reference_vector(jnp.asarray(t, dtype=jnp.float64), state)
        return {
            "x": ref[0], "y": ref[1], "z": ref[2],
            "vx": ref[3], "vy": ref[4], "vz": ref[5],
            "ax": ref[6], "ay": ref[7], "az": ref[8],
            "yaw": ref[9], "yaw_rate": 0.0,
        }


class CrazyflieVehicle:
    def __init__(
        self,
        config,
        ge_velocity_x=None,
        ge_velocity_vx=None,
    ):
        self.c = config
        self.I = jnp.asarray(config.I_MATRIX, dtype=jnp.float64)
        self.I_inv = jnp.linalg.inv(self.I)
        self.spin_sign = jnp.array([1.0, -1.0, 1.0, -1.0], dtype=jnp.float64)
        # Motor order consistent with wrench_from_thrusts below. In the X
        # layout, motors 0/3 are on +body-x and motors 1/2 on -body-x.
        arm_xy = 0.5 * config.MOTOR_DISTANCE
        rotor_z = config.ROTOR_PLANE_Z_ABOVE_COM
        self.rotor_positions_body = jnp.array(
            [
                [ arm_xy, -arm_xy, rotor_z],
                [-arm_xy, -arm_xy, rotor_z],
                [-arm_xy,  arm_xy, rotor_z],
                [ arm_xy,  arm_xy, rotor_z],
            ],
            dtype=jnp.float64,
        )
        if (ge_velocity_x is None) != (ge_velocity_vx is None):
            raise ValueError("ge_velocity_x and ge_velocity_vx must be provided together")
        self.ge_velocity_x = (
            None if ge_velocity_x is None
            else jnp.asarray(ge_velocity_x, dtype=jnp.float64)
        )
        self.ge_velocity_vx = (
            None if ge_velocity_vx is None
            else jnp.asarray(ge_velocity_vx, dtype=jnp.float64)
        )

    def battery_voltage(self):
        pct = jnp.clip(self.c.BATTERY_PERCENTAGE, 0.0, 100.0)
        order = jnp.argsort(self.c.BATTERY_SOC_LOOKUP)
        return jnp.interp(pct, self.c.BATTERY_SOC_LOOKUP[order], self.c.BATTERY_VOLTAGE_LOOKUP[order])

    def battery_omega_factor(self):
        corrected = jnp.clip(self.battery_voltage()/jnp.maximum(self.c.BATTERY_VOLTAGE_REFERENCE, 1e-9), 0.0, 1.5)
        return jnp.where(self.c.INCLUDE_BATTERY_CORRECTION, corrected, 1.0)

    def pwm_to_rpm(self, pwm):
        # ``pwm`` is the legacy virtual thrust command before the firmware's
        # battery compensation, not the final hardware PWM duty cycle.
        requested_thrust = legacy_command_to_rotor_thrust(
            pwm,
            self.c.FIRMWARE_THRUST_MAX_PER_MOTOR,
        )
        return self.rpm_to_omega_inverse(requested_thrust)

    def rpm_to_omega_inverse(self, thrust):
        omega = jnp.sqrt(jnp.maximum(thrust, 0.0) / self.c.KF)
        return omega * 60.0 / (2.0 * jnp.pi)

    @staticmethod
    def rpm_to_omega(rpm):
        return jnp.asarray(rpm, dtype=jnp.float64)*(2.0*jnp.pi/60.0)

    def hover_pwm(self):
        return rotor_thrust_to_legacy_command(
            self.c.MASS * self.c.GRAVITY / 4.0,
            self.c.FIRMWARE_THRUST_MAX_PER_MOTOR,
        )

    def motor_thrusts(self, rpm, state=None, theta_p=None):
        thrusts = self.c.KF*self.rpm_to_omega(rpm)**2
        if state is None:
            return thrusts
        rotation = quat_to_rot(normalize_quat(state[6:10]))
        rotor_positions_world = (
            state[:3][None, :]
            + (rotation @ self.rotor_positions_body.T).T
        )
        return apply_ge(
            thrusts,
            rotor_positions_world[:, 0],
            rotor_positions_world[:, 2],
            theta_p,
        )

    def motor_yaw_torques(self, rpm):
        return self.spin_sign*self.c.KM*self.rpm_to_omega(rpm)**2

    def wrench_from_thrusts(self, thrusts, rpm):
        t = jnp.asarray(thrusts, dtype=jnp.float64)
        return jnp.array([
            jnp.sum(t),
            0.5*self.c.MOTOR_DISTANCE*(-t[0]-t[1]+t[2]+t[3]),
            0.5*self.c.MOTOR_DISTANCE*(-t[0]+t[1]+t[2]-t[3]),
            jnp.sum(self.motor_yaw_torques(rpm)),
        ], dtype=jnp.float64)

    def wrench_from_rpm(self, rpm, state=None, theta_p=None):
        return self.wrench_from_thrusts(self.motor_thrusts(rpm, state, theta_p), rpm)

    def body_drag_force(self, rotation, vel_world):
        v_body = rotation.T @ jnp.asarray(vel_world, dtype=jnp.float64)
        return -jnp.asarray(self.c.CD, dtype=jnp.float64)*jnp.abs(v_body)*v_body

    def dynamics(self, state_vec, pwm_cmd, t, theta_p=None):
        del t
        vel = state_vec[3:6]
        quat = normalize_quat(state_vec[6:10])
        omega_body = state_vec[10:13]
        rpm = state_vec[13:17]
        rotation = quat_to_rot(quat)
        rpm_cmd = self.pwm_to_rpm(jnp.clip(pwm_cmd, self.c.PWM_MIN, self.c.PWM_MAX))
        rpm_dot = jnp.clip(
            (rpm_cmd-rpm)/jnp.maximum(self.c.TAU_RPM, 1e-9),
            -self.c.RPM_DOT_MAX,
            self.c.RPM_DOT_MAX,
        )
        wrench = self.wrench_from_rpm(rpm, state_vec, theta_p)
        force_body = jnp.array([0.0, 0.0, wrench[0]], dtype=jnp.float64)+self.body_drag_force(rotation, vel)
        acc = jnp.array([0.0, 0.0, -self.c.GRAVITY], dtype=jnp.float64)+(rotation@force_body)/self.c.MASS
        omega_dot = self.I_inv@(wrench[1:4]-jnp.cross(omega_body, self.I@omega_body))
        return jnp.concatenate([vel, acc, quat_dot(quat, omega_body), omega_dot, rpm_dot])

    def rk4_step(self, state_vec, pwm_cmd, dt, t0, theta_p=None):
        k1 = self.dynamics(state_vec, pwm_cmd, t0, theta_p)
        k2 = self.dynamics(state_vec+0.5*dt*k1, pwm_cmd, t0+0.5*dt, theta_p)
        k3 = self.dynamics(state_vec+0.5*dt*k2, pwm_cmd, t0+0.5*dt, theta_p)
        k4 = self.dynamics(state_vec+dt*k3, pwm_cmd, t0+dt, theta_p)
        nxt = state_vec+dt*(k1+2*k2+2*k3+k4)/6.0
        nxt = nxt.at[6:10].set(normalize_quat(nxt[6:10]))
        nxt = nxt.at[13:17].set(jnp.clip(nxt[13:17], self.pwm_to_rpm(self.c.PWM_MIN), self.pwm_to_rpm(self.c.PWM_MAX)))
        return nxt


class SimulationEnvironment:
    def __init__(
        self,
        config,
        controller,
        trajectory,
        dt,
        t_final=None,
        ge_velocity_x=None,
        ge_velocity_vx=None,
    ):
        self.vehicle = CrazyflieVehicle(
            config,
            ge_velocity_x=ge_velocity_x,
            ge_velocity_vx=ge_velocity_vx,
        )
        self.controller = controller
        self.trajectory = trajectory
        self.dt = float(dt)
        self.t_final = float(trajectory.T_total if t_final is None else t_final)

    def run(self, initial_state: DroneState, theta_p=None, initial_controller_state=None):
        t_vec = jnp.arange(0.0, self.t_final+self.dt, self.dt, dtype=jnp.float64)
        controller_state0 = (
            self.controller.initial_state()
            if initial_controller_state is None
            else initial_controller_state
        )
        state0 = initial_state.as_vector()

        def step(carry, t):
            state, controller_state = carry
            rotation = quat_to_rot(state[6:10])
            ref = self.trajectory.get_reference_vector(t, state)
            pwm, controller_state_next, collective_pwm = self.controller.compute_control(
                state,
                ref,
                self.dt,
                controller_state,
                return_collective=True,
            )
            rpm_cmd = self.vehicle.pwm_to_rpm(pwm)
            deriv = self.vehicle.dynamics(state, pwm, t, theta_p)
            acceleration = deriv[3:6]
            thrust = self.vehicle.motor_thrusts(state[13:17])
            wrench_cmd = self.vehicle.wrench_from_rpm(rpm_cmd)
            euler = rot_to_euler_zyx(rotation)
            state_next = self.vehicle.rk4_step(state, pwm, self.dt, t, theta_p)
            outputs = (
                state,
                ref,
                pwm,
                collective_pwm,
                acceleration,
                thrust,
                wrench_cmd,
                euler,
            )
            return (state_next, controller_state_next), outputs

        (_, _), outputs = lax.scan(step, (state0, controller_state0), t_vec)
        (
            states,
            references,
            pwm,
            collective_pwm,
            acceleration,
            thrust,
            wrench_cmd,
            euler,
        ) = outputs
        return {
            "time": t_vec,
            "state": states,
            "reference": references,
            "pwm": pwm,
            "collective_pwm": collective_pwm,
            "command": wrench_cmd,
            "pwm_command": pwm,
            "acceleration": acceleration,
            "motor": jnp.column_stack((self.vehicle.pwm_to_rpm(pwm), thrust)),
            "euler": euler,
            "crashed": False,
            "crash_reason": "",
            "crash_time": jnp.nan,
            "mission_type": getattr(self.trajectory, "mission_type", "trajectory_tracking"),
        }
