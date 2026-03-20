"""
OGCoreRoute.py
--------------
Flask Blueprint for OG-Core model execution endpoints.

Mirrors the structure of CaseRoute.py in the existing MUIOGO API:
  - Blueprint registration pattern
  - jsonify({"message": "...", "status_code": "..."}) response format
  - try/except(IOError) error handling
  - Config.DATA_STORAGE path management
  - Session-based case tracking

Endpoints
---------
POST /ogcore/run
    Accept a scenario config, trigger an OG-Core run asynchronously,
    return run_id immediately. Mirrors how CLEWS runs are dispatched.

GET  /ogcore/status/<run_id>
    Poll run status. Returns "running" | "completed" | "failed"
    and metadata. Mirrors the frontend polling pattern.

GET  /ogcore/results/<run_id>
    Return output file paths and key result data for a completed run.
    Mirrors /getResultData and /getResultCSV patterns.

POST /ogcore/runs
    List all OG-Core runs for the active case session.
    Mirrors /getCases pattern.

DELETE /ogcore/run/<run_id>
    Delete a run's output directory.
    Mirrors /deleteCase pattern.

Author: Tejas Singh Bhati
Project: OG-CLEWS Integration — GSoC 2026, UN DESA
"""

from flask import Blueprint, jsonify, request, session
import os
import json
import shutil
import threading
from datetime import datetime
from pathlib import Path

from Classes.Base import Config
from Classes.Base.FileClass import File
from Classes.OGCore.OGCoreRunner import OGCoreRunner


ogcore_api = Blueprint("OGCoreRoute", __name__)


# ── In-memory run registry ────────────────────────────────────────────────────
# Maps run_id → {"status": ..., "thread": ..., "result": ...}
# In production, persist this to a JSON file or lightweight DB
_run_registry: dict = {}


def _generate_run_id() -> str:
    return "ogcore_" + datetime.now().strftime("%Y%m%d_%H%M%S")


def _run_in_background(runner: OGCoreRunner, run_id: str):
    """Execute OG-Core in a background thread — mirrors how CLEWS dispatches."""
    try:
        result = runner.run()
        _run_registry[run_id]["status"] = "completed"
        _run_registry[run_id]["result"] = result
    except Exception as e:
        _run_registry[run_id]["status"] = "failed"
        _run_registry[run_id]["error"]  = str(e)


# ── POST /ogcore/run ──────────────────────────────────────────────────────────

@ogcore_api.route("/ogcore/run", methods=["POST"])
def run_ogcore():
    """
    Trigger an OG-Core run for the active case.

    Request body (JSON):
    {
        "casename": "MyScenario",
        "ogcore_params": {
            "gdp_growth": 0.03,
            "capital_share": 0.35,
            "labor_share": 0.65
        }
    }

    Response:
    {
        "message": "OG-Core run ogcore_20260314_113000 started!",
        "status_code": "running",
        "run_id": "ogcore_20260314_113000"
    }
    """
    try:
        casename = request.json.get("casename")
        config   = request.json.get("ogcore_params", {})

        # Session validation — mirrors copyCase / deleteCase pattern
        active_case = session.get("osycase", None)
        if not active_case:
            return jsonify({
                "message"    : "No active session. Please select a case first.",
                "status_code": "error"
            }), 403

        if casename != active_case:
            return jsonify({
                "message"    : "Unauthorised: case does not match active session.",
                "status_code": "error"
            }), 403

        # Validate case directory exists
        case_path = Path(Config.DATA_STORAGE, casename)
        if not case_path.is_dir():
            return jsonify({
                "message"    : f"Case '{casename}' not found.",
                "status_code": "error"
            }), 404

        # Generate run ID and set up runner
        run_id  = _generate_run_id()
        runner  = OGCoreRunner(
            casename     = casename,
            run_id       = run_id,
            config       = {"ogcore_params": config},
            data_storage = Path(Config.DATA_STORAGE),
        )

        # Register run
        _run_registry[run_id] = {
            "status"  : "running",
            "casename": casename,
            "result"  : None,
            "error"   : None,
        }

        # Dispatch to background thread — non-blocking response
        thread = threading.Thread(
            target=_run_in_background,
            args=(runner, run_id),
            daemon=True
        )
        thread.start()
        _run_registry[run_id]["thread"] = thread

        response = {
            "message"    : f"OG-Core run <b>{run_id}</b> started!",
            "status_code": "running",
            "run_id"     : run_id,
        }
        return jsonify(response), 200

    except (IOError, KeyError):
        return jsonify({
            "message"    : "Failed to start OG-Core run.",
            "status_code": "error"
        }), 404


# ── GET /ogcore/status/<run_id> ───────────────────────────────────────────────

@ogcore_api.route("/ogcore/status/<run_id>", methods=["GET"])
def get_run_status(run_id: str):
    """
    Poll the status of an OG-Core run.

    Response:
    {
        "run_id": "ogcore_20260314_113000",
        "status": "completed",       // "running" | "completed" | "failed"
        "casename": "MyScenario",
        "status_code": "success"
    }
    """
    try:
        if run_id not in _run_registry:
            # Fall back to reading metadata.json from disk
            # (handles restarts where in-memory registry was cleared)
            casename    = session.get("osycase", None)
            if casename:
                meta_path = Path(Config.DATA_STORAGE, casename, "res", run_id, "metadata.json")
                if meta_path.is_file():
                    with open(meta_path) as f:
                        metadata = json.load(f)
                    return jsonify({
                        "run_id"      : run_id,
                        "status"      : metadata.get("status", "unknown"),
                        "casename"    : metadata.get("casename"),
                        "status_code" : "success",
                    }), 200

            return jsonify({
                "message"    : f"Run '{run_id}' not found.",
                "status_code": "error"
            }), 404

        entry  = _run_registry[run_id]
        status = entry["status"]

        response = {
            "run_id"      : run_id,
            "status"      : status,
            "casename"    : entry["casename"],
            "status_code" : "success",
        }

        if status == "failed":
            response["error"] = entry.get("error")

        return jsonify(response), 200

    except (IOError, KeyError):
        return jsonify({
            "message"    : "Error retrieving run status.",
            "status_code": "error"
        }), 404


# ── GET /ogcore/results/<run_id> ──────────────────────────────────────────────

@ogcore_api.route("/ogcore/results/<run_id>", methods=["GET"])
def get_run_results(run_id: str):
    """
    Return output file paths and key result data for a completed run.
    Mirrors /getResultData pattern from CaseRoute.

    Response:
    {
        "run_id": "ogcore_20260314_113000",
        "status": "completed",
        "results": { ... macro aggregates ... },
        "output_dirs": { "results": "...", "logs": "...", "metadata": "..." },
        "status_code": "success"
    }
    """
    try:
        casename = session.get("osycase", None)
        if not casename:
            return jsonify({
                "message"    : "No active session.",
                "status_code": "error"
            }), 403

        run_dir      = Path(Config.DATA_STORAGE, casename, "res", run_id)
        metadata_path = run_dir / "metadata.json"
        results_path  = run_dir / "results" / "og_results.json"

        if not run_dir.is_dir():
            return jsonify({
                "message"    : f"Run '{run_id}' not found.",
                "status_code": "error"
            }), 404

        # Read metadata
        metadata = {}
        if metadata_path.is_file():
            with open(metadata_path) as f:
                metadata = json.load(f)

        if metadata.get("status") != "completed":
            return jsonify({
                "message"    : f"Run '{run_id}' is not yet completed (status: {metadata.get('status', 'unknown')}).",
                "status_code": "error"
            }), 400

        # Read results
        results = {}
        if results_path.is_file():
            with open(results_path) as f:
                results = json.load(f)

        response = {
            "run_id"      : run_id,
            "casename"    : casename,
            "status"      : "completed",
            "results"     : results,
            "output_dirs" : {
                "results" : str(run_dir / "results"),
                "logs"    : str(run_dir / "logs"),
                "metadata": str(metadata_path),
            },
            "status_code" : "success",
        }
        return jsonify(response), 200

    except (IOError, KeyError):
        return jsonify({
            "message"    : "Error retrieving run results.",
            "status_code": "error"
        }), 404


# ── POST /ogcore/runs ─────────────────────────────────────────────────────────

@ogcore_api.route("/ogcore/runs", methods=["POST"])
def get_runs():
    """
    List all OG-Core runs for a given case.
    Mirrors /getCases and /getResultCSV patterns.

    Request body: { "casename": "MyScenario" }

    Response:
    {
        "runs": ["ogcore_20260314_113000", "ogcore_20260315_090000"],
        "status_code": "success"
    }
    """
    try:
        casename = request.json.get("casename")
        res_path = Path(Config.DATA_STORAGE, casename, "res")

        if not res_path.is_dir():
            return jsonify({
                "runs"       : [],
                "status_code": "success"
            }), 200

        # Only return OG-Core runs (prefixed), not CLEWS runs
        runs = [
            f.name for f in os.scandir(res_path)
            if f.is_dir() and f.name.startswith("ogcore_")
        ]
        runs.sort(reverse=True)  # most recent first

        return jsonify({
            "runs"       : runs,
            "status_code": "success"
        }), 200

    except (IOError, KeyError):
        return jsonify({
            "message"    : "No existing runs found.",
            "status_code": "error"
        }), 404


# ── DELETE /ogcore/run/<run_id> ───────────────────────────────────────────────

@ogcore_api.route("/ogcore/run/<run_id>", methods=["DELETE"])
def delete_run(run_id: str):
    """
    Delete a specific OG-Core run's output directory.
    Mirrors /deleteCase pattern.

    Response:
    {
        "message": "Run ogcore_20260314_113000 deleted!",
        "status_code": "success"
    }
    """
    try:
        casename    = session.get("osycase", None)
        active_case = session.get("osycase", None)

        if not active_case:
            return jsonify({
                "message"    : "No active session.",
                "status_code": "error"
            }), 403

        run_dir = Path(Config.DATA_STORAGE, active_case, "res", run_id)
        if not run_dir.is_dir():
            return jsonify({
                "message"    : f"Run '{run_id}' not found.",
                "status_code": "error"
            }), 404

        shutil.rmtree(run_dir)

        # Remove from in-memory registry
        _run_registry.pop(run_id, None)

        return jsonify({
            "message"    : f"Run <b>{run_id}</b> deleted!",
            "status_code": "success"
        }), 200

    except (IOError, OSError):
        return jsonify({
            "message"    : "Error deleting run.",
            "status_code": "error"
        }), 404