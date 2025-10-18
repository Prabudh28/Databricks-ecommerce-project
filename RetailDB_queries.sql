%sql
SELECT MAX(InvoiceDate) AS LatestDate FROM bronze_online_retail

CREATE OR REPLACE TABLE silver_online_retail
AS
SELECT *,
  Quantity * Price AS TotalPrice
FROM bronze_online_retail
WHERE CustomerID IS NOT NULL AND Quantity > 0

SELECT COUNT(*) FROM silver_online_retail


CREATE OR REPLACE TABLE gold_customer_rfm
AS
SELECT
  CustomerID,

  -- Recency: Days from 'today' (max date) to last purchase
  DATEDIFF(
    (SELECT MAX(InvoiceDate) FROM silver_online_retail), -- This is 'today'
    MAX(InvoiceDate)                                      -- This is customer's last purchase
  ) AS Recency,
  
  -- Frequency: Count of unique orders
  COUNT(DISTINCT Invoice) AS Frequency,
  
  -- Monetary: Total amount spent
  SUM(TotalPrice) AS Monetary
  
FROM silver_online_retail
GROUP BY CustomerID

SELECT * FROM gold_customer_rfm
ORDER BY Monetary DESC
LIMIT 10


-- Create a new table with R, F, and M scores from 1-4
CREATE OR REPLACE TABLE gold_customer_segments
AS
SELECT
  CustomerID,
  Recency,
  Frequency,
  Monetary,
  -- Score for Recency (lower is better, so we reverse the order)
  NTILE(4) OVER (ORDER BY Recency DESC) AS R_Score,
  
  -- Score for Frequency (higher is better)
  NTILE(4) OVER (ORDER BY Frequency ASC) AS F_Score,
  
  -- Score for Monetary (higher is better)
  NTILE(4) OVER (ORDER BY Monetary ASC) AS M_Score
  
FROM gold_customer_rfm



SELECT
  CustomerID,
  Recency,
  Frequency,
  Monetary,
  R_Score,
  F_Score,
  M_Score,
  -- We can combine scores to get a segment
  CONCAT(R_Score, F_Score, M_Score) AS RFM_Score_Combined,
  
  -- Or use logic to create named segments
  CASE
    WHEN R_Score = 4 AND F_Score = 4 AND M_Score = 4 THEN 'Champions'
    WHEN R_Score >= 3 AND F_Score >= 3 THEN 'Loyal Customers'
    WHEN R_Score >= 3 AND F_Score <= 2 THEN 'Potential Loyalists'
    WHEN R_Score = 4 AND F_Score = 1 THEN 'New Customers'
    WHEN R_Score = 2 AND (F_Score = 1 OR F_Score = 2) THEN 'Promising'
    WHEN R_Score = 3 AND (F_Score = 1 OR F_Score = 2) THEN 'Needs Attention'
    WHEN R_Score <= 2 AND F_Score >= 3 THEN 'At Risk (High Value)'
    WHEN R_Score <= 2 AND F_Score <= 2 THEN 'At Risk (Low Value)'
    WHEN R_Score = 1 THEN 'Lost'
    ELSE 'Other'
  END AS Customer_Segment
  
FROM gold_customer_segments
ORDER BY Monetary DESC