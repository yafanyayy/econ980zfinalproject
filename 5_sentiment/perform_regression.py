import pandas as pd
from sklearn.linear_model import LinearRegression
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Ensure the VADER lexicon is downloaded
nltk.download('vader_lexicon', quiet=True)

# Load the filtered data
file_path = "filtered_nonna_data.xlsx"
filtered_df = pd.read_excel(file_path)

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Compute sentiment scores
filtered_df['sentiment_overall'] = filtered_df['transcripts'].apply(
    lambda text: sia.polarity_scores(text)['compound'] if isinstance(text, str) else None
)

# Prepare data for regression
reg_df = filtered_df.dropna(subset=['sentiment_overall', 'surprise', 'Friday_Label', 'immediate_return', 'drift_return'])
reg_df = reg_df[['Friday_Label', 'surprise', 'sentiment_overall', 'immediate_return', 'drift_return']].copy()

# Regression 1: Sentiment vs Friday_Label and surprise
X1 = reg_df[['Friday_Label', 'surprise']]
y1 = reg_df['sentiment_overall'].astype(float)
model1 = LinearRegression().fit(X1, y1)
print("Regression 1: sentiment_overall = b0 + b1*Friday_Label + b2*surprise")
print("Coefficients (b1, b2):", model1.coef_)
print("Intercept (b0):", model1.intercept_)
print("R^2:", model1.score(X1, y1))
print()

# Regression 2: Immediate return vs surprise and sentiment
X2 = reg_df[['surprise', 'sentiment_overall']].astype(float)
y2 = reg_df['immediate_return'].astype(float)
model2 = LinearRegression().fit(X2, y2)
print("Regression 2: immediate_return = a0 + a1*surprise + a2*sentiment_overall")
print("Coefficients (a1, a2):", model2.coef_)
print("Intercept (a0):", model2.intercept_)
print("R^2:", model2.score(X2, y2))
print()

# Regression 3: Final drift return vs surprise and sentiment
X3 = reg_df[['surprise', 'sentiment_overall']].astype(float)
y3 = reg_df['drift_return'].astype(float)
model3 = LinearRegression().fit(X3, y3)
print("Regression 3: final_drift_return = c0 + c1*surprise + c2*sentiment_overall")
print("Coefficients (c1, c2):", model3.coef_)
print("Intercept (c0):", model3.intercept_)
print("R^2:", model3.score(X3, y3))