import wrds
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Connect to WRDS
db = wrds.Connection(wrds_username='wangyafan')

# Input parameters for a single company
permno = 86431  # Example permno
cusip = '01662K10'  # Example cusip
t_ibes = '1994-04-08 00:00:00'  # Example t_ibes date

# Ensure t_ibes is in the correct format
if isinstance(t_ibes, pd.Timestamp):
    t_ibes = t_ibes.strftime('%Y-%m-%d')
else:
    t_ibes = t_ibes.split(" ")[0]  # Extract the date part if it's a string with time

# Initialize variables
mean_value = None
actual_eps = None
price = None
surprise = None

# Query IBES for mean EPS estimates
ibes_query = f"""
    SELECT value
    FROM ibes.det_epsus
    WHERE cusip = '{cusip}'
    AND anndats_act = '{t_ibes}'
    AND fpi = '6' -- Quarterly EPS
"""
ibes_result = db.raw_sql(ibes_query)
print(f"IBES result: {ibes_result}")  # Debugging line to check the IBES result
if not ibes_result.empty:
    mean_value = ibes_result['value'].mean()  # Calculate the mean EPS estimate

    # Query IBES for actual EPS
    actual_eps_query = f"""
        SELECT value AS actual_eps
        FROM ibes.act_epsus
        WHERE cusip = '{cusip}'
        AND anndats = '{t_ibes}'
        LIMIT 1
    """
    actual_eps_result = db.raw_sql(actual_eps_query)

    if not actual_eps_result.empty:
        actual_eps = actual_eps_result.iloc[0]['actual_eps']

        # Query CRSP for price on the exact t_ibes date
        price_query = f"""
            SELECT date, prc
            FROM crsp.dsf
            WHERE permno = {permno}
            AND date = '{t_ibes}'
        """
        price_result = db.raw_sql(price_query)

        # If no price is found, try the day before and the day after
        if price_result.empty:
            for offset in [-1, 1]:  # Check the day before and the day after
                adjusted_date = (datetime.strptime(t_ibes, '%Y-%m-%d') + timedelta(days=offset)).strftime('%Y-%m-%d')
                price_query = f"""
                    SELECT date, prc
                    FROM crsp.dsf
                    WHERE permno = {permno}
                    AND date = '{adjusted_date}'
                """
                price_result = db.raw_sql(price_query)
                if not price_result.empty:
                    break  # Exit the loop if a price is found

        # Calculate surprise if price is available
        if not price_result.empty:
            price = abs(price_result.iloc[0]['prc'])  # Use abs(price) to handle negative prices
            surprise = (actual_eps - mean_value) / price
            print(f"Mean EPS estimate for cusip {cusip} on {t_ibes}: {mean_value}")
            print(f"Actual EPS for cusip {cusip} on {t_ibes}: {actual_eps}")
            print(f"Price for permno {permno} on {t_ibes}: {price}")
            print(f"Surprise for permno {permno} on {t_ibes}: {surprise}")
        else:
            print(f"No price data available for permno {permno} on {t_ibes} or nearby dates.")
    else:
        print(f"No actual EPS data available for cusip {cusip} on {t_ibes}.")
else:
    print(f"No IBES EPS estimates available for cusip {cusip} on {t_ibes}.")