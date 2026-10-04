from pathlib import Path
from src.config import ROOT

RAW = ROOT / 'data' / 'raw'
PROCESSED = ROOT / 'data' / 'processed'
RETAIL_RAW = RAW / 'online_retail_ii.zip'
TRANSACTIONS_PARQUET = PROCESSED / 'online_retail_ii.parquet'
SNAPSHOTS_PARQUET = PROCESSED / 'retail_churn_snapshots.parquet'
MODEL = ROOT / 'artifacts' / 'retail_churn_model.joblib'

# Business definition: a customer is churned if they make no positive-quantity purchase
# during the 90 days following the snapshot date. Refund-only activity does not count.
OBSERVATION_DAYS = 365
HORIZON_DAYS = 90
SNAPSHOT_FREQUENCY = 'MS'
MIN_HISTORY_DAYS = 365
