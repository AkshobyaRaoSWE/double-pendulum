"""Generate the static fallback data and the README demo image.

  * web/data.json   -- a default ensemble so the web UI animates on static
    hosting (GitHub Pages) without the Python backend running.
  * assets/demo.png -- the tip traces of the ensemble, showing them start as one
    curve and fan apart into chaos.

Run after changing the model:  python generate_data.py
"""

from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from dpend import Pendulum, simulate_ensemble

STATE0 = np.array([2.0, 0.0, 2.0, 0.0])
COUNT = 8
DURATION = 15.0
FRAME_DT = 0.02


def write_json() -> None:
    trajs = simulate_ensemble(STATE0, Pendulum(), count=COUNT,
                              perturbation=1e-3, duration=DURATION,
                              frame_dt=FRAME_DT)
    data = {
        "reach": 2.0,
        "frame_dt": FRAME_DT,
        "frames": len(trajs[0].x1),
        "pendulums": [
            {"x1": t.x1.tolist(), "y1": t.y1.tolist(),
             "x2": t.x2.tolist(), "y2": t.y2.tolist()}
            for t in trajs
        ],
    }
    with open("web/data.json", "w") as f:
        json.dump(data, f)
    print(f"wrote web/data.json ({COUNT} pendulums, {data['frames']} frames)")


def write_demo() -> None:
    trajs = simulate_ensemble(STATE0, Pendulum(), count=COUNT,
                              perturbation=1e-3, duration=DURATION,
                              frame_dt=FRAME_DT)
    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor("#06070b")
    ax.set_facecolor("#06070b")

    cmap = plt.get_cmap("plasma")
    for k, t in enumerate(trajs):
        ax.plot(t.x2, t.y2, color=cmap(k / (COUNT - 1)), lw=1.0, alpha=0.8)

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Tip paths of 8 pendulums starting 0.001 rad apart",
                 color="#e8eaf2")
    fig.tight_layout()
    fig.savefig("assets/demo.png", dpi=130, facecolor="#06070b")
    print("wrote assets/demo.png")


if __name__ == "__main__":
    write_json()
    write_demo()
