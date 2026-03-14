# run_etl.py
import argparse
from pathlib import Path
from exchange.transformer import run_transform
from exchange.validator import validate_inputs, validate_outputs
from exchange.writer import write_exchange_file

REQUIRED_FILES = [
    "TotalCapacityAnnual.csv",
    "AnnualTechnologyEmission.csv",
    "TotalDiscountedCost.csv",
]

def main():
    parser = argparse.ArgumentParser(description="CLEWS → OG-Core ETL Pipeline")
    parser.add_argument("--data-dir",   default="data/sample_clews_outputs")
    parser.add_argument("--schema",     default="exchange/schema_clews_to_og.yaml")
    parser.add_argument("--output",     default="outputs/og_exchange.json")
    args = parser.parse_args()

    data_dir    = Path(args.data_dir)
    schema_path = Path(args.schema)
    output_path = Path(args.output)

    print("[etl] Step 1: Validating inputs...")
    errors = validate_inputs(data_dir, REQUIRED_FILES)
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
        raise SystemExit(1)
    print("  All input files valid.")

    print("[etl] Step 2: Running transformations...")
    params = run_transform(schema_path, data_dir)

    print("[etl] Step 3: Validating outputs...")
    validated = validate_outputs(params)
    print(f"  Validated params: {validated.model_dump()}")

    print("[etl] Step 4: Writing exchange file...")
    write_exchange_file(
        params=validated.model_dump(),
        output_path=output_path,
        metadata={"data_dir": str(data_dir), "schema": str(schema_path)},
    )
    print("[etl] Done.")

if __name__ == "__main__":
    main()