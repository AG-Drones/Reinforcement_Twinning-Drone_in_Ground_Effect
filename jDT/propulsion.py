"""Crazyflie 2.1+ legacy thrust-command conventions.

With firmware battery-thrust compensation enabled, ``control.thrust`` is a
virtual per-motor force request on the legacy [0, 65535] scale.  The firmware
mixes this quantity first and subsequently converts each motor request into a
battery-dependent PWM duty cycle.  The collective command-to-force conversion
is therefore linear and must not use the old PWM-to-RPM calibration.
"""

from __future__ import annotations

import jax.numpy as jnp


LEGACY_COMMAND_MAX = 65535.0
# Calibrated effective value for the current 32.42 g vehicle. The nominal
# Crazyflie 2.1+ firmware platform value is 0.12 N per motor.
CF21PLUS_THRUST_MAX_PER_MOTOR = 0.1148  # [N]


def legacy_command_to_rotor_thrust(
    command,
    thrust_max_per_motor=CF21PLUS_THRUST_MAX_PER_MOTOR,
):
    command = jnp.asarray(command, dtype=jnp.float64)
    return (
        jnp.clip(command, 0.0, LEGACY_COMMAND_MAX)
        / LEGACY_COMMAND_MAX
        * thrust_max_per_motor
    )


def collective_command_to_thrust(
    collective_command,
    thrust_max_per_motor=CF21PLUS_THRUST_MAX_PER_MOTOR,
):
    return 4.0 * legacy_command_to_rotor_thrust(
        collective_command,
        thrust_max_per_motor,
    )


def rotor_thrust_to_legacy_command(
    rotor_thrust,
    thrust_max_per_motor=CF21PLUS_THRUST_MAX_PER_MOTOR,
):
    rotor_thrust = jnp.asarray(rotor_thrust, dtype=jnp.float64)
    return jnp.clip(
        rotor_thrust / thrust_max_per_motor * LEGACY_COMMAND_MAX,
        0.0,
        LEGACY_COMMAND_MAX,
    )
