from flask import Flask, render_template, request, jsonify
import json
import os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.maritime import generate_simulation

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    sim = generate_simulation(turns=30, seed=7, speed=1.0)
    return render_template("index.html", sim_json=json.dumps(sim))

@app.route("/api/simulate", methods=["POST"])
def simulate():
    sim = generate_simulation(turns=30, seed=7, speed=1.0)
    return jsonify(sim)

if __name__ == "__main__":
    app.run(debug=True)
