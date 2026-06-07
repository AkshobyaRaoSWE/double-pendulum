"""Double-pendulum equations of motion and an RK4 integrator.

The double pendulum is the classic example of deterministic chaos: fully
described by four numbers (two angles, two angular velocities) and a handful of
constants, yet so sensitive to its starting state that two near-identical
pendulums diverge completely within seconds.

The equations of motion come from the Lagrangian of the system. They're
nonlinear and coupled, so there's no closed-form solution -- we integrate them
numerically with a 4th-order Runge-Kutta step, the same integrator used in the
projectile and lap-time projects.

State vector convention:  [theta1, omega1, theta2, omega2]
Angles are measured from straight down; gravity points -y.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

GRAVITY = 9.81


@dataclass
class Pendulum:
    """Physical constants of a double pendulum."""

    m1: float = 1.0   # upper bob mass (kg)
    m2: float = 1.0   # lower bob mass (kg)
    l1: float = 1.0   # upper rod length (m)
    l2: float = 1.0   # lower rod length (m)
    g: float = GRAVITY


def derivatives(state: np.ndarray, p: Pendulum) -> np.ndarray:
    """Time derivative of the state vector (the equations of motion)."""
    th1, w1, th2, w2 = state
    m1, m2, l1, l2, g = p.m1, p.m2, p.l1, p.l2, p.g
    delta = th1 - th2
    cos_d, sin_d = np.cos(delta), np.sin(delta)

    den = 2 * m1 + m2 - m2 * np.cos(2 * th1 - 2 * th2)

    dw1 = (
        -g * (2 * m1 + m2) * np.sin(th1)
        - m2 * g * np.sin(th1 - 2 * th2)
        - 2 * sin_d * m2 * (w2 * w2 * l2 + w1 * w1 * l1 * cos_d)
    ) / (l1 * den)

    dw2 = (
        2 * sin_d * (
            w1 * w1 * l1 * (m1 + m2)
            + g * (m1 + m2) * np.cos(th1)
            + w2 * w2 * l2 * m2 * cos_d
        )
    ) / (l2 * den)

    return np.array([w1, dw1, w2, dw2])


def rk4_step(state: np.ndarray, p: Pendulum, dt: float) -> np.ndarray:
    """Advance the state by one 4th-order Runge-Kutta step."""
    k1 = derivatives(state, p)
    k2 = derivatives(state + 0.5 * dt * k1, p)
    k3 = derivatives(state + 0.5 * dt * k2, p)
    k4 = derivatives(state + dt * k3, p)
    return state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def energy(state: np.ndarray, p: Pendulum) -> float:
    """Total mechanical energy (kinetic + potential), in joules.

    For an undamped pendulum this is conserved, so it doubles as an accuracy
    check on the integrator.
    """
    th1, w1, th2, w2 = state
    m1, m2, l1, l2, g = p.m1, p.m2, p.l1, p.l2, p.g

    kinetic = (
        0.5 * m1 * (l1 * w1) ** 2
        + 0.5 * m2 * (
            (l1 * w1) ** 2 + (l2 * w2) ** 2
            + 2 * l1 * l2 * w1 * w2 * np.cos(th1 - th2)
        )
    )
    potential = -(m1 + m2) * g * l1 * np.cos(th1) - m2 * g * l2 * np.cos(th2)
    return float(kinetic + potential)
