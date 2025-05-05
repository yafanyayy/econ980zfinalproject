import wrds
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import statsmodels.api as sm
from scipy.stats import linregress

# Connect to WRDS
db = wrds.Connection(wrds_username='wangyafan')

# Read the input Excel file
file_path = "../3_control/labeled_earningsearch_with_log_market_cap_nearby_dates.xlsx"
data = pd.read_excel(file_path)

# Initialize lists to store calculated values
immediate_returns = []
company_drift_returns = []
betas = []
betas_1 = []
market_drift_returns = []
drift_returns = []

# Add a new column for beta_1 and set all values to 1
data['beta_1'] = 1

def get_trading_dates(db, start_date, num_days, direction="forward"):
    if direction == "forward":
        query = f"""
            SELECT date
            FROM crsp.dsf
            WHERE date >= '{start_date}'
            GROUP BY date
            ORDER BY date ASC
            LIMIT {num_days}
        """
    elif direction == "backward":
        query = f"""
            SELECT date
            FROM crsp.dsf
            WHERE date <= '{start_date}'
            GROUP BY date
            ORDER BY date DESC
            LIMIT {num_days}
        """
    trading_dates = db.raw_sql(query)
    if not trading_dates.empty:
        return trading_dates.iloc[-1]['date']
    else:
        return None

# Iterate through each row in the DataFrame
for index, row in data.iterrows():
    permno = row['permno']
    cusip = row['cusip']
    t_newswires = row['t_newswires']

    # Ensure t_newswires is in the correct format
    if isinstance(t_newswires, pd.Timestamp):
        t_newswires = t_newswires.strftime('%Y-%m-%d')

    # -----------------------------
    # Step 2: Calculate Returns
    # -----------------------------
    # Get trading dates for the immediate and drift periods
    date_before = get_trading_dates(db, t_newswires, 1, direction="backward")
    date_after = get_trading_dates(db, t_newswires, 1, direction="forward")
    date_2_days_after = get_trading_dates(db, t_newswires, 2, direction="forward")
    date_75_days_after = get_trading_dates(db, t_newswires, 75, direction="forward")

    # Query company and market returns for the immediate period
    query_immediate = f"""
        SELECT a.date, a.ret AS company_ret, b.vwretd  AS market_ret
        FROM crsp.dsf AS a
        JOIN crsp.dsi AS b ON a.date = b.date
        WHERE a.permno = {permno}
        AND a.date IN ('{date_before}', '{date_after}')
    """
    result_immediate = db.raw_sql(query_immediate)

    # Query company and market returns for the drift period
    query_drift = f"""
        SELECT a.date, a.ret AS company_ret, b.vwretd  AS market_ret
        FROM crsp.dsf AS a
        JOIN crsp.dsi AS b ON a.date = b.date
        WHERE a.permno = {permno}
        AND a.date BETWEEN '{date_2_days_after}' AND '{date_75_days_after}'
    """
    result_drift = db.raw_sql(query_drift)

    # Calculate immediate return using beta_1 (set to 1)
    beta_1 = row['beta_1']
    if not result_immediate.empty:
        try:
            ret_before_company = result_immediate[result_immediate['date'] == date_before]['company_ret'].iloc[0]
            ret_after_company = result_immediate[result_immediate['date'] == date_after]['company_ret'].iloc[0]
            ret_before_market = result_immediate[result_immediate['date'] == date_before]['market_ret'].iloc[0]
            ret_after_market = result_immediate[result_immediate['date'] == date_after]['market_ret'].iloc[0]

            # Calculate company and market immediate returns
            immediate_return_company = (1 + ret_after_company) * (1 + ret_before_company) - 1
            immediate_return_market = (1 + ret_after_market) * (1 + ret_before_market) - 1

            # Immediate return is the difference between company and market returns using beta_1
            immediate_return = immediate_return_company - beta_1 * immediate_return_market
            immediate_returns.append(immediate_return)
        except IndexError:
            immediate_returns.append(None)
    else:
        immediate_returns.append(None)

    if not result_drift.empty:
        # Initialize a list to store incremental cumulative returns
        cumulative_returns = []
    
        # Calculate cumulative company return incrementally
        cumulative_company_return = 1  # Start with 1 (no return yet)
        cumulative_market_return = 1  # Start with 1 (no return yet)
    
        for _, row in result_drift.iterrows():
            # Incrementally calculate cumulative returns
            cumulative_company_return *= (1 + row['company_ret'])
            cumulative_market_return *= (1 + row['market_ret'])
    
            # Calculate the abnormal return for the current day using beta_1
            cumulative_abnormal_return = cumulative_company_return - beta_1 * cumulative_market_return
    
            # Append the cumulative abnormal return to the list
            cumulative_returns.append(cumulative_abnormal_return)
    
        # Store the list of cumulative abnormal returns in the drift_returns list
        drift_returns.append(cumulative_returns)
    else:
        drift_returns.append(None)


# Add the calculated values as new columns to the DataFrame
data['immediate_return'] = immediate_returns
data['drift_return'] = drift_returns

# Save the updated DataFrame to a new Excel file
output_file = "labeled_earningsearch_with_abnormal_beta_1.xlsx"
data.to_excel(output_file, index=False)
print(f"Updated file with returns and abnormal returns using beta_1 saved to {output_file}.")