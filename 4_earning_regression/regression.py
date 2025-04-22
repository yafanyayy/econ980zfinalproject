import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Load the main dataset
file_path = "75.xlsx"
data = pd.read_excel(file_path)

# Drop rows with missing values for surprise, immediate_return, drift_return, or log_market_cap
data_cleaned = data.dropna(subset=['surprise', 'immediate_return', 'drift_return_75', 'log_market_cap'])

# Rename drift_return to drift for clarity
data_cleaned.rename(columns={'drift_return_75': 'drift'}, inplace=True)

# Run the first regression: immediate_return ~ surprise + Friday_Label + surprise:Friday_Label + log_market_cap
formula_immediate = "immediate_return ~ surprise + Friday_Label + surprise:Friday_Label + log_market_cap"
model_immediate = smf.ols(formula=formula_immediate, data=data_cleaned).fit()

# Run the second regression: drift ~ surprise + Friday_Label + surprise:Friday_Label + log_market_cap
formula_drift = "drift ~ surprise + Friday_Label + surprise:Friday_Label + log_market_cap"
model_drift = smf.ols(formula=formula_drift, data=data_cleaned).fit()

# Output regression tables to console
print("Regression Results: Immediate Return")
print(model_immediate.summary())

print("\nRegression Results: Drift (75 Days Return)")
print(model_drift.summary())

# Save regression results to a text file
with open("regression_results_with_log_market_cap.txt", "w") as f:
    f.write("Regression Results: Immediate Return\n")
    f.write(model_immediate.summary().as_text())
    f.write("\n\nRegression Results: Drift (75 Days Return)\n")
    f.write(model_drift.summary().as_text())

# Save regression results to LaTeX files
with open("immediate_return_regression.tex", "w") as f:
    f.write(model_immediate.summary().as_latex())

with open("drift_return_regression.tex", "w") as f:
    f.write(model_drift.summary().as_latex())

print("Regression results saved to LaTeX files: immediate_return_regression.tex and drift_return_regression.tex")