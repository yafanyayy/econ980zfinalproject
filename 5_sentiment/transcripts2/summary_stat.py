import pandas as pd

# Load the dataset
file_path = "summaryPtranscripts2_with_friday_label_and_speaker_stats.xlsx"
data = pd.read_excel(file_path)

# Debug: Print column names to verify
print("Column names in the dataset:")
print(data.columns)

# Columns to include in the summary
columns_to_summarize = [
    'operator_word_count', 'operator_avg_sentiment',
    'executives_word_count', 'executives_avg_sentiment',
    'analysts_word_count', 'analysts_avg_sentiment'
]

# Calculate means for all rows
overall_mean = data[columns_to_summarize].mean()

# Calculate means for Friday rows
friday_mean = data[data['friday_label'] == 1][columns_to_summarize].mean()

# Calculate means for non-Friday rows
non_friday_mean = data[data['friday_label'] == 0][columns_to_summarize].mean()

# Combine results into a single DataFrame
summary_stats = pd.DataFrame({
    'Overall Mean': overall_mean,
    'Friday Mean': friday_mean,
    'Non-Friday Mean': non_friday_mean
}).T

# Save the summary statistics to a LaTeX file with a two-row header
latex_file_path = "summary_statistics.tex"
with open(latex_file_path, 'w') as f:
    f.write(r"""
\begin{table}[h!]
\centering
\caption{Summary Statistics for Sentiment and Word Count}
\begin{tabular}{lcccccc}
\toprule
 & \multicolumn{2}{c}{Operator} & \multicolumn{2}{c}{Executives} & \multicolumn{2}{c}{Analysts} \\
\cmidrule(lr){2-3} \cmidrule(lr){4-5} \cmidrule(lr){6-7}
 & Word Count & Sentiment & Word Count & Sentiment & Word Count & Sentiment \\
\midrule
""")
    # Write the data rows
    for index, row in summary_stats.iterrows():
        f.write(f"{index} & " + " & ".join(f"{value:.4f}" for value in row) + r" \\" + "\n")
    f.write(r"""
\bottomrule
\end{tabular}
\end{table}
""")

print(f"Summary statistics saved to {latex_file_path}")