import wrds
import pandas as pd
import numpy as np

# Connect to WRDS
db = wrds.Connection(wrds_username='wangyafan')

# Input parameters for a single company
permno = 29947  # Example permno
t_ibes = '1986-07-24 00:00:00'  # Example t_ibes date

# Ensure t_ibes is in the correct format
if isinstance(t_ibes, pd.Timestamp):
    t_ibes = t_ibes.strftime('%Y-%m-%d')
else:
    t_ibes = t_ibes.split(" ")[0]  # Extract the date part if it's a string with time

# Query CRSP for price (prc) and shares outstanding (shrout) on the exact t_ibes date
query = f"""
    SELECT date, prc, shrout
    FROM crsp.dsf
    WHERE permno = {permno}
    AND date = '{t_ibes}'
"""
result = db.raw_sql(query)

# Calculate and print log(market cap) if data is available
if not result.empty:
    price = result.iloc[0]['prc']
    shares_outstanding = result.iloc[0]['shrout']
    market_cap = abs(price) * shares_outstanding  # Use abs(price) to handle negative prices
    log_market_cap = np.log(market_cap)
    print(f"Log(Market Cap) for permno {permno} on {t_ibes}: {log_market_cap}")
else:
    print(f"No data available for permno {permno} on {t_ibes}.")