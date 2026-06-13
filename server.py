"""Flask backend: serves the web UI and a /api/simulate endpoint.

The browser sends the starting angles, masses, lengths and number of "ghost"
pendulums; this integrates them and returns the joint positions per frame as
JSON for the canvas to animate. Run:

    python server.py    ->    open http://localhost:5050
"""

from __future__ import annotations

import numpy as np
from flask import Flask, jsonify, request, send_from_directory

from dpend import Pendulum, simulate_ensemble

app = Flask(__name__, static_folder="web", static_url_path="")


@app.route("/")
def index():
    return send_from_directory("web", "index.html")


@app.route("/api/simulate")
def api_simulate():
    """Integrate an ensemble of pendulums and return their frames as JSON."""
    try:
        a = request.args
        p = Pendulum(
            m1=float(a.get("m1", 1.0)), m2=float(a.get("m2", 1.0)),
            l1=float(a.get("l1", 1.0)), l2=float(a.get("l2", 1.0)),
        )
        state0 = np.array([
            float(a.get("th1", 2.0)), 0.0, float(a.get("th2", 2.0)), 0.0,
        ])
        count = max(1, min(int(a.get("ghosts", 6)), 20))
        duration = max(2.0, min(float(a.get("duration", 15.0)), 40.0))
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    trajs = simulate_ensemble(state0, p, count=count, perturbation=1e-3,
                              duration=duration)
    pendulums = [
        {"x1": t.x1.tolist(), "y1": t.y1.tolist(),
         "x2": t.x2.tolist(), "y2": t.y2.tolist()}
        for t in trajs
    ]
    return jsonify({
        "reach": p.l1 + p.l2,
        "frame_dt": 0.02,
        "frames": len(trajs[0].x1),
        "pendulums": pendulums,
    })


if __name__ == "__main__":
    # 5050, not 5000: macOS Control Center / AirPlay Receiver holds port 5000.
    app.run(host="127.0.0.1", port=5050, debug=False)
