import pandas as pd
import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download()
nltk.download('all')

# # Ensure the VADER lexicon is downloaded
nltk.download('vader_lexicon', quiet=True)

# 1. Load the Excel file into a DataFrame
df = pd.read_excel("../4_earning_regression/labeled_earningsearch_with_returns_and_abnormal.xlsx")

# 2. Filter to first 500 rows with complete data in relevant columns
# Define a mask for non-missing announcement date (either t_ibes or t_newswires)
has_date = df['t_ibes'].notna() | df['t_newswires'].notna()
needed_cols = ['cusip', 'Friday_Label', 'immediate_return', 'drift_return', 'surprise']
has_others = df[needed_cols].notna().all(axis=1)
filtered_df = df[has_date & has_others].iloc[:500].copy()

# Prepare new columns for sentiment and final drift
filtered_df['sentiment_mgmt'] = None
filtered_df['sentiment_qa'] = None
filtered_df['sentiment_overall'] = None
filtered_df['final_drift_return'] = None

# Helper function to compute 9th digit of CUSIP (Modulus 10 Double-Add-Double algorithm)
def compute_cusip_check(cusip8: str) -> str:
    mapping = {**{str(i): i for i in range(10)},
               **{chr(i): i - 55 for i in range(65, 91)},  # A=10, B=11, ..., Z=35 (65->'A')
               '*': 36, '@': 37, '#': 38}
    total = 0
    for idx, char in enumerate(cusip8, start=1):
        if char not in mapping:
            raise ValueError(f"Invalid CUSIP character: {char}")
        val = mapping[char]
        # Double every even-position character
        if idx % 2 == 0:
            val *= 2
        # If double-digit, sum the digits (which is equivalent to subtracting 9 if val>=10)
        val = (val // 10) + (val % 10)
        total += val
    check_digit = (10 - (total % 10)) % 10
    return str(check_digit)

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# 3 & 4. Loop through each entry, fetch transcript and compute sentiment
API_KEY = "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"

for idx, row in filtered_df.iterrows():
    cusip_base = str(row['cusip']).zfill(8)  # ensure it's 8 characters (pad with zeros if needed)
    try:
        cusip_full = cusip_base + compute_cusip_check(cusip_base)
    except ValueError as e:
        # If CUSIP is invalid or missing, skip this entry
        print(f"Skipping row {idx}: {e}")
        continue

    # Fetch symbol using FMP CUSIP search API
    try:
        resp = requests.get(f"https://financialmodelingprep.com/stable/search-cusip?cusip={cusip_full}&apikey={API_KEY}")
        data = resp.json()
    except Exception as e:
        print(f"API request failed for CUSIP {cusip_full}: {e}")
        continue
    if not data:
        print(f"No symbol found for CUSIP {cusip_full}")
        continue
    symbol = data[0].get('symbol')
    if not symbol:
        print(f"No symbol in response for CUSIP {cusip_full}")
        continue

    # Determine announcement date
    ann_date = row['t_newswires'] if pd.notna(row['t_newswires']) else row['t_ibes']
    # Determine year and quarter for earnings call
    ann_month = ann_date.month
    ann_year = ann_date.year
    if ann_month <= 3:
        call_year = ann_year - 1
        call_quarter = 4
    elif ann_month <= 6:
        call_year = ann_year
        call_quarter = 1
    elif ann_month <= 9:
        call_year = ann_year
        call_quarter = 2
    else:
        call_year = ann_year
        call_quarter = 3

    # Fetch earnings call transcript from FMP API
    try:
        url = f"https://financialmodelingprep.com/api/v3/earning_call_transcript/{symbol}?year={call_year}&quarter={call_quarter}&apikey={API_KEY}"
        resp = requests.get(url)
        transcript_data = resp.json()
    except Exception as e:
        print(f"Transcript API request failed for {symbol} {call_year} Q{call_quarter}: {e}")
        continue
    if not transcript_data:
        # If no transcript returned, skip sentiment for this entry
        print(f"No transcript found for {symbol} {call_year} Q{call_quarter}")
        continue

    # Assume the first (or only) item in transcript_data is the relevant transcript
    transcript_entry = transcript_data[0]
    transcript_text = transcript_entry.get('content', '')
    transcript_date_str = transcript_entry.get('date')
    if transcript_date_str:
        try:
            transcript_date = datetime.strptime(transcript_date_str.split(' ')[0], "%Y-%m-%d")
        except Exception:
            transcript_date = None
    else:
        transcript_date = None

    # Optional: verify transcript date is within ±3 days of announcement date
    if transcript_date:
        date_diff = abs((transcript_date.date() - ann_date.date()).days)
        if date_diff > 3:
            print(f"Warning: Transcript date {transcript_date.date()} not within 3 days of announcement {ann_date.date()} for {symbol}.")
    
    # 4. Split transcript into management discussion vs Q&A
    text_lower = transcript_text.lower()
    qna_start_idx = None
    # Find indicator of Q&A start
    key_phrases = ["your first question", "the floor is now open for questions", "q&a session", "question-and-answer session"]
    for phrase in key_phrases:
        idx = text_lower.find(phrase)
        if idx != -1:
            qna_start_idx = idx
            break
    if qna_start_idx is not None:
        # Find the start of that sentence (likely at an Operator: or just before the phrase)
        op_idx = text_lower.rfind("operator", 0, qna_start_idx)
        qna_start_idx = op_idx if op_idx != -1 else qna_start_idx
    # If we found a Q&A split point, separate the text
    if qna_start_idx:
        mgmt_text = transcript_text[:qna_start_idx].strip()
        qa_text = transcript_text[qna_start_idx:].strip()
    else:
        # If no clear Q&A marker, treat entire transcript as management portion
        mgmt_text = transcript_text
        qa_text = ""

    # Compute sentiment scores using VADER
    if mgmt_text:
        score_mgmt = sia.polarity_scores(mgmt_text)['compound']
    else:
        score_mgmt = None
    if qa_text:
        score_qa = sia.polarity_scores(qa_text)['compound']
    else:
        score_qa = None
    # Compute overall sentiment as average of available scores
    if score_mgmt is not None and score_qa is not None:
        score_overall = (score_mgmt + score_qa) / 2.0
    elif score_mgmt is not None:
        score_overall = score_mgmt
    else:
        score_overall = score_qa

    # 5. Add sentiment scores to the DataFrame
    filtered_df.at[idx, 'sentiment_mgmt'] = score_mgmt
    filtered_df.at[idx, 'sentiment_qa'] = score_qa
    filtered_df.at[idx, 'sentiment_overall'] = score_overall

    # Parse final drift return (last value in drift_return list)
    drift_list = None
    # The drift_return might be stored as a list or string representation of list
    dr_value = row['drift_return']
    if isinstance(dr_value, str):
        # Remove any surrounding quotes and evaluate the list safely
        try:
            import ast
            drift_list = ast.literal_eval(dr_value)
        except Exception:
            # If parsing fails, skip
            pass
    elif isinstance(dr_value, (list, tuple)):
        drift_list = dr_value
    # If we got a list, take the last element as final drift return
    final_drift = None
    if drift_list:
        try:
            final_drift = drift_list[-1]
        except Exception:
            final_drift = None
    filtered_df.at[idx, 'final_drift_return'] = final_drift
# After loop, we have sentiment scores and final drift returns for up to 500 entries.

# 6. Regression analyses

# Prepare data for regression (drop any rows where sentiment or returns are missing)
reg_df = filtered_df.dropna(subset=['sentiment_overall', 'surprise', 'Friday_Label', 'immediate_return', 'final_drift_return'])
reg_df = reg_df[['Friday_Label', 'surprise', 'sentiment_overall', 'immediate_return', 'final_drift_return']].copy()
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
y3 = reg_df['final_drift_return'].astype(float)
model3 = LinearRegression().fit(X3, y3)
print("Regression 3: final_drift_return = c0 + c1*surprise + c2*sentiment_overall")
print("Coefficients (c1, c2):", model3.coef_)
print("Intercept (c0):", model3.intercept_)
print("R^2:", model3.score(X3, y3))
