import argparse
from .pipeline import connect, ingest_csv, metrics

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--database", default="demo.sqlite")
args = parser.parse_args()
db = connect(args.database)
print(ingest_csv(db, args.input))
print(metrics(db))
