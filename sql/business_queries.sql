-- Executive KPI
SELECT COUNT(*) customers, SUM(churn_flag) churned, ROUND(AVG(churn_flag)*100,2) churn_rate_pct, ROUND(SUM(monthly_charges),2) monthly_revenue FROM customers;

-- Churn and revenue by contract
SELECT contract, COUNT(*) customers, SUM(churn_flag) churned, ROUND(AVG(churn_flag)*100,2) churn_rate_pct, ROUND(SUM(monthly_charges),2) monthly_revenue FROM customers GROUP BY contract ORDER BY churn_rate_pct DESC;

-- Revenue exposure among observed churners (descriptive, not a forecast)
SELECT ROUND(SUM(monthly_charges) FILTER (WHERE churn_flag=1),2) monthly_revenue_from_observed_churners FROM customers;

-- Tenure bands
SELECT CASE WHEN tenure<=12 THEN '0-12' WHEN tenure<=24 THEN '13-24' WHEN tenure<=48 THEN '25-48' ELSE '49+' END tenure_band, COUNT(*) customers, ROUND(AVG(churn_flag)*100,2) churn_rate_pct FROM customers GROUP BY 1 ORDER BY 1;

-- Payment method
SELECT payment_method, COUNT(*) customers, ROUND(AVG(churn_flag)*100,2) churn_rate_pct, ROUND(AVG(monthly_charges),2) avg_monthly_charge FROM customers GROUP BY payment_method ORDER BY churn_rate_pct DESC;

-- High-value churn exposure
SELECT COUNT(*) customers, ROUND(SUM(monthly_charges),2) monthly_revenue FROM customers WHERE churn_flag=1 AND monthly_charges >= (SELECT PERCENTILE_CONT(.75) WITHIN GROUP (ORDER BY monthly_charges) FROM customers);
