# exchange/writer.py
import json
from pathlib import Path
from datetime import datetime


def write_exchange_file(params: dict, output_path: Path, metadata: dict = None):
    """
    Write validated OG-Core parameters to a JSON exchange file.
    This file is the handoff artifact between CLEWS and OG-Core.
    """
    output = {
        "generated_at": datetime.utcnow().isoformat(),
        "source_model": "CLEWS/OSeMOSYS",
        "target_model": "OG-Core",
        "metadata": metadata or {},
        "og_parameters": params,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[writer] Exchange file written to: {output_path}")