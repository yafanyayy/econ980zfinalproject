import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Read data from Excel
data = pd.read_excel('75.xlsx')

# Prepare Data
data['top_group'] = (data['surprise_quantile'] == 11).astype(int)
data['top_two_groups'] = (data['surprise_quantile'] >= 10).astype(int)
data['Friday'] = data['Friday_Label']

# Controls
# Adjust log market cap by subtracting quarterly mean
quarterly_avg = data.groupby(['year', 'quarter'])['log_market_cap'].transform('mean')
data['log_market_cap_adj'] = data['log_market_cap'] - quarterly_avg

# Add month and year as controls
data['month'] = pd.to_datetime(data['t_newswire']).dt.month.astype('category')
data['year'] = pd.to_datetime(data['t_newswire']).dt.year.astype('category')

# Define control variables
standard_controls = 'log_market_cap_adj + C(month) + C(year)'
surprise_vol_controls = 'surprise_volatility'

# Regression specifications
specifications = [
    ('top_group', False, False, '11 Quantiles'),
    ('top_group', True, False, '11 Quantiles'),
    ('top_group', True, True, '11 Quantiles'),
    ('top_group', True, True, '10 Deciles'),
    ('top_two_groups', False, False, '11 Quantiles'),
    ('top_two_groups', True, False, '11 Quantiles'),
    ('top_two_groups', True, True, '10 Deciles')
]

# Function to run regressions and store results
def run_regressions(dependent_var, data, specs):
    results = []
    for group_var, std_ctrl, vol_ctrl, sorting in specs:
        controls = []
        if std_ctrl:
            controls.append(standard_controls)
        if vol_ctrl:
            controls.append(surprise_vol_controls)
        control_formula = '+'.join(controls)
        
        formula = f"{dependent_var} ~ Friday + {group_var} + Friday:{group_var}"
        if control_formula:
            formula += ' + ' + control_formula

        model = smf.ols(formula, data=data).fit(cov_type='HC3')
        results.append(model)

    return results

# Run Immediate Return regressions
immediate_results = run_regressions('immediate_return', data, specifications)

# Run Drift Return regressions
drift_results = run_regressions('drift_return', data, specifications)

# Output results to LaTeX
from statsmodels.iolib.summary2 import summary_col

immediate_table = summary_col(immediate_results, stars=True, model_names=[f'({i+1})' for i in range(len(immediate_results))],
                              info_dict={'N':lambda x: f"{int(x.nobs)}",
                                         'R2':lambda x: f"{x.rsquared:.4f}"})

with open('immediat_return_2.tex', 'w') as f:
    f.write(immediate_table.as_latex())

drift_table = summary_col(drift_results, stars=True, model_names=[f'({i+1})' for i in range(len(drift_results))],
                          info_dict={'N':lambda x: f"{int(x.nobs)}",
                                     'R2':lambda x: f"{x.rsquared:.4f}"})

with open('delay_return_2.tex', 'w') as f:
    f.write(drift_table.as_latex())
