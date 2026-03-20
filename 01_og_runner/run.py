# run.py
import argparse
import sys
from runner.config_loader import load_config
from runner.og_runner import run
from runner.summary_extractor import extract_summary, write_summary_csv
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="OG-Core Runner")
    parser.add_argument("config", help="Path to YAML config file")
    parser.add_argument("--no-tpi", action="store_true", help="Skip TPI, solve SS only (faster for testing)")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.no_tpi:
        config.time_path = False

    print(f"[runner] Starting run: {config.run_id}")
    result = run(config)
    print(f"[runner] Completed: {result['status']}")

    # Extract and write summary
    results_dir = Path(result["results_dir"])
    summary = extract_summary(results_dir, scenario="BASELINE")
    summary_path = results_dir / "summary.csv"
    write_summary_csv(summary, summary_path)
    print(f"[runner] Summary written to: {summary_path}")

if __name__ == "__main__":
    main()