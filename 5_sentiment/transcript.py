import pandas as pd
import wrds

# Connect to WRDS
db = wrds.Connection(wrds_username='wangyafan ') 

# Load the dataset
file_path = "../4_earning_regression/labeled_earningsearch_with_returns_and_abnormal.xlsx"
data = pd.read_excel(file_path)

# Initialize a list to store transcripts
transcripts = []
# List all available libraries
libraries = db.list_libraries()
# print("Available Libraries:", libraries)

# # List all tables in the 'ciq' library
# ciq_tables = db.list_tables(library='ciq')
# print("Available Tables in CIQ Library:", ciq_tables)
transcript_columns = db.get_table(library='ciq', table='ciqtranscript')
print(transcript_columns)
transcript_sample = db.raw_sql("SELECT * FROM ciq.ciqtranscript LIMIT 5")
print(transcript_sample)
# Iterate through each row in the dataset
for index, row in data.iterrows():
    permno = row['permno']
    cusip = row['cusip']

    # Query the transcript from Compustat Capital IQ using permno or cusip
    transcript_query = f"""
        SELECT *
        FROM ciqtranscripts
        WHERE gvkey IN (
            SELECT gvkey
            FROM crsp.ccmxpf_linktable
            WHERE lpermno = {permno} OR cusip = '{cusip}'
        )
        LIMIT 1
    """
    transcript_result = db.raw_sql(transcript_query)

    # Check if a transcript was found
    if not transcript_result.empty:
        # Store the transcript text in the list
        transcripts.append(transcript_result['transcript_text'].iloc[0])
    else:
        # If no transcript is found, append None
        transcripts.append(None)

# Add the transcripts as a new column to the DataFrame
data['transcript'] = transcripts

# Save the updated DataFrame to a new Excel file
output_file = "labeled_earningsearch_with_transcripts.xlsx"
data.to_excel(output_file, index=False)
print(f"Updated file with transcripts saved to {output_file}.")