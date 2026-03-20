# runner/output_writer.py
from pathlib import Path
import json
from datetime import datetime

def _make_serializable(obj):
    """Recursively convert non-JSON-serializable types."""
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_serializable(i) for i in obj]
    return obj

class OutputWriter:
    def __init__(self, base_dir: Path, run_id: str, scenario_name: str):
        self.run_id = run_id
        self.scenario_name = scenario_name
        self.run_dir = base_dir / run_id
        self.results_dir = self.run_dir / "results"
        self.logs_dir = self.run_dir / "logs"
        self._create_dirs()

    def _create_dirs(self):
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def write_metadata(self, config_dict: dict, status: str = "running", error: str = None):
        metadata = {
            "run_id": self.run_id,
            "scenario_name": self.scenario_name,
            "status": status,
            "started_at": datetime.utcnow().isoformat(),
            "config": _make_serializable(config_dict),
        }
        if error:
            metadata["error"] = error
        
        metadata_path = self.run_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def update_metadata(self, updates: dict):
        path = self.run_dir / "metadata.json"
        if not path.exists():
            return
            
        with open(path) as f:
            metadata = json.load(f)
        metadata.update(_make_serializable(updates))
        with open(path, "w") as f:
            json.dump(metadata, f, indent=2)

    @property
    def log_path(self) -> Path:
        return self.logs_dir / "run.log"