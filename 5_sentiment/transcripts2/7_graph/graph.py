import pandas as pd
import matplotlib.pyplot as plt

# Read data from Excel
data = pd.read_excel('../6_return/75.xlsx')

# Group data by friday_label and surprise_quantile, then calculate the mean for immediate_return and drift_return_75
grouped_data = data.groupby(['friday_label', 'surprise_quantile']).agg({
    'immediate_return': 'mean',
    'drift_return_75': 'mean'
}).reset_index()

# Separate data for Friday and non-Friday
friday_data = grouped_data[grouped_data['friday_label'] == 1]
non_friday_data = grouped_data[grouped_data['friday_label'] == 0]

# Plot Immediate Return
plt.figure(figsize=(8, 5))
plt.plot(friday_data['surprise_quantile'], friday_data['immediate_return'], label='Friday', color='black', linestyle='-')
plt.plot(non_friday_data['surprise_quantile'], non_friday_data['immediate_return'], label='Other Days', color='gray', linestyle='-')
plt.xlabel('Earnings Surprise Quantile')
plt.ylabel('Mean Immediate Return')
plt.title('(a) Immediate Return')
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(friday_data['surprise_quantile'])
plt.legend()
plt.tight_layout()
plt.savefig('immediate_return_graph.png')  # Save the graph as a PNG file
plt.show()

# Plot Drift Return
plt.figure(figsize=(8, 5))
plt.plot(friday_data['surprise_quantile'], friday_data['drift_return_75'], label='Friday', color='black', linestyle='-')
plt.plot(non_friday_data['surprise_quantile'], non_friday_data['drift_return_75'], label='Other Days', color='gray', linestyle='-')
plt.xlabel('Earnings Surprise Quantile')
plt.ylabel('Mean Drift Return')
plt.title('(b) Drift Return')
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(friday_data['surprise_quantile'])
plt.legend()
plt.tight_layout()
plt.savefig('drift_return_graph.png')  # Save the graph as a PNG file
plt.show()