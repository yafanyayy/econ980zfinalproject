from sec_edgar_downloader import Downloader
import pandas as pd
import os
from datetime import timedelta

# Load the dataset
file_path = "../4_earning_regression/labeled_earningsearch_with_returns_and_abnormal.xlsx"
data = pd.read_excel(file_path)

# Initialize the downloader
dl = Downloader("sec_edgar_filings", email_address="yafan_wang@college.harvard.edu")

# Limit to the first 10 rows for testing
data = data.head(10)

# Initialize a list to store downloaded filing paths
filing_paths = []

# Iterate through each row in the dataset
for index, row in data.iterrows():
    permno = row['permno']
    cusip = row['cusip']
    t_newswires = row['t_newswires']  # Announcement date

    # Ensure the date is in datetime format
    if not pd.isna(t_newswires):
        t_newswires = pd.to_datetime(t_newswires)

        # Define a search window (e.g., 5 days before and after the announcement date)
        start_date = t_newswires - timedelta(days=5)
        end_date = t_newswires + timedelta(days=5)

        # Use cusip or permno to identify the company (use cusip as an example here)
        ticker = cusip  # Replace with permno if needed

        # Download the latest 8-K filings for the company
        print(f"Downloading filings for cusip: {ticker}, Date Range: {start_date} to {end_date}")
        dl.get("8-K", ticker) 

        # Check the downloaded files
        download_path = os.path.join("sec_edgar_filings", ticker, "8-K")
        if os.path.exists(download_path):
            # Filter the filings by date
            relevant_filing = None
            for filing in os.listdir(download_path):
                filing_date = pd.to_datetime(filing.split("_")[0])  # Extract date from filename
                if start_date <= filing_date <= end_date:
                    relevant_filing = os.path.join(download_path, filing)
                    break  # Stop after finding the first relevant filing

            if relevant_filing:
                filing_paths.append(relevant_filing)
            else:
                filing_paths.append(None)
        else:
            filing_paths.append(None)
    else:
        print(f"Skipping row {index} due to missing t_newswires date.")
        filing_paths.append(None)

# Add the filing paths as a new column to the DataFrame
data['filing_path'] = filing_paths

# Save the updated DataFrame to a new Excel file
output_file = "labeled_earningsearch_with_filing_paths.xlsx"
data.to_excel(output_file, index=False)
print(f"Updated file with filing paths saved to {output_file}.")