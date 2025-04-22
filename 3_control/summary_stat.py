import pandas as pd

# Load the Excel file
file_path = "labeled_earningsearch_with_log_market_cap_nearby_dates.xlsx"
df = pd.read_excel(file_path)

# Ensure the relevant columns are present
required_columns = ['Friday_Label', 'surprise', 'log_market_cap', 't_newswires']
for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"Missing required column: {col}")

# Extract the year from the 't_newswires' column
df['year'] = pd.to_datetime(df['t_newswires'], errors='coerce').dt.year

# Filter data for Friday and Non-Friday
friday_data = df[df['Friday_Label'] == 1]
non_friday_data = df[df['Friday_Label'] == 0]

# Calculate summary statistics (mean with standard deviation in parentheses)
summary_stats = {
    'Metric': ['Earnings Surprise', 'Log Market Cap', 'Year', 'N'],
    'Friday': [
        f"{friday_data['surprise'].mean():.4f}\n({friday_data['surprise'].std():.4f})",
        f"{friday_data['log_market_cap'].mean():.4f}\n({friday_data['log_market_cap'].std():.4f})",
        f"{friday_data['year'].mean():.4f}\n({friday_data['year'].std():.4f})",
        f"{len(friday_data)}"
    ],
    'Non-Friday': [
        f"{non_friday_data['surprise'].mean():.4f}\n({non_friday_data['surprise'].std():.4f})",
        f"{non_friday_data['log_market_cap'].mean():.4f}\n({non_friday_data['log_market_cap'].std():.4f})",
        f"{non_friday_data['year'].mean():.4f}\n({non_friday_data['year'].std():.4f})",
        f"{len(non_friday_data)}"
    ],
    'Difference': [
        f"{(friday_data['surprise'].mean() - non_friday_data['surprise'].mean()):.4f}",
        f"{(friday_data['log_market_cap'].mean() - non_friday_data['log_market_cap'].mean()):.4f}",
        f"{(friday_data['year'].mean() - non_friday_data['year'].mean()):.4f}",
        f"{len(friday_data) + len(non_friday_data)}"  # Total sample size
    ]
}

# Create a DataFrame for the summary table
summary_table = pd.DataFrame(summary_stats)

# Save the summary table to an Excel file
output_file = "/Users/yafan/Desktop/Econ 980Z/final_project/3_control/summary_statistics_with_std_combined.xlsx"
summary_table.to_excel(output_file, index=False)
print(f"Summary table saved to {output_file}")

# Generate LaTeX table
latex_table = summary_table.to_latex(index=False, caption="Summary Statistics for Friday vs Non-Friday Earnings Announcements (with Standard Deviations)", label="tab:summary_statistics_with_std_combined", escape=False)
latex_output_file = "/Users/yafan/Desktop/Econ 980Z/final_project/3_control/summary_statistics_with_std_combined.tex"
with open(latex_output_file, "w") as f:
    f.write(latex_table)
print(f"LaTeX table saved to {latex_output_file}")

# Print the LaTeX table
print("LaTeX Table:")
print(latex_table)