# coding: utf-8
"""
DRKagi REST API Server
Lightweight Flask API for integration with other security tools.
Usage: python api_server.py
"""

from flask import Flask, request, jsonify
from agent import PentestAgent
from database import DatabaseManager
from cve_lookup import CVELookup
import json
import os

app = Flask(__name__)

# Lazy-init globals
_agent = None
_db = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = PentestAgent()
    return _agent


def get_db():
    global _db
    if _db is None:
        _db = DatabaseManager()
    return _db


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "version": "0.3.0", "engine": "DRKagi"})


@app.route("/api/suggest", methods=["POST"])
def suggest():
    """
    Get AI suggestion for a pentest task.
    Body: {"query": "scan 192.168.1.1"}
    """
    data = request.get_json()
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "Missing 'query' field"}), 400

    agent = get_agent()
    response = agent.get_suggestion(query)
    try:
        parsed = json.loads(response.strip().replace("```json", "").replace("```", ""))
        return jsonify(parsed)
    except json.JSONDecodeError:
        return jsonify({"raw_response": response})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Analyze command output and get next-step suggestion.
    Body: {"command": "nmap -sV 10.10.10.5", "output": "...scan results..."}
    """
    data = request.get_json()
    command = data.get("command", "")
    output = data.get("output", "")
    if not command or not output:
        return jsonify({"error": "Missing 'command' or 'output' field"}), 400

    agent = get_agent()
    response = agent.analyze_output(command, output)
    try:
        parsed = json.loads(response.strip().replace("```json", "").replace("```", ""))
        return jsonify(parsed)
    except json.JSONDecodeError:
        return jsonify({"raw_response": response})


@app.route("/api/script", methods=["POST"])
def generate_script():
    """
    Generate a security script.
    Body: {"task": "port scanner with OS detection", "language": "python"}
    """
    data = request.get_json()
    task = data.get("task", "")
    lang = data.get("language", "python")
    if not task:
        return jsonify({"error": "Missing 'task' field"}), 400

    agent = get_agent()
    response = agent.generate_script(task, lang)
    try:
        parsed = json.loads(response.strip().replace("```json", "").replace("```", ""))
        return jsonify(parsed)
    except json.JSONDecodeError:
        return jsonify({"raw_response": response})


@app.route("/api/targets", methods=["GET"])
def get_targets():
    """Get all discovered targets from the database."""
    db = get_db()
    targets = db.get_all_targets()
    return jsonify({
        "targets": [
            {"ip": t[0], "hostname": t[1], "status": t[2], "last_scanned": t[3]}
            for t in targets
        ]
    })


@app.route("/api/simulate", methods=["POST"])
def simulate():
    """
    Simulate an attack scenario.
    Body: {"scenario": "SQL injection on login page"}
    """
    data = request.get_json()
    scenario = data.get("scenario", "")
    if not scenario:
        return jsonify({"error": "Missing 'scenario' field"}), 400

    agent = get_agent()
    response = agent.simulate_attack(scenario)
    try:
        parsed = json.loads(response.strip().replace("```json", "").replace("```", ""))
        return jsonify(parsed)
    except json.JSONDecodeError:
        return jsonify({"raw_response": response})


@app.route("/api/cve", methods=["GET"])
def cve_lookup():
    """
    Lookup CVEs for a service.
    Query params: ?service=apache&version=2.4.49
    """
    service = request.args.get("service", "")
    version = request.args.get("version", "")
    if not service or not version:
        return jsonify({"error": "Missing 'service' or 'version' query params"}), 400

    cve = CVELookup()
    results = cve.search_cve(service, version)
    return jsonify({"service": service, "version": version, "cves": results})


if __name__ == "__main__":
    print("=" * 50)
    print("  DRKagi REST API Server v0.3")
    print("  Endpoints: /api/health, /api/suggest, /api/analyze,")
    print("             /api/script, /api/targets, /api/simulate, /api/cve")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=False)
