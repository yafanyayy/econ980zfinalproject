import pandas as pd

# Read the Excel file
file_path = "matches_optimized.xlsx"
data = pd.read_excel(file_path)

# Drop rows where 'cusip' or 'permno' are empty
cleaned_data = data.dropna(subset=['cusip', 'permno'])

# Output the number of rows left
print(f"Number of rows left after dropping rows with empty 'cusip' or 'permno': {len(cleaned_data)}")

# Count how many rows have '1' in the 'Friday_Label' column
friday_count = cleaned_data['friday_label'].sum()
print(f"Number of rows with '1' in 'friday_label': {friday_count}")

# Optionally, save the cleaned data to a new file
output_file = "matches_cleaned.xlsx"
cleaned_data.to_excel(output_file, index=False)
print(f"Cleaned data saved to {output_file}.")