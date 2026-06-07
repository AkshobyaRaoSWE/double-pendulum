"""Tests for the double-pendulum dynamics.

Run with:  python -m pytest   (or: python tests/test_dpend.py)
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dpend import Pendulum, energy, integrate, simulate, simulate_ensemble  # noqa: E402


def test_energy_is_conserved():
    """RK4 must conserve total energy to a tight tolerance (undamped system)."""
    p = Pendulum()
    s0 = np.array([2.0, 0.0, 2.0, 0.0])
    states = integrate(s0, p, duration=15.0, dt=0.005)
    e0, e1 = energy(states[0], p), energy(states[-1], p)
    e_scale = (p.m1 + p.m2) * p.g * (p.l1 + p.l2)
    assert abs(e1 - e0) / e_scale < 1e-4


def test_rest_state_stays_at_rest():
    """Hanging straight down with no velocity is an equilibrium."""
    p = Pendulum()
    s0 = np.array([0.0, 0.0, 0.0, 0.0])
    states = integrate(s0, p, duration=5.0, dt=0.005)
    assert np.allclose(states[-1], s0, atol=1e-9)


def test_chaos_diverges():
    """Two pendulums 0.001 rad apart must separate dramatically (chaos)."""
    s0 = np.array([2.0, 0.0, 2.0, 0.0])
    a, b = simulate_ensemble(s0, count=2, perturbation=1e-3, duration=15.0)
    sep = np.hypot(a.x2 - b.x2, a.y2 - b.y2)
    assert sep.max() > 1.0   # tips end up over a meter apart


def test_near_identical_start_initially_together():
    """The same pendulums must start essentially on top of each other."""
    s0 = np.array([2.0, 0.0, 2.0, 0.0])
    a, b = simulate_ensemble(s0, count=2, perturbation=1e-3, duration=15.0)
    sep0 = np.hypot(a.x2[0] - b.x2[0], a.y2[0] - b.y2[0])
    assert sep0 < 1e-2


def test_trajectory_within_reach():
    """The lower tip can never be farther from the pivot than l1 + l2."""
    p = Pendulum(l1=1.0, l2=0.7)
    traj, _ = simulate(np.array([2.5, 0.0, 1.0, 0.0]), p, duration=10.0)
    r = np.hypot(traj.x2, traj.y2)
    assert r.max() <= (p.l1 + p.l2) + 1e-6


def test_simulate_reports_small_drift():
    """The drift returned by simulate() should be small for a good integration."""
    _, drift = simulate(np.array([2.0, 0.0, 2.0, 0.0]), duration=15.0)
    assert drift < 1e-4


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} passed")
