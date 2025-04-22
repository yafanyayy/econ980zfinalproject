import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col

# Load the dataset
file_path = "../75.xlsx"
data = pd.read_excel(file_path)

# -----------------------------
# Data Processing
# -----------------------------

# Define top and bottom quantiles
data['top_group'] = (data['surprise_quantile'] == 11).astype(int)  # Top quantile (11)
data['bottom_quantile'] = (data['surprise_quantile'] == 1).astype(int)  # Bottom quantile (1)
data['top_two_groups'] = ((data['surprise_quantile'] >= 10) & (data['surprise_quantile'] <= 11)).astype(int)  # Top two quantiles (10, 11)

# Calculate log_market_cap deviation from the average in the same quarter
data['year'] = pd.to_datetime(data['t_newswires']).dt.year
data['month'] = pd.to_datetime(data['t_newswires']).dt.month
data['quarter'] = (data['month'] - 1) // 3 + 1  # Calculate quarter
data['log_market_cap_dev'] = data['log_market_cap'] - data.groupby(['year', 'quarter'])['log_market_cap'].transform('mean')

# Calculate surprise volatility (standard deviation of surprise within each quarter)
data['surprise_volatility'] = data.groupby(['year', 'quarter'])['surprise'].transform('std')

# Drop rows with missing values for required variables
data_cleaned = data.dropna(subset=['immediate_return', 'drift_return_75', 'log_market_cap_dev', 'Friday_Label', 'surprise_volatility'])

# Define control variables
standard_controls = 'log_market_cap_dev + C(month) + C(year)'
surprise_vol_controls = 'surprise_volatility'

# -----------------------------
# Regression Specifications
# -----------------------------

specifications = [
    ('top_group', False, False, '11 Quantiles'),
    ('top_group', True, False, '11 Quantiles'),
    ('top_group', True, True, '11 Quantiles'),
    ('top_two_groups', False, False, '11 Quantiles'),
    ('top_two_groups', True, False, '11 Quantiles'),
    ('top_two_groups', True, True, '11 Quantiles')
]

# -----------------------------
# Function to Run Regressions
# -----------------------------

def run_regressions(dependent_var, data, specs):
    results = []
    for group_var, std_ctrl, vol_ctrl, sorting in specs:
        # Filter the dataset based on the specification
        if group_var == 'top_group':
            # Include only top group (11) and bottom group (1)
            filtered_data = data[(data['surprise_quantile'] == 11) | (data['surprise_quantile'] == 1)].copy()
            # Create indicator variable d_top: 1 for top group (11), 0 for bottom group (1)
            filtered_data['d_top'] = (filtered_data['surprise_quantile'] == 11).astype(int)
        elif group_var == 'top_two_groups':
            # Include only top two groups (10, 11) and bottom two groups (1, 2)
            filtered_data = data[(data['surprise_quantile'] >= 10) | (data['surprise_quantile'] <= 2)].copy()
            # Create indicator variable d_top_two: 1 for top two groups (10, 11), 0 for bottom two groups (1, 2)
            filtered_data['d_top_two'] = ((filtered_data['surprise_quantile'] >= 10)).astype(int)
        else:
            filtered_data = data.copy()  # No filtering if the group_var is not recognized

        # Define control variables
        controls = []
        if std_ctrl:
            controls.append(standard_controls)
        if vol_ctrl:
            controls.append(surprise_vol_controls)
        control_formula = '+'.join(controls)
        
        # Construct the regression formula
        formula = f"{dependent_var} ~ Friday_Label + {group_var} + Friday_Label:{group_var}"
        if control_formula:
            formula += ' + ' + control_formula

        # Run the regression
        model = smf.ols(formula, data=filtered_data).fit(cov_type='HC3')
        results.append((model, std_ctrl, vol_ctrl))  # Include control flags for later use

    return results

# -----------------------------
# Run Regressions
# -----------------------------

# Run Immediate Return regressions
immediate_results = run_regressions('immediate_return', data_cleaned, specifications)

# Run Drift Return regressions
drift_results = run_regressions('drift_return_75', data_cleaned, specifications)

# -----------------------------
# Output Results to LaTeX
# -----------------------------
def create_summary_table(results, file_name):
    models = [res[0] for res in results]
    std_ctrl_flags = [res[1] for res in results]
    vol_ctrl_flags = [res[2] for res in results]

    # Add "X" for included controls
    info_dict = {
        'N': lambda x: f"{int(x.nobs)}",  # Correctly extract the number of observations
        'R2': lambda x: f"{x.rsquared:.4f}",  # Correctly extract R-squared
        'Standard Controls': lambda x: "X" if std_ctrl_flags[models.index(x)] else "",  # Correctly associate flags
        'Surprise Volatility': lambda x: "X" if vol_ctrl_flags[models.index(x)] else ""  # Correctly associate flags
    }

    # Generate the summary table
    table = summary_col(models, stars=True, model_names=[f'({i+1})' for i in range(len(models))],
                        info_dict=info_dict)

    # Extract the main table as a DataFrame
    table_df = table.tables[0]

    # Debug: Print the table to ensure it is correctly generated
    print("Generated Table:")
    print(table_df)

    # Save the filtered table to LaTeX
    try:
        with open(file_name, 'w') as f:
            f.write(table_df.to_latex())
        print(f"Table successfully saved to {file_name}")
    except Exception as e:
        print(f"Error saving table to {file_name}: {e}")

# -----------------------------
# Output Results to LaTeX
# -----------------------------

# Generate and save Immediate Return Table
create_summary_table(immediate_results, 'immediate_return_2.tex')

# Generate and save Drift Return Table
create_summary_table(drift_results, 'delay_return_2.tex')