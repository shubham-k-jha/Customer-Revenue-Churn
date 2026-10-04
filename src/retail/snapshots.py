import duckdb
from src.retail.config import TRANSACTIONS_PARQUET, SNAPSHOTS_PARQUET, OBSERVATION_DAYS, HORIZON_DAYS, MIN_HISTORY_DAYS

SQL = f'''
WITH base AS (
    SELECT
        CAST(CustomerID AS BIGINT) AS customer_id,
        CAST(InvoiceDate AS TIMESTAMP) AS invoice_date,
        CAST(Quantity AS DOUBLE) AS quantity,
        CAST(UnitPrice AS DOUBLE) AS unit_price,
        CAST(line_revenue AS DOUBLE) AS line_revenue,
        CAST(Country AS VARCHAR) AS country,
        CAST(StockCode AS VARCHAR) AS stock_code,
        CASE WHEN lower(CAST(InvoiceNo AS VARCHAR)) LIKE 'c%' THEN 1 ELSE 0 END AS is_cancel,
        CAST(date_trunc('month', InvoiceDate) AS DATE) AS month
    FROM read_parquet('{TRANSACTIONS_PARQUET.as_posix()}')
    WHERE CustomerID IS NOT NULL AND InvoiceDate IS NOT NULL
),
dates AS (
    SELECT min(month) AS min_month, max(month) AS max_month FROM base
),
snapshots AS (
    SELECT month::DATE AS snapshot_date
    FROM generate_series(
        (SELECT min_month + INTERVAL '{MIN_HISTORY_DAYS} days' FROM dates),
        (SELECT max_month - INTERVAL '{HORIZON_DAYS} days' FROM dates),
        INTERVAL '1 month'
    ) t(month)
),
features AS (
    SELECT
        s.snapshot_date,
        b.customer_id,
        max(b.invoice_date) FILTER (WHERE b.quantity > 0 AND b.unit_price > 0 AND b.is_cancel = 0)::DATE AS last_purchase_date,
        datediff('day', max(b.invoice_date) FILTER (WHERE b.quantity > 0 AND b.unit_price > 0 AND b.is_cancel = 0), s.snapshot_date) AS recency_days,
        count(DISTINCT b.invoice_date::DATE) FILTER (WHERE b.quantity > 0 AND b.unit_price > 0 AND b.is_cancel = 0) AS purchase_days,
        count(DISTINCT b.stock_code) FILTER (WHERE b.quantity > 0 AND b.unit_price > 0 AND b.is_cancel = 0) AS unique_products,
        count(DISTINCT b.month) FILTER (WHERE b.quantity > 0 AND b.unit_price > 0 AND b.is_cancel = 0) AS active_months,
        sum(b.line_revenue) FILTER (WHERE b.quantity > 0 AND b.unit_price > 0 AND b.is_cancel = 0) AS monetary,
        avg(b.line_revenue) FILTER (WHERE b.quantity > 0 AND b.unit_price > 0 AND b.is_cancel = 0) AS avg_line_revenue,
        sum(b.quantity) FILTER (WHERE b.quantity > 0 AND b.unit_price > 0 AND b.is_cancel = 0) AS units,
        avg(b.unit_price) FILTER (WHERE b.quantity > 0 AND b.unit_price > 0 AND b.is_cancel = 0) AS avg_unit_price,
        count(DISTINCT b.invoice_date::DATE) FILTER (WHERE b.is_cancel = 1) AS cancellation_days,
        count(*) FILTER (WHERE b.is_cancel = 1) AS cancellation_lines,
        max(b.country) FILTER (WHERE b.quantity > 0 AND b.unit_price > 0 AND b.is_cancel = 0) AS country
    FROM snapshots s
    JOIN base b
      ON b.invoice_date < s.snapshot_date
     AND b.invoice_date >= s.snapshot_date - INTERVAL '{OBSERVATION_DAYS} days'
    GROUP BY 1,2
),
future AS (
    SELECT DISTINCT s.snapshot_date, p.customer_id
    FROM snapshots s
    JOIN base p
      ON p.invoice_date >= s.snapshot_date
     AND p.invoice_date < s.snapshot_date + INTERVAL '{HORIZON_DAYS} days'
     AND p.quantity > 0 AND p.unit_price > 0 AND p.is_cancel = 0
)
SELECT
    f.*,
    CASE WHEN fu.customer_id IS NULL THEN 1 ELSE 0 END AS churn_90d,
    CASE WHEN fu.customer_id IS NULL THEN 0 ELSE 1 END AS retained_90d
FROM features f
LEFT JOIN future fu
  ON f.snapshot_date = fu.snapshot_date AND f.customer_id = fu.customer_id
WHERE f.monetary > 0;
'''

def build(out=SNAPSHOTS_PARQUET):
    con = duckdb.connect()
    con.execute(f"COPY ({SQL}) TO '{out.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    return out

if __name__ == '__main__':
    print(build())
