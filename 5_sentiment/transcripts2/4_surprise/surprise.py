import wrds
import pandas as pd
from datetime import datetime, timedelta

# Connect to WRDS
db = wrds.Connection(wrds_username='wangyafan')

# Read the input Excel file
input_file = "../3_match/matches_cleaned.xlsx"  
data = pd.read_excel(input_file)

# Initialize a list to store surprise values
surprise_values = []

# Iterate through each row in the DataFrame
for index, row in data.iterrows():
    try:
        # Extract permno, cusip, and announcement date from the current row
        permno = row['permno']
        cusip = row['cusip']
        announce_date = row['date']

        # Ensure announce_date is in the correct format
        if isinstance(announce_date, pd.Timestamp):
            announce_date = announce_date.strftime('%Y-%m-%d %H:%M:%S')

        # -----------------------------
        # 1. Get IBES Estimates (EPS)
        # -----------------------------
        ibes_sample_query = f"""
            SELECT *
            FROM ibes.det_epsus
            WHERE cusip = '{cusip}'
            AND anndats_act = '{announce_date}'
            AND fpi = '6' -- Quarterly EPS
        """
        ibes_sample = db.raw_sql(ibes_sample_query)

        if not ibes_sample.empty:
            # Calculate the median of the 'value' column (median estimate)
            median_value = ibes_sample['value'].median()

            # -----------------------------
            # 2. Get Actual EPS
            # -----------------------------
            actual_eps_query = f"""
                SELECT anndats, value AS actual_eps
                FROM ibes.act_epsus
                WHERE cusip = '{cusip}'
                AND anndats = '{announce_date}'
                LIMIT 1
            """
            actual_eps = db.raw_sql(actual_eps_query)

            if not actual_eps.empty:
                # Get the actual EPS value
                actual = actual_eps.iloc[0]['actual_eps']

                # -----------------------------
                # 3. Get Current Share Price (3 Days Before Announcement Date)
                # -----------------------------
                price_date = (datetime.strptime(announce_date.split(" ")[0], '%Y-%m-%d') - timedelta(days=3)).strftime('%Y-%m-%d')

                price_query = f"""
                    SELECT date, prc
                    FROM crsp.dsf
                    WHERE permno = {permno}
                    AND date = '{price_date}'
                """
                price_result = db.raw_sql(price_query)

                # If no price is found for the exact date, try the day before or after
                if price_result.empty:
                    adjusted_date = None
                    for offset in [-1, 1]:  # Check the day before and the day after the 3-day offset
                        adjusted_date = (datetime.strptime(price_date, '%Y-%m-%d') + timedelta(days=offset)).strftime('%Y-%m-%d')
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
                    surprise = (actual - median_value) / price
                    surprise_values.append(surprise)
                else:
                    # If no price is found, append NaN
                    surprise_values.append(None)
            else:
                # If actual EPS is missing, append NaN
                surprise_values.append(None)
        else:
            # If IBES sample is empty, append NaN
            surprise_values.append(None)
    except Exception as e:
        # If any error occurs, append NaN and print the error for debugging
        surprise_values.append(None)
        print(f"Error processing row {index}: {e}")

# Ensure the length of surprise_values matches the number of rows in data
if len(surprise_values) != len(data):
    print(f"Warning: Length mismatch! surprise_values: {len(surprise_values)}, data: {len(data)}")

# Add the surprise values as a new column to the DataFrame
data['surprise'] = surprise_values

# Save the updated DataFrame to a new Excel file
output_file = "surprise.xlsx"
data.to_excel(output_file, index=False)
print(f"Updated file with surprise values saved to {output_file}.")