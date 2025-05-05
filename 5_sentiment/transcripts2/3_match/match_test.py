import pandas as pd
from fuzzywuzzy import fuzz, process
import wrds

# Connect to WRDS
db = wrds.Connection(wrds_username='wangyafan')

# Read the input Excel file
file_path = "../1_sentiment/summaryPtranscripts2_with_friday_label_and_speaker_stats.xlsx"
data = pd.read_excel(file_path)

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

# Step 1: Get distinct company names
distinct_company_names = data['companyname'].dropna().unique()

# Step 2: Create a dictionary to store results
results_dict = {}

# Step 3: Perform matching for each distinct company name
for i, company_name in enumerate(distinct_company_names, start=1):
    print(f"Processing {i}/{len(distinct_company_names)}: {company_name}")
    # Initialize the result for this company
    results_dict[company_name] = {
        'company_name_ibes': None,
        'cusip': None,
        'permno': None,
        'company_name_crsp': None
    }

    # Exact match with IBES
    exact_match = ibes_data[ibes_data['cname'].str.lower() == company_name.lower()]
    if not exact_match.empty:
        results_dict[company_name]['company_name_ibes'] = exact_match['cname'].iloc[0]
        results_dict[company_name]['cusip'] = exact_match['cusip'].iloc[0]
    else:
        # Fuzzy match with IBES
        best_match = process.extractOne(company_name, ibes_company_names, scorer=fuzz.token_sort_ratio)
        if best_match:
            matched_name, score = best_match  # Unpack the tuple
            if score >= 80:  # Set a threshold for fuzzy matching
                matched_row = ibes_data[ibes_data['cname'] == matched_name]
                results_dict[company_name]['company_name_ibes'] = matched_row['cname'].iloc[0]
                results_dict[company_name]['cusip'] = matched_row['cusip'].iloc[0]

    # Exact match with CRSP
    exact_match_crsp = crsp_data[crsp_data['comnam'].str.lower() == company_name.lower()]
    if not exact_match_crsp.empty:
        results_dict[company_name]['permno'] = exact_match_crsp['permno'].iloc[0]
        results_dict[company_name]['company_name_crsp'] = exact_match_crsp['comnam'].iloc[0]
    else:
        # Fuzzy match with CRSP
        best_match_crsp = process.extractOne(company_name, crsp_company_names, scorer=fuzz.token_sort_ratio)
        if best_match_crsp:
            matched_name_crsp, score_crsp = best_match_crsp  # Unpack the tuple
            if score_crsp >= 80:  # Set a threshold for fuzzy matching
                matched_row_crsp = crsp_data[crsp_data['comnam'] == matched_name_crsp]
                results_dict[company_name]['permno'] = matched_row_crsp['permno'].iloc[0]
                results_dict[company_name]['company_name_crsp'] = matched_row_crsp['comnam'].iloc[0]

# Step 4: Map results back to the original DataFrame
data['company_name_ibes'] = data['companyname'].map(lambda x: results_dict[x]['company_name_ibes'] if x in results_dict else None)
data['cusip'] = data['companyname'].map(lambda x: results_dict[x]['cusip'] if x in results_dict else None)
data['permno'] = data['companyname'].map(lambda x: results_dict[x]['permno'] if x in results_dict else None)
data['company_name_crsp'] = data['companyname'].map(lambda x: results_dict[x]['company_name_crsp'] if x in results_dict else None)

# Save the updated DataFrame to a new Excel file
output_file = "matches_optimized.xlsx"
data.to_excel(output_file, index=False)
print(f"Updated file with IBES and CRSP matches saved to {output_file}.")