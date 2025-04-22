import wrds
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Connect to WRDS
db = wrds.Connection(wrds_username='wangyafan')

# Read the input Excel file
input_file = "../2_surprise/labeled_earningsearch_with_surprise_and_quantiles_by_year.xlsx"  # Replace with the actual file name
data = pd.read_excel(input_file)

# Initialize a list to store log(market cap) values
log_market_cap = []

# Iterate through each row in the DataFrame
for index, row in data.iterrows():
    permno = row['permno']  # Extract permno
    t_ibes = row['t_ibes']  # Extract t_ibes date

    # Ensure t_ibes is in the correct format
    if isinstance(t_ibes, pd.Timestamp):
        t_ibes = t_ibes.strftime('%Y-%m-%d')

    # Try the exact t_ibes date first
    query = f"""
        SELECT date, prc, shrout
        FROM crsp.dsf
        WHERE permno = {permno}
        AND date = '{t_ibes}'
    """
    result = db.raw_sql(query)

    # If no data is found, try the day before
    if result.empty:
        t_ibes_before = (datetime.strptime(t_ibes, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        query = f"""
            SELECT date, prc, shrout
            FROM crsp.dsf
            WHERE permno = {permno}
            AND date = '{t_ibes_before}'
        """
        result = db.raw_sql(query)

    # If still no data, try the day after
    if result.empty:
        t_ibes_after = (datetime.strptime(t_ibes, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        query = f"""
            SELECT date, prc, shrout
            FROM crsp.dsf
            WHERE permno = {permno}
            AND date = '{t_ibes_after}'
        """
        result = db.raw_sql(query)

    # Calculate log(market cap) if data is available
    if not result.empty:
        price = result.iloc[0]['prc']
        shares_outstanding = result.iloc[0]['shrout']
        market_cap = abs(price) * shares_outstanding  # Use abs(price) to handle negative prices
        log_market_cap.append(np.log(market_cap))
    else:
        log_market_cap.append(None)  # Append None if no data is available

# Add the log(market cap) column to the DataFrame
data['log_market_cap'] = log_market_cap

# Save the updated DataFrame to a new Excel file
output_file = "labeled_earningsearch_with_log_market_cap_nearby_dates.xlsx"
data.to_excel(output_file, index=False)
print(f"Updated file with log(market cap) saved to {output_file}.")