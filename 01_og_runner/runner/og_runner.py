# runner/og_runner.py
import importlib
import traceback
from ogcore.parameters import Specifications
from ogcore import execute
from runner.config_loader import RunConfig
from runner.output_writer import OutputWriter
from runner.log_capture import LogCapture


def build_parameters(config: RunConfig) -> Specifications:
    p = Specifications(
        output_base=(config.output_base_dir / config.run_id / "results").as_posix(),
        baseline=True,
        baseline_dir=(
            config.output_base_dir / config.run_id / "results" / "OUTPUT_BASELINE"
        ).as_posix(),
    )

    # Dynamically load country calibration if specified
    if config.country_module:
        country_lib = importlib.import_module(f"{config.country_module}.calibrate")
        calibration = country_lib.Calibration(p)
        updated_params = calibration.get_dict()
        p.update_specifications(updated_params)

    # Merge start_year from run config + any og_spec overrides
    # og_spec wins if it explicitly sets start_year too
    spec_overrides = {"start_year": config.start_year}
    spec_overrides.update(config.og_spec)
    p.update_specifications(spec_overrides)

    return p


def run(config: RunConfig) -> dict:
    writer = OutputWriter(
        config.output_base_dir,
        config.run_id,
        config.scenario_name,
    )

    # Write initial metadata before anything runs
    writer.write_metadata(
        config_dict=config.__dict__,
        status="running",
    )

    try:
        with LogCapture(writer.log_path):
            p = build_parameters(config)
            execute.runner(p, time_path=config.time_path, client=None)

        writer.update_metadata({
            "status": "complete",
            "results_dir": str(writer.results_dir),
        })

        return {
            "status": "complete",
            "run_id": config.run_id,
            "results_dir": str(writer.results_dir),
        }

    except Exception as e:
        tb = traceback.format_exc()
        writer.update_metadata({
            "status": "failed",
            "error": tb,
        })
        raise