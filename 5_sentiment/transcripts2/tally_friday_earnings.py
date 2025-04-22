import os
import pandas as pd
from datetime import datetime

# Directory containing the year folders
base_dir = "/Users/yafan/Desktop/Econ 980Z/final_project/5_sentiment/transcripts2"

# Initialize counters
total_earnings_calls = 0
friday_earnings_calls = 0
non_friday_earnings_calls = 0

# List to store summary data
summary_data = []

# Iterate through each year folder (2011 to 2022)
for year in range(2011, 2023):
    year_folder = os.path.join(base_dir, str(year))
    if not os.path.exists(year_folder):
        continue  # Skip if the folder doesn't exist

    # Iterate through each file in the year folder
    for file_name in os.listdir(year_folder):
        if file_name.endswith(".csv"):  # Process only CSV files
            file_path = os.path.join(year_folder, file_name)
            
            # Load the CSV file into a DataFrame
            try:
                df = pd.read_csv(file_path)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

            # Check if the 'mostimportantdateutc' column exists
            if 'mostimportantdateutc' not in df.columns:
                print(f"'mostimportantdateutc' column not found in {file_path}")
                continue

            # Extract unique dates from the 'mostimportantdateutc' column
            df['mostimportantdateutc'] = pd.to_datetime(df['mostimportantdateutc'], errors='coerce')
            unique_dates = df['mostimportantdateutc'].dropna().dt.date.unique()

            # Tally the dates and collect summary data
            for date in unique_dates:
                total_earnings_calls += 1
                is_friday = datetime.strptime(str(date), "%Y-%m-%d").weekday() == 4  # Friday is weekday 4
                if is_friday:
                    friday_earnings_calls += 1
                else:
                    non_friday_earnings_calls += 1

                # Collect summary data for each unique date
                subset = df[df['mostimportantdateutc'].dt.date == date]
                if not subset.empty:
                    summary_data.append({
                        'companyid': subset['companyid'].iloc[0],
                        'keydevid': subset['keydevid'].iloc[0],
                        'transcriptid': subset['transcriptid'].iloc[0],
                        'keydeveventtypename': subset['keydeveventtypename'].iloc[0],
                        'companyname': subset['companyname'].iloc[0],
                        'date': date,
                        'friday_label': 1 if is_friday else 0
                    })

# Print the results
print("Earnings Call Statistics:")
print(f"Total Earnings Calls: {total_earnings_calls}")
print(f"Earnings Calls on Fridays: {friday_earnings_calls}")
print(f"Earnings Calls on Other Days: {non_friday_earnings_calls}")

# Save the summary data to an Excel file
summary_df = pd.DataFrame(summary_data)
output_file = "summaryPtranscripts2_with_friday_label.xlsx"
summary_df.to_excel(output_file, index=False)
print(f"Summary saved to {output_file}.")