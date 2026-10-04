-- UCI Online Retail II business analytics (DuckDB/PostgreSQL-compatible concepts)
-- 1. Revenue by month
SELECT date_trunc('month', invoice_date) AS month,
       SUM(quantity * unit_price) AS gross_revenue,
       COUNT(DISTINCT invoice_no) AS invoices,
       COUNT(DISTINCT customer_id) AS customers
FROM retail_transactions
WHERE quantity > 0 AND unit_price > 0
GROUP BY 1 ORDER BY 1;

-- 2. Country contribution
SELECT country,
       SUM(quantity * unit_price) AS revenue,
       COUNT(DISTINCT customer_id) AS customers
FROM retail_transactions
WHERE quantity > 0 AND unit_price > 0
GROUP BY 1 ORDER BY revenue DESC;

-- 3. Snapshot churn rate
SELECT snapshot_date,
       AVG(churn_90d) AS churn_90d_rate,
       COUNT(*) AS customers
FROM retail_churn_snapshots
GROUP BY 1 ORDER BY 1;

-- 4. Revenue at risk among customers predicted high-risk
SELECT SUM(monetary) AS historical_revenue_exposure,
       COUNT(*) AS high_risk_customers
FROM retail_churn_scores
WHERE risk_band = 'High';
