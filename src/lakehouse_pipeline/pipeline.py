"""Idempotent ingestion with synthetic input and bronze/silver/gold tables."""
import csv
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS bronze (
 event_id TEXT PRIMARY KEY, order_id TEXT NOT NULL, customer_id TEXT NOT NULL,
 amount REAL NOT NULL, status TEXT NOT NULL, version INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS silver (
 order_id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, amount REAL NOT NULL,
 status TEXT NOT NULL, version INTEGER NOT NULL);
CREATE VIEW IF NOT EXISTS gold AS
 SELECT customer_id, COUNT(*) AS orders,
 SUM(CASE WHEN status='paid' THEN amount ELSE 0 END) AS paid_amount
 FROM silver GROUP BY customer_id;
"""

def connect(path=":memory:"):
    db = sqlite3.connect(path)
    db.executescript(SCHEMA)
    return db

def ingest(db, rows):
    stats = {"accepted": 0, "duplicates": 0, "rejected": 0}
    with db:
        for row in rows:
            try:
                event_id = row["event_id"].strip()
                order_id = row["order_id"].strip()
                customer_id = row["customer_id"].strip()
                status = row["status"].strip()
                amount = float(row["amount"])
                version = int(row["version"])
                if not all((event_id, order_id, customer_id)) or status not in {"placed","paid","cancelled"} or amount < 0 or version < 0:
                    raise ValueError("invalid event")
            except (KeyError, ValueError, TypeError):
                stats["rejected"] += 1
                continue
            cursor = db.execute("INSERT OR IGNORE INTO bronze VALUES (?,?,?,?,?,?)",
                (event_id, order_id, customer_id, amount, status, version))
            if not cursor.rowcount:
                stats["duplicates"] += 1
                continue
            stats["accepted"] += 1
            db.execute("""INSERT INTO silver VALUES (?,?,?,?,?)
              ON CONFLICT(order_id) DO UPDATE SET
              customer_id=excluded.customer_id,amount=excluded.amount,
              status=excluded.status,version=excluded.version
              WHERE excluded.version > silver.version""",
              (order_id, customer_id, amount, status, version))
    return stats

def ingest_csv(db, source: str | Path):
    with open(source, newline="", encoding="utf-8") as handle:
        return ingest(db, csv.DictReader(handle))

def metrics(db):
    return db.execute("SELECT customer_id,orders,paid_amount FROM gold ORDER BY customer_id").fetchall()
