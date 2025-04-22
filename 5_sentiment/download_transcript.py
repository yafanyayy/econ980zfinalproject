import pandas as pd
import requests
import os
from datetime import datetime

# Load the filtered data
file_path = "filtered_nonna_data.xlsx"
filtered_df = pd.read_excel(file_path)

# Limit to the first 500 rows
filtered_df = filtered_df.iloc[:500]

# Helper function to compute the 9th digit of CUSIP
def compute_cusip_check(cusip8: str) -> str:
    mapping = {**{str(i): i for i in range(10)},
               **{chr(i): i - 55 for i in range(65, 91)},  # A=10, B=11, ..., Z=35
               '*': 36, '@': 37, '#': 38}
    total = 0
    for idx, char in enumerate(cusip8, start=1):
        if char not in mapping:
            raise ValueError(f"Invalid CUSIP character: {char}")
        val = mapping[char]
        if idx % 2 == 0:
            val *= 2
        val = (val // 10) + (val % 10)
        total += val
    check_digit = (10 - (total % 10)) % 10
    return str(check_digit)

# Initialize folder for saving transcripts
output_folder = "transcripts"
os.makedirs(output_folder, exist_ok=True)

# FMP API Key
API_KEY = "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"
year = 2024
quarter =1 
symbol = "AAPL"
url = f"https://financialmodelingprep.com/api/v3/earning_call_transcript/{symbol}?year={year}&quarter={quarter}&apikey={API_KEY}"
response = requests.get(url)
print("test", response.json())
# Loop through each entry in the filtered DataFrame
for idx, row in filtered_df.iterrows():
    cusip_base = str(row['cusip']).zfill(8)
    try:
        cusip_full = cusip_base + compute_cusip_check(cusip_base)
    except ValueError as e:
        print(f"Skipping row {idx}: {e}")
        continue

    # Fetch symbol using FMP CUSIP search API
    try:
        resp = requests.get(f"https://financialmodelingprep.com/stable/search-cusip?cusip={cusip_full}&apikey={API_KEY}")
        data = resp.json()
        print(f"API response for CUSIP {cusip_full}: {data}")
    except Exception as e:
        print(f"API request failed for CUSIP {cusip_full}: {e}")
        continue
    if not data:
        print(f"No symbol found for CUSIP {cusip_full}")
        continue
    symbol = data[0].get('symbol')
    if not symbol:
        print(f"No symbol in response for CUSIP {cusip_full}")
        continue


    # Fetch earnings call transcript from FMP API
    try:
        url = f"https://financialmodelingprep.com/api/v3/earning_call_transcript/{symbol}?year={call_year}&quarter={call_quarter}&apikey={API_KEY}"
        resp = requests.get(url)
        transcript_data = resp.json()
    except Exception as e:
        print(f"Transcript API request failed for {symbol} {call_year} Q{call_quarter}: {e}")
        continue
    if not transcript_data:
        print(f"No transcript found for {symbol} {call_year} Q{call_quarter}")
        continue

    # Save the transcript as a text file
    transcript_entry = transcript_data[0]
    transcript_text = transcript_entry.get('content', '')
    output_file = os.path.join(output_folder, f"{symbol}_{call_year}_Q{call_quarter}.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transcript_text)
    print(f"Transcript saved to {output_file}.")