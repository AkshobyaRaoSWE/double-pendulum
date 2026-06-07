"""Integrate the pendulum over time and build trajectories for drawing.

Two entry points:
  * `simulate` runs a single pendulum and returns the joint positions per frame.
  * `simulate_ensemble` runs a group of pendulums whose starting angles differ by
    a tiny perturbation -- the visual proof of chaos, as they peel apart.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .dynamics import Pendulum, energy, rk4_step


@dataclass
class Trajectory:
    """Joint positions of one pendulum over the whole run."""

    x1: np.ndarray
    y1: np.ndarray
    x2: np.ndarray
    y2: np.ndarray


def _positions(states: np.ndarray, p: Pendulum) -> Trajectory:
    """Convert a sequence of states into upper/lower joint xy positions."""
    th1, th2 = states[:, 0], states[:, 2]
    x1 = p.l1 * np.sin(th1)
    y1 = -p.l1 * np.cos(th1)
    x2 = x1 + p.l2 * np.sin(th2)
    y2 = y1 - p.l2 * np.cos(th2)
    return Trajectory(x1, y1, x2, y2)


def integrate(state0: np.ndarray, p: Pendulum, duration: float,
              dt: float) -> np.ndarray:
    """Integrate from `state0` and return the (F, 4) array of states."""
    steps = int(duration / dt)
    states = np.empty((steps + 1, 4))
    states[0] = state0
    for i in range(steps):
        states[i + 1] = rk4_step(states[i], p, dt)
    return states


def simulate(state0: np.ndarray, p: Pendulum | None = None, *,
             duration: float = 15.0, dt: float = 0.005,
             frame_dt: float = 0.02) -> tuple[Trajectory, float]:
    """Run one pendulum.

    Integrates at the fine `dt` for accuracy, then subsamples to `frame_dt` for
    the animation. Returns the trajectory and the relative energy drift over the
    run (a small number means the integration stayed accurate).
    """
    p = p or Pendulum()
    states = integrate(state0, p, duration, dt)

    # Normalize energy drift by a fixed energy scale (the full potential swing),
    # not by the initial energy -- a horizontal start has E = 0, which would make
    # a ratio meaningless.
    e_scale = (p.m1 + p.m2) * p.g * (p.l1 + p.l2)
    drift = abs(energy(states[-1], p) - energy(states[0], p)) / e_scale

    stride = max(int(frame_dt / dt), 1)
    return _positions(states[::stride], p), drift


def simulate_ensemble(state0: np.ndarray, p: Pendulum | None = None, *,
                      count: int = 6, perturbation: float = 1e-3,
                      duration: float = 15.0, dt: float = 0.005,
                      frame_dt: float = 0.02) -> list[Trajectory]:
    """Run `count` pendulums whose initial theta1 differs by tiny steps.

    They start visually identical, then diverge -- the signature of chaos.
    """
    p = p or Pendulum()
    trajectories = []
    for k in range(count):
        s = state0.copy()
        s[0] += k * perturbation
        traj, _ = simulate(s, p, duration=duration, dt=dt, frame_dt=frame_dt)
        trajectories.append(traj)
    return trajectories
