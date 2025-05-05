# ECON 980z Final Project: Investor Inattention and Friday Earnings Announcements

This repository contains scripts and data necessary to reproduce key results from DellaVigna and Pollet (2009) and extend their analysis by incorporating earnings call sentiment data.

---

## Structure

### Reproduction (Folders `0-4`)

These folders contain scripts to reproduce the main analysis from the DellaVigna and Pollet (2009) study:

- `0_raw_company_list`: Initial company data collection and preparation.
- `1_index_day`: Identification and labeling of earnings announcement dates.
- `2_surprise`: Calculation of earnings surprises based on analyst forecasts and actual earnings.
- `3_control`: Preparation of control variables used in regressions.
- `4_earning_regression`: Regression analysis scripts for immediate and delayed stock responses to earnings announcements.

---

### Extension: Sentiment Analysis (Folder `5_sentiment`)

This folder contains scripts and data extending the original analysis by incorporating textual sentiment analysis from earnings call transcripts.

Within `transcripts2`:

- `0_data`: Collection and preparation of earnings call transcript data.
- `1_sentiment`: Sentiment analysis of transcript data using NLP tools.
- `3_match`: Matching sentiment data with financial data (earnings announcements, stock returns, etc.).
- `4_surprise`: Computation of earnings surprises for matched data.
- `5_control`: Preparation of control variables for regression.
- `6_return`: Analysis of stock returns (immediate and delayed responses) based on sentiment scores and other predictors.
- `7_graph`: Scripts for creating visualizations to illustrate results clearly.

---

## Data Files

- `EarningsSearchesDec06.dta`: Original earnings announcements data.
- `ccm_lnkused.csv`: Linking table between CRSP and Compustat/I-B-E-S.
- PDF references for methodology and data guidelines:
  - `2009-DELLAVIGNA - Investor Inattention and Friday Earnings.pdf`
  - `A_Note_on_IBES_Unadjusted_Data_pdf.pdf`

---

## How to Run

To reproduce or extend analysis:

1. Follow folders sequentially, running scripts numbered in ascending order.
2. Ensure necessary Python packages and dependencies (e.g., Pandas, NumPy, statsmodels, NLTK, Vader Sentiment) are installed.

Example workflow:
```
python import.py  # Initial data import script
cd 0_raw_company_list
python script.py
# continue sequentially
```

---

## Requirements

- Python (3.7+)
- Libraries: Pandas, NumPy, SciPy, statsmodels, matplotlib, seaborn, NLTK, VADER Sentiment Analysis

---

## Notes

- Carefully validate all earnings announcement dates and financial data.
- The sentiment extension provides insights into the impact of qualitative information on stock market reactions, particularly addressing investor attention dynamics on Fridays.
- Within each folder, it is kind of messy. My apologies for that; I do not have the time to separate the raw, derived and output.

---

## Contact

For any questions or clarifications, please contact the repository owner.
