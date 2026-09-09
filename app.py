"""
Flask backend for the Lamport Logical Clock Simulator.

Routes:
  GET  /                 -> serves the frontend
  POST /api/simulate     -> runs a simulation, returns JSON trace
"""

from flask import Flask, jsonify, request, render_template
from lamport import simulate

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    payload = request.get_json(silent=True) or {}

    try:
        num_processes = int(payload.get("num_processes", 3))
        events_per_process = int(payload.get("events_per_process", 6))
        message_probability = float(payload.get("message_probability", 0.35))
        seed = payload.get("seed")
        seed = int(seed) if seed not in (None, "") else None
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid parameters. Check types."}), 400

    if not (2 <= num_processes <= 8):
        return jsonify({"error": "num_processes must be between 2 and 8"}), 400
    if not (1 <= events_per_process <= 20):
        return jsonify({"error": "events_per_process must be between 1 and 20"}), 400
    if not (0 <= message_probability <= 1):
        return jsonify({"error": "message_probability must be between 0 and 1"}), 400

    result = simulate(num_processes, events_per_process, message_probability, seed)
    return jsonify(result)


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
