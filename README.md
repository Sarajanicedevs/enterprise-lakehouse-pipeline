# Enterprise Lakehouse Pipeline

A reproducible portfolio example of incremental bronze → silver → gold data processing using Python, SQLite and synthetic order events. Demonstrates data validation, idempotent ingestion, latest-event reconciliation and customer metrics.

## Architecture
CSV events → input validation → bronze event log → silver order state → gold customer metrics.

## Quick start
```bash
python -m pip install -e '.[dev]'
python -m lakehouse_pipeline --input data/order_events.csv --database demo.sqlite
pytest -q
```
Re-running ingestion should not duplicate accepted records. SQLite is used so the example needs no cloud account; Delta Lake, Snowflake and Airflow would be production extensions, not integrations claimed in this repository.

**Scope:** Independent demo with synthetic data, not proprietary employer code or a production deployment.
