# --- Ensure this path is correct ---
excel_file_path = "/Volumes/workspace/default/retail_data/online_retail_II.xlsx"
# ------------------------------------

# 1. Install library for reading Excel
import pandas as pd

# 2. Define data types for ALL problem columns
col_types = {
    'Invoice': str,
    'StockCode': str,
    'Customer ID': str,  # Use the original name with the space
    'Description': str
}

# 3. Read 'Year 2009-2010' sheet
print("Reading first sheet...")
pandas_df1 = pd.read_excel(excel_file_path, 
                           sheet_name='Year 2009-2010',
                           dtype=col_types)
spark_df1 = spark.createDataFrame(pandas_df1)

# 4. Read 'Year 2010-2011' sheet
print("Reading second sheet...")
pandas_df2 = pd.read_excel(excel_file_path, 
                           sheet_name='Year 2010-2011',
                           dtype=col_types)
spark_df2 = spark.createDataFrame(pandas_df2)

# 5. Combine (union) them
print("Combining data...")
raw_df = spark_df1.unionByName(spark_df2)

# 6. Fix the bad column name
raw_df_renamed = raw_df.withColumnRenamed("Customer ID", "CustomerID")

# 7. Save the final Bronze table
print("Saving Bronze table...")
bronze_table_name = "bronze_online_retail"
raw_df_renamed.write.format("delta").mode("overwrite").saveAsTable(bronze_table_name)

print(f"--- SUCCESS! ---")
print(f"Bronze table '{bronze_table_name}' is created and has {raw_df_renamed.count()} total rows.")

# 1. Install necessary libraries
#%pip install scikit-learn matplotlib seaborn

import pandas as pd
import numpy as np  # <-- THE FIX: Import numpy directly
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# 2. Load our gold table into a pandas DataFrame
pdf = spark.table("gold_customer_rfm").toPandas()

# 3. Print the head() of the data
print("--- Head of gold_customer_rfm Table ---")
print(pdf.head())
print("\n")


# --- DATA VISUALIZATION ---

print("--- Data Visualizations ---")

# Plot 1: Histograms to show data distributions
# We take the log of Monetary and Frequency for better visualization,
# as they are highly skewed (many small values, few very large ones)

# <-- THE FIX: Use np.log1p instead of pd.np.log1p
pdf['Monetary_log'] = np.log1p(pdf['Monetary'])
pdf['Frequency_log'] = np.log1p(pdf['Frequency'])

plt.figure(figsize=(18, 5))

# Plot for Recency
plt.subplot(1, 3, 1)
sns.histplot(pdf['Recency'], kde=True)
plt.title('Distribution of Recency (Days)')

# Plot for Frequency (Log-transformed)
plt.subplot(1, 3, 2)
sns.histplot(pdf['Frequency_log'], kde=True, color='orange')
plt.title('Distribution of Frequency (Log-Transformed)')

# Plot for Monetary (Log-transformed)
plt.subplot(1, 3, 3)
sns.histplot(pdf['Monetary_log'], kde=True, color='green')
plt.title('Distribution of Monetary (Log-Transformed)')

plt.suptitle('Histograms of RFM Variables')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()


# Plot 2: Scatter plots to show relationships
plt.figure(figsize=(15, 6))

# Plot for Recency vs Monetary
plt.subplot(1, 2, 1)
sns.scatterplot(data=pdf, x='Recency', y='Monetary_log')
plt.title('Recency vs. Monetary (Log-Transformed)')
plt.xlabel('Recency (Days)')
plt.ylabel('Monetary (Log-Transformed)')

# Plot for Frequency vs Monetary
plt.subplot(1, 2, 2)
sns.scatterplot(data=pdf, x='Frequency_log', y='Monetary_log')
plt.title('Frequency (Log-Transformed) vs. Monetary (Log-Transformed)')
plt.xlabel('Frequency (Log-Transformed)')
plt.ylabel('Monetary (Log-Transformed)')

plt.suptitle('Feature vs. Target Relationships')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()


# --- MODEL TRAINING ---

# 4. Define our features (what we use to predict)
# We'll use the original (non-log) values for the model
features = ['Recency', 'Frequency']
X = pdf[features]

# 5. Define our target (what we WANT to predict)
target = 'Monetary'
y = pdf[target]

# 6. Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 7. Create and train the model
model = LinearRegression()
model.fit(X_train, y_train)

print("\n--- Machine Learning Model Trained Successfully ---")
print(f"Model formula: Monetary = (Recency * {model.coef_[0]:.2f}) + (Frequency * {model.coef_[1]:.2f}) + {model.intercept_:.2f}\n")


# --- MODEL EVALUATION PLOT ---

# 8. Get the model's predictions on the test set
y_pred = model.predict(X_test)

# Plot 3: Scatter plot of Actual vs. Predicted values
plt.figure(figsize=(8, 8))
plt.scatter(y_test, y_pred, alpha=0.3)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], '--r', linewidth=2) # Perfect prediction line
plt.title('Model Performance: Actual vs. Predicted Monetary Value')
plt.xlabel('Actual Monetary Value (Test Set)')
plt.ylabel('Predicted Monetary Value')
plt.show()