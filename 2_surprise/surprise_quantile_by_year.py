import pandas as pd

# Read the input file
input_file = "labeled_earningsearch_with_surprise_and_price.xlsx"
data = pd.read_excel(input_file)

# Ensure the 'surprise' column is numeric
data['surprise'] = pd.to_numeric(data['surprise'], errors='coerce')

# Extract the year from the 't_newswires' column
data['year'] = pd.to_datetime(data['t_newswires'], errors='coerce').dt.year

# Handle outliers: Winsorize the 'surprise' column (limit extreme values to the 1st and 99th percentiles)
data['surprise'] = data['surprise'].clip(lower=data['surprise'].quantile(0.01),
                                         upper=data['surprise'].quantile(0.99))

# Identify the most and second most negative surprises on Fridays
friday_data = data[data['Friday_Label'] == 1]
most_negative_surprise_row = friday_data.loc[friday_data['surprise'].idxmin()]
second_most_negative_surprise_row = friday_data.loc[friday_data['surprise'].nsmallest(2).idxmax()]

# Print the company names and surprises
most_negative_company = most_negative_surprise_row.get('companyname', 'Unknown Company')
most_negative_surprise = most_negative_surprise_row['surprise']
second_most_negative_company = second_most_negative_surprise_row.get('companyname', 'Unknown Company')
second_most_negative_surprise = second_most_negative_surprise_row['surprise']

print(f"Most negative surprise: {most_negative_company} with a surprise of {most_negative_surprise}")
print(f"Second most negative surprise: {second_most_negative_company} with a surprise of {second_most_negative_surprise}")

# Initialize an empty DataFrame to store results
quantile_data = pd.DataFrame()

# Process data year by year
for year, group in data.groupby('year'):
    # Separate the data into negative, zero, and positive surprises for the year
    negative_surprises = group[group['surprise'] < 0]
    zero_surprises = group[group['surprise'] == 0]
    positive_surprises = group[group['surprise'] > 0]

    # Assign quantiles for negative surprises (1-5)
    if not negative_surprises.empty:
        negative_surprises['surprise_quantile'] = pd.qcut(
            negative_surprises['surprise'], 5, labels=range(1, 6)
        )

    # Assign quantile 6 for zero surprises
    zero_surprises['surprise_quantile'] = 6

    # Assign quantiles for positive surprises (7-11)
    if not positive_surprises.empty:
        positive_surprises['surprise_quantile'] = pd.qcut(
            positive_surprises['surprise'], 5, labels=range(7, 12)
        )

    # Combine the data for the year
    year_data = pd.concat([negative_surprises, zero_surprises, positive_surprises])
    quantile_data = pd.concat([quantile_data, year_data])

# Save the updated DataFrame to a new Excel file
output_file = "labeled_earningsearch_with_surprise_and_quantiles_by_year.xlsx"
quantile_data.to_excel(output_file, index=False)
print(f"Updated file with surprise quantiles by year saved to {output_file}.")

# Calculate mean surprise for each quantile (all rows)
all_means = quantile_data.groupby('surprise_quantile')['surprise'].mean()

# Calculate mean surprise for each quantile where Friday_Label = 1 (Fridays)
friday_means = quantile_data[quantile_data['Friday_Label'] == 1].groupby('surprise_quantile')['surprise'].mean()

# Calculate mean surprise for each quantile where Friday_Label = 0 (Non-Fridays)
non_friday_means = quantile_data[quantile_data['Friday_Label'] == 0].groupby('surprise_quantile')['surprise'].mean()

# Calculate the total sample size (N) for each quantile
sample_sizes = quantile_data.groupby('surprise_quantile').size()

# Combine the results into a single DataFrame
summary_stats = pd.DataFrame({
    'Friday': friday_means,
    'Other Days': non_friday_means,
    'All': all_means,
    'N': sample_sizes
}).reset_index()

# Transpose the table for horizontal formatting
transposed_table = summary_stats.set_index('surprise_quantile').T

# Format the N row as integers (remove trailing zeros)
transposed_table.loc['N'] = transposed_table.loc['N'].astype(int)

# Save the transposed table to an Excel file
output_file_transposed = "summary_statistics_surprise_quantiles_transposed.xlsx"
transposed_table.to_excel(output_file_transposed)
print(f"Transposed summary statistics saved to {output_file_transposed}.")

# Generate a normal LaTeX table and save it directly to a file
latex_output_file = "summary_statistics_surprise_quantiles_transposed_winsorized.tex"
with open(latex_output_file, "w") as f:
    f.write(
        "\\begin{table}[ht]\n"
        "\\centering\n"
        "\\resizebox{\\textwidth}{!}{%\n"
        "\\begin{tabular}{l" + "r" * len(transposed_table.columns) + "}\n"
        "\\toprule\n"
        " & " + " & ".join(map(str, transposed_table.columns)) + " \\\\\n"
        "\\midrule\n"
        + "\n".join(
            f"{row} & " + " & ".join(f"{value:.4f}" if isinstance(value, float) else str(value) for value in transposed_table.loc[row])
            for row in transposed_table.index
        )
        + "\n\\bottomrule\n"
        "\\end{tabular}%\n"
        "}\n"
        "\\caption{Average Surprise by Earnings Surprise Quantile}\n"
        "\\label{tab:surprise_quantiles}\n"
        "\\end{table}\n"
    )
print(f"LaTeX table saved to {latex_output_file}")