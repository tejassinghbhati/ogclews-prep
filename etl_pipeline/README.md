# etl_pipeline/README.md
# CLEWS to OG-Core ETL Pipeline

This module handles the transformation of resource-system outputs (CLEWS) into macroeconomic shocks for OG-Core.

## Structure
- `data/`: Sample CSV outputs from a CLEWS run.
- `exchange/`: Core transformation logic, schema mappings, and validation.
- `run_etl.py`: CLI tool to execute the pipeline.

## Usage
```bash
python run_etl.py --data-dir data/sample_clews_outputs --output og_exchange.json
```

## Transformation Logic
The pipeline uses a YAML schema to map specific technologies and metrics from CLEWS (e.g., total discounted cost for power sector) to OG-Core parameter overrides (e.g., investment shocks).
