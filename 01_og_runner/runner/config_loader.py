import yaml
import uuid
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

@dataclass
class RunConfig:
    scenario_name: str
    country_module: str
    time_path: bool
    start_year: int
    og_spec: dict
    output_base_dir: Path
    run_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6])

def load_config(path: str) -> RunConfig:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return RunConfig(
        scenario_name=raw["run"]["scenario_name"],
        country_module=raw["run"]["country_module"],
        time_path=raw["run"].get("time_path", True),
        start_year=raw["run"].get("start_year", 2025),
        og_spec=raw.get("og_spec", {}),
        output_base_dir=Path(raw["output"]["base_dir"]),
    )