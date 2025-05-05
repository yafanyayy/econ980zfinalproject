import pandas as pd

# Load the Excel file into a DataFrame
file_path = "../4_earning_regression/labeled_earningsearch_with_abnormal.xlsx"
df = pd.read_excel(file_path)

# Define a mask for non-missing announcement date (either t_ibes or t_newswires)
has_date = df['t_ibes'].notna() | df['t_newswires'].notna()
needed_cols = ['cusip', 'Friday_Label', 'immediate_return', 'drift_return', 'surprise']
has_others = df[needed_cols].notna().all(axis=1)

# Filter the DataFrame to include only rows with complete data
filtered_df = df[has_date & has_others].copy()

# Add a column for the quarter based on the announcement date
def determine_quarter(row):
    ann_date = row['t_newswires'] if pd.notna(row['t_newswires']) else row['t_ibes']
    if pd.isna(ann_date):
        return None  # Handle missing dates gracefully
    ann_date = pd.to_datetime(ann_date)
    ann_month = ann_date.month
    ann_year = ann_date.year
    if ann_month <= 3:
        return f"{ann_year - 1}_Q4"
    elif ann_month <= 6:
        return f"{ann_year}_Q1"
    elif ann_month <= 9:
        return f"{ann_year}_Q2"
    else:
        return f"{ann_year}_Q3"

filtered_df['quarter'] = filtered_df.apply(determine_quarter, axis=1)

# Save the filtered DataFrame to a new Excel file
output_file = "filtered_nonna_data_with_quarter.xlsx"
filtered_df.to_excel(output_file, index=False)
print(f"Filtered data with quarter column saved to {output_file}.")