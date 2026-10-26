from __future__ import annotations

import jax.numpy as jnp

from .params import (
    OBSTACLE_X_END, OBSTACLE_X_START, ROTOR_RADIUS, TABLE_HEIGHT_Z,
)

CHEESEMAN_BENNETT_COEFFS = jnp.array([1.0 / 16.0, 2.0], dtype=jnp.float64)
MIN_F_GE = 0.05


def f_ge(z, theta_p=None):
    """Static ground-effect factor ``1 + A (R/z)^p``.

    ``theta_p = [A, p]`` contains the physical-model parameters used in the
    paper.  The classical Cheeseman--Bennett values are used only when no
    identified parameters are supplied.
    """
    theta_p = (
        CHEESEMAN_BENNETT_COEFFS
        if theta_p is None
        else jnp.asarray(theta_p, dtype=jnp.float64)
    )
    normalized_clearance = (
        ROTOR_RADIUS / jnp.maximum(jnp.asarray(z), 0.05 * ROTOR_RADIUS)
    )
    return jnp.maximum(
        1.0 + theta_p[0] * normalized_clearance ** theta_p[1],
        MIN_F_GE,
    )


def rotor_disk_fraction_after_edge(rotor_x, edge_x):
    d = (jnp.asarray(rotor_x) - edge_x) / ROTOR_RADIUS
    q = jnp.clip(d, -1.0 + 1e-9, 1.0 - 1e-9)
    partial = 0.5 + (jnp.arcsin(q) + q * jnp.sqrt(1.0 - q**2)) / jnp.pi
    return jnp.where(d <= -1.0, 0.0, jnp.where(d >= 1.0, 1.0, partial))


def rotor_disk_fraction_over_obstacle(rotor_x):
    return jnp.clip(
        rotor_disk_fraction_after_edge(rotor_x, OBSTACLE_X_START)
        - rotor_disk_fraction_after_edge(rotor_x, OBSTACLE_X_END), 0.0, 1.0
    )


def apply_ge(thrusts, rotor_x, rotor_z, theta_p=None):
    """Apply the finite-obstacle GE correction independently to each rotor."""
    clearance = jnp.maximum(jnp.asarray(rotor_z) - TABLE_HEIGHT_Z, 0.05 * ROTOR_RADIUS)
    overlap = rotor_disk_fraction_over_obstacle(rotor_x)
    factor = 1.0 + overlap * (f_ge(clearance, theta_p=theta_p) - 1.0)
    return thrusts * jnp.maximum(factor, 0.05)
