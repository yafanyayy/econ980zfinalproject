import pandas as pd

# Load data
df = pd.read_excel("../0_raw_company_list/EarningsSearchesDec06.xls")  

# Make sure dates are in datetime format
df['t_ibes'] = pd.to_datetime(df['t_ibes'], errors='coerce')
df['t_predict'] = pd.to_datetime(df['t_predict'], errors='coerce')
df['t_newswires'] = pd.to_datetime(df['t_newswires'], errors='coerce')

# Label based on the preferred announcement date (e.g., t_ibes or t_predict)
df['announcement_weekday'] = df['t_newswires'].dt.weekday

# Create indicator variable for Friday (1) vs Non-Friday (0)
df['Friday_Label'] = df['announcement_weekday'].apply(lambda x: 1 if x == 4 else 0)

# Generate the summary table
weekday_counts = df['announcement_weekday'].value_counts().sort_index()
weekday_fractions = weekday_counts / weekday_counts.sum()

# Create a DataFrame for the summary table
summary_table = pd.DataFrame({
    'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
    'Number': weekday_counts.values,
    'Fraction': weekday_fractions.values
})
# Add a row for totals (All)
summary_table.loc[len(summary_table)] = ['All', weekday_counts.sum(), 1.0]

# Transpose the table so days of the week are column headers
transposed_table = summary_table.set_index('Day').T

# Check the labeling
print(df[['t_newswires', 'Friday_Label']].head())

df.to_excel("Labeled_EarningsSearches.xlsx", index=False)
summary_table.to_excel("Earnings_Distribution_By_Day.xlsx", index=False)

# Generate LaTeX table
latex_table = transposed_table.to_latex(index=False, float_format="%.4f", caption="Distribution of Earnings Announcements by Day of the Week", label="tab:earnings_distribution")
with open("Earnings_Distribution_By_Day.tex", "w") as f:
    f.write(latex_table)

# Print the LaTeX table
print("LaTeX Table:")
print(latex_table)

