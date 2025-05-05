import pandas as pd
from fuzzywuzzy import fuzz, process
import wrds

# Connect to WRDS
db = wrds.Connection(wrds_username='wangyafan')

# Read the input Excel file
file_path = "../1_sentiment/summaryPtranscripts2_with_friday_label_and_speaker_stats.xlsx"
data = pd.read_excel(file_path)

# Initialize new columns for IBES and CRSP matches
data['company_name_ibes'] = None
data['cusip'] = None
data['permno'] = None

# Fetch IBES company names and CUSIPs
ibes_query = """
    SELECT cname, cusip
    FROM ibes.idsum
"""
ibes_data = db.raw_sql(ibes_query)

# Fetch CRSP PERMNOs and company names
crsp_query = """
    SELECT permno, comnam
    FROM crsp.stocknames
"""
crsp_data = db.raw_sql(crsp_query)

# Ensure cname is a list or iterable
ibes_company_names = ibes_data['cname'].dropna().tolist()
# Ensure comnam is a list or iterable
crsp_company_names = crsp_data['comnam'].dropna().tolist()

# Perform exact and fuzzy matching for IBES and CRSP
for index, row in data.iterrows():
    company_name = row['companyname']

    # Exact match with IBES
    exact_match = ibes_data[ibes_data['cname'].str.lower() == company_name.lower()]
    if not exact_match.empty:
        data.at[index, 'company_name_ibes'] = exact_match['cname'].iloc[0]
        data.at[index, 'cusip'] = exact_match['cusip'].iloc[0]
    else:
        # Fuzzy match with IBES
        best_match = process.extractOne(company_name, ibes_company_names, scorer=fuzz.token_sort_ratio)
        if best_match:
            matched_name, score = best_match  # Unpack the tuple
            if score >= 80:  # Set a threshold for fuzzy matching
                matched_row = ibes_data[ibes_data['cname'] == matched_name]
                data.at[index, 'company_name_ibes'] = matched_row['cname'].iloc[0]
                data.at[index, 'cusip'] = matched_row['cusip'].iloc[0]
                
    # Exact match with CRSP
    exact_match_crsp = crsp_data[crsp_data['comnam'].str.lower() == company_name.lower()]
    if not exact_match_crsp.empty:
        data.at[index, 'permno'] = exact_match_crsp['permno'].iloc[0]
    else:
        # Fuzzy match with CRSP
        best_match_crsp = process.extractOne(company_name, crsp_company_names, scorer=fuzz.token_sort_ratio)
        if best_match_crsp:
            matched_name_crsp, score_crsp = best_match_crsp  # Unpack the tuple
            if score_crsp >= 80:  # Set a threshold for fuzzy matching
                matched_row_crsp = crsp_data[crsp_data['comnam'] == matched_name_crsp]
                data.at[index, 'permno'] = matched_row_crsp['permno'].iloc[0]
                
# Save the updated DataFrame to a new Excel file
output_file = "matches.xlsx"
data.to_excel(output_file, index=False)
print(f"Updated file with IBES and CRSP matches saved to {output_file}.")