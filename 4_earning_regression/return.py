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
market_drift_returns = []
drift_returns = []

# Function to get trading dates
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
    # Step 1: Calculate Beta
    # -----------------------------
    # Get trading dates for the beta calculation period (300 to 46 days before t_newswires)
    date_300_days_before = get_trading_dates(db, t_newswires, 300, direction="backward")
    date_46_days_before = get_trading_dates(db, t_newswires, 46, direction="backward")
    
    # # Debugging: Inspect the structure and contents of the crsp.dsi table
    # print("Fetching a sample of the crsp.dsi table to inspect its structure...")
    # dsi_sample_query = """
    #     SELECT date, vwretd
    #     FROM crsp.dsi
    #     LIMIT 5
    # """
    # dsi_sample = db.raw_sql(dsi_sample_query)
    # print("Sample of crsp.dsi table:")

    # print(dsi_sample.head())  # Print the first few rows of the table

    if date_300_days_before and date_46_days_before:
        # Query company and market returns for the beta calculation period
        beta_query = f"""
            SELECT a.date, a.ret AS company_ret, b.vwretd AS market_ret
            FROM crsp.dsf AS a
            JOIN crsp.dsi AS b ON a.date = b.date
            WHERE a.permno = {permno}
            AND a.date BETWEEN '{date_300_days_before}' AND '{date_46_days_before}'
        """
        beta_data = db.raw_sql(beta_query)


        beta_data['company_ret'] = pd.to_numeric(beta_data['company_ret'], errors='coerce')
        beta_data['market_ret'] = pd.to_numeric(beta_data['market_ret'], errors='coerce')
        beta_data = beta_data.replace([np.inf, -np.inf], np.nan).dropna(subset=['company_ret', 'market_ret'])
        
        if not beta_data.empty:
            # Run regression: company_ret ~ market_ret using scipy.stats.linregress
            X = beta_data['market_ret']
            y = beta_data['company_ret']
            slope, intercept, r_value, p_value, std_err = linregress(X, y)
            beta = slope  # The slope is the beta
            # print(f"Beta (slope): {beta}, Intercept: {intercept}, R-squared: {r_value**2}")
        else:
            beta = None
    else:
        beta = None

    betas.append(beta)

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

    # Calculate immediate return
    if not result_immediate.empty:
        try:
            ret_before_company = result_immediate[result_immediate['date'] == date_before]['company_ret'].iloc[0]
            ret_after_company = result_immediate[result_immediate['date'] == date_after]['company_ret'].iloc[0]
            ret_before_market = result_immediate[result_immediate['date'] == date_before]['market_ret'].iloc[0]
            ret_after_market = result_immediate[result_immediate['date'] == date_after]['market_ret'].iloc[0]

            # Calculate company and market immediate returns
            immediate_return_company = (1 + ret_after_company) * (1 + ret_before_company) - 1
            immediate_return_market = (1 + ret_after_market) * (1 + ret_before_market) - 1

            # Immediate return is the difference between company and market returns
            immediate_return = immediate_return_company - beta*immediate_return_market
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
    
            # Calculate the abnormal return for the current day
            cumulative_abnormal_return = cumulative_company_return - beta * cumulative_market_return
    
            # Append the cumulative abnormal return to the list
            cumulative_returns.append(cumulative_abnormal_return)
    
        # Store the list of cumulative abnormal returns in the drift_returns list
        drift_returns.append(cumulative_returns)
    else:
        drift_returns.append(None)


# Add the calculated values as new columns to the DataFrame
data['immediate_return'] = immediate_returns
data['drift_return'] = drift_returns
data['beta'] = betas

# Save the updated DataFrame to a new Excel file
output_file = "labeled_earningsearch_with_abnormal.xlsx"
data.to_excel(output_file, index=False)
print(f"Updated file with returns and abnormal returns saved to {output_file}.")