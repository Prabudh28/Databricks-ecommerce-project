# Databricks-ecommerce-project
 The project analyzes a large e-commerce dataset to segment customers and predict their spending habits, demonstrating a full data lifecycle from raw file ingestion to actionable business intelligence. 

![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=for-the-badge&logo=databricks&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-025E8C?style=for-the-badge&logo=microsoft-sql-server&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)

## 1. Project Overview

This repository documents a complete data engineering and data science project built on the **Databricks Lakehouse Platform**. The project analyzes a large, real-world e-commerce dataset from a UK-based online retailer to perform customer segmentation and predict customer spending.

The workflow demonstrates a full data lifecycle, tackling common data engineering challenges and delivering actionable business insights through advanced analytics and machine learning.

### Project Objectives:
* **Engineer a Reliable Data Pipeline:** Build a scalable, multi-stage pipeline to handle complex raw data, address quality issues, and prepare it for analysis.
* **Segment Customers:** Use RFM (Recency, Frequency, Monetary) analysis to group customers into meaningful segments (e.g., "Champions," "At Risk") that can inform targeted marketing strategies.
* **Predict Customer Value:** Develop a machine learning model to predict the potential monetary value of a customer based on their historical behavior.

---

## 2. The Databricks Platform & The Medallion Architecture

This project is built entirely on **Databricks**, a unified analytics platform that combines data warehousing and data lakes into a **Lakehouse**. This allows for a seamless transition from data engineering (using SQL and PySpark) to data science (using Python and ML libraries) in a single environment.

To ensure data quality and governance, the project is structured around the **Medallion Architecture**, an industry best practice for logically organizing data:

* **🥉 Bronze Layer:** Contains raw, unaltered data ingested directly from source systems. This is our source of truth.
* **🥈 Silver Layer:** Data from the Bronze layer is cleaned, validated, and enriched. This represents a trustworthy, analysis-ready version of the data.
* **🥇 Gold Layer:** Data from the Bronze layer is aggregated to serve specific business use cases, such as reporting and machine learning.



---

## 3. Project Workflow & Technical Explanations

### Phase 1: Ingestion (Bronze Layer)

The first and most critical challenge was ingesting the source data: a 43.51 MB multi-sheet Excel file (`.xlsx`).

**Challenge:** Standard data ingestion methods failed. Converting the Excel file to `.csv` resulted in silent data truncation, and the Databricks UI for table creation does not support `.xlsx` files.

**Solution:** The robust solution was to upload the original `.xlsx` file directly to a **Databricks Volume**. A Volume is a Unity Catalog object that allows you to store and access files of any format in cloud object storage.

![Uploading the raw .xlsx file to a Databricks Volume](./Screenshot%202025-10-17%20114844.png)

A Python script using `pandas` and `PySpark` was then used to read each sheet directly from the Excel file. This process required explicitly defining data types (`dtype`) for mixed-type columns to prevent `PySparkTypeError` exceptions, ensuring no data was lost. The data from both sheets was then combined and saved as a single, complete `bronze_online_retail` Delta table.

![The final Bronze table in the Databricks Catalog, containing all 1,067,371 raw records](./Bronze-.jpg)

### Phase 2: Cleansing & Enrichment (Silver Layer)

The raw bronze data was transformed into a clean Silver table using a single SQL query. This query applied key business rules to ensure data quality:

1.  **Filtering:** Records with `NULL` `CustomerID`s were removed, as they are unusable for customer-level analysis. Transactions that were returns (where `Quantity < 0`) were also filtered out.
2.  **Enrichment:** A new `TotalPrice` column was created by multiplying `Quantity` by `Price` to calculate the value of each transaction line.

The result is the `silver_online_retail` Delta table: a clean, trustworthy source for all future analysis, containing 824,364 valid transactions.

![The clean Silver table in the Databricks Catalog](./Silver_Tier.jpg)

### Phase 3: Aggregation & Segmentation (Gold Layer)

The goal of the Gold layer is to create business-level insights. We used SQL to perform **RFM (Recency, Frequency, Monetary) analysis** to segment customers.

This involved two SQL queries:
1.  **RFM Scoring:** An initial query aggregated the clean silver data by `CustomerID` to calculate their `Recency`, `Frequency`, and `Monetary` values. The `NTILE(4)` window function was used to assign a score from 1 to 4 for each of these metrics.
2.  **Segmentation:** A final query used a `CASE` statement to apply business logic to these scores, assigning human-readable segments like "Champions," "At Risk," and "Loyal Customers."

This final `gold_customer_segments` table is what a marketing team would use to run targeted campaigns.

![The final Gold table showing the SQL CASE statement and the resulting "Customer_Segment"](./Gold_Tier_DB.jpg)

### Phase 4: Visualization & Predictive Modeling

The final step was to perform data science on our Gold RFM table using Python in a Databricks notebook.

#### Data Visualization
First, we visualized the distributions of our RFM variables. The histograms revealed that `Frequency` and `Monetary` were heavily skewed (a common pattern in retail data), so a log transformation was used to make patterns more visible for analysis.

![Histograms of Recency, Frequency (Log-Transformed), and Monetary (Log-Transformed)](./Data_Visualization_1.png)

#### Predictive Modeling
A **Linear Regression** model was trained using `scikit-learn` to predict a customer's `Monetary` value based on their `Recency` and `Frequency`. The model was trained on 80% of the data and tested on the remaining 20%.

![The Python code in Databricks for training the Linear Regression model](./Screenshot%202025-10-17%20114614.jpg)

## 4. Conclusion: Model Performance

The model's performance was evaluated by plotting its `Predicted Monetary Value` (Y-axis) against the `Actual Monetary Value` (X-axis) for the held-out test set.

![Final model performance, plotting Actual vs. Predicted customer spending](./Model_Scatter_Plot_Actual_vs_Predicted.png)

**Analysis:** The red dashed line represents a perfect prediction (`y=x`). The cluster of blue dots shows that our model successfully learned the general relationship between customer behavior and spending, as its predictions follow this line. While the model is less accurate for high-value outliers (a known limitation of simple linear models), it provides a strong baseline for forecasting the potential value of new or promising customers. This allows the business to focus its marketing efforts effectively and make data-driven decisions.
