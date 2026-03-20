"""
OGCoreRunner.py
---------------
Programmatic runner for the OG-Core macroeconomic model.

Wraps ogcore.execute.runner() so it can be called from the MUIOGO
Flask backend without subprocess calls — the same approach the existing
CLEWS runner uses for OSeMOSYS.

In production this class:
  - Accepts a scenario config dict (from the frontend or API request)
  - Applies parameter overrides via p.update_specifications()
  - Captures stdout/stderr to a structured log file
  - Writes outputs to a standardized directory structure:
      DataStorage/{casename}/res/{run_id}/results/
      DataStorage/{casename}/res/{run_id}/logs/
      DataStorage/{casename}/res/{run_id}/metadata.json

Author: Tejas Singh Bhati
Project: OG-CLEWS Integration — GSoC 2026, UN DESA
"""

import json
import logging
import os
import sys
import io
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime
from pathlib import Path


class OGCoreRunner:
    """
    Programmatic OG-Core runner for MUIOGO backend integration.

    Parameters
    ----------
    casename : str
        Name of the case (maps to DataStorage/{casename}/)
    run_id : str
        Unique run identifier (timestamp-based)
    config : dict
        Scenario configuration including OG-Core parameter overrides
    data_storage : Path
        Root DataStorage path from Config
    """

    def __init__(self, casename: str, run_id: str, config: dict, data_storage: Path):
        self.casename     = casename
        self.run_id       = run_id
        self.config       = config
        self.data_storage = data_storage

        # Output directory structure mirrors CLEWS res/ layout
        self.run_dir      = Path(data_storage, casename, "res", run_id)
        self.results_dir  = self.run_dir / "results"
        self.logs_dir     = self.run_dir / "logs"

        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.log_path      = self.logs_dir / "ogcore_run.log"
        self.metadata_path = self.run_dir  / "metadata.json"

        self._setup_logger()


    def _setup_logger(self):
        self.logger = logging.getLogger(f"ogcore.runner.{self.run_id}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        fmt = logging.Formatter(
            "%(asctime)s  %(levelname)-8s  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        fh = logging.FileHandler(self.log_path, mode="w")
        fh.setFormatter(fmt)
        self.logger.addHandler(fh)


    def _write_metadata(self, status: str, error: str = None):
        """Write run metadata.json — mirrors MUIOGO's resData.json pattern."""
        metadata = {
            "run_id"      : self.run_id,
            "casename"    : self.casename,
            "status"      : status,           # "running" | "completed" | "failed"
            "config"      : self.config,
            "timestamp"   : datetime.now().isoformat(),
            "output_dirs" : {
                "results" : str(self.results_dir),
                "logs"    : str(self.logs_dir),
            }
        }
        if error:
            metadata["error"] = error

        with open(self.metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        self.logger.info(f"Metadata written → {self.metadata_path}")


    def run(self) -> dict:
        """
        Execute OG-Core programmatically.

        Returns
        -------
        dict
            Run result with status, run_id, output paths, and
            key macroeconomic indicators extracted from results.
        """
        self.logger.info("=" * 60)
        self.logger.info(f"OG-Core Run — {self.run_id}")
        self.logger.info(f"Case      : {self.casename}")
        self.logger.info(f"Config    : {json.dumps(self.config, indent=2)}")
        self.logger.info("=" * 60)

        self._write_metadata(status="running")

        try:
            # ── Attempt real OG-Core execution ─────────────────────────
            # In production: import and run ogcore programmatically
            # import ogcore.parameters as Specifications
            # import ogcore.execute as runner
            #
            # p = Specifications.Calibration()
            # overrides = self.config.get("ogcore_params", {})
            # if overrides:
            #     p.update_specifications(overrides)
            #
            # stdout_capture = io.StringIO()
            # stderr_capture = io.StringIO()
            # with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            #     runner.run_og_spec(p, output_base=str(self.results_dir))
            #
            # self.logger.info(stdout_capture.getvalue())
            # if stderr_capture.getvalue():
            #     self.logger.warning(stderr_capture.getvalue())

            # ── Mock execution for prototype ────────────────────────────
            self.logger.info("Running OG-Core (mock execution)...")
            results = self._mock_run()

            # Write results JSON
            results_path = self.results_dir / "og_results.json"
            with open(results_path, "w") as f:
                json.dump(results, f, indent=2)
            self.logger.info(f"Results written → {results_path}")

            self._write_metadata(status="completed")
            self.logger.info("Run completed successfully.")

            return {
                "message"     : f"OG-Core run <b>{self.run_id}</b> completed!",
                "status_code" : "success",
                "run_id"      : self.run_id,
                "results"     : results,
                "output_dirs" : {
                    "results" : str(self.results_dir),
                    "logs"    : str(self.logs_dir),
                    "metadata": str(self.metadata_path),
                }
            }

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Run failed: {error_msg}", exc_info=True)
            self._write_metadata(status="failed", error=error_msg)
            raise


    def _mock_run(self) -> dict:
        """
        Mock OG-Core execution for prototype.
        Returns plausible macroeconomic aggregates.
        Replace with real ogcore.execute.runner() call in production.
        """
        import math
        params = self.config.get("ogcore_params", {})
        gdp    = params.get("gdp_growth", 0.03)
        cap    = params.get("capital_share", 0.35)

        return {
            "generated_at"    : datetime.now().isoformat(),
            "model"           : "OG-Core (mock)",
            "run_id"          : self.run_id,
            "macro_aggregates": {
                "GDP_growth"      : round(gdp, 4),
                "investment_share": round(cap * 0.3, 4),
                "consumption_share": round(1 - cap * 0.3, 4),
            },
            "factor_prices"   : {
                "wage_rate"    : round(1.0 + gdp * 2, 4),
                "interest_rate": round(0.04 + cap * 0.02, 4),
            },
            "fiscal"          : {
                "tax_revenue_pct_gdp": round(0.18 + gdp * 0.5, 4),
            }
        }