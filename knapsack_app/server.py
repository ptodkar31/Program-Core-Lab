from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
from knapsack_backend import (
    select_projects_for_budget,
    select_portfolio_by_budget,
    schedule_tasks_with_time_limit,
    Project,
    Asset,
    Task,
)

BASE_DIR = Path(__file__).parent.resolve()
app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")

@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.post("/api/projects")
def api_projects():
    data = request.get_json(force=True) or {}
    projects = [
        Project(
            name=str(p.get("name", "")),
            cost=int(p.get("cost", 0)),
            benefit=float(p.get("benefit", 0.0)),
        )
        for p in data.get("projects", [])
    ]
    budget = int(data.get("budget", 0))
    res = select_projects_for_budget(projects, budget)
    return jsonify(res)

@app.post("/api/portfolio")
def api_portfolio():
    data = request.get_json(force=True) or {}
    assets = [
        Asset(
            name=str(a.get("name", "")),
            price=float(a.get("price", 0.0)),
            expected_return=float(a.get("expected_return", 0.0)),
        )
        for a in data.get("assets", [])
    ]
    capital = float(data.get("capital", 0.0))
    allow_fractional = bool(data.get("allow_fractional", True))
    res = select_portfolio_by_budget(assets, capital, allow_fractional=allow_fractional)
    return jsonify(res)

@app.post("/api/scheduling")
def api_scheduling():
    data = request.get_json(force=True) or {}
    tasks = [
        Task(
            name=str(t.get("name", "")),
            duration=int(t.get("duration", 0)),
            reward=float(t.get("reward", 0.0)),
        )
        for t in data.get("tasks", [])
    ]
    time_limit = int(data.get("time_limit", 0))
    res = schedule_tasks_with_time_limit(tasks, time_limit)
    return jsonify(res)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
