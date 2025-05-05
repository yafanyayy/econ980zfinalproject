import os
import pandas as pd
from datetime import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import ssl

# Test on a single file
file_path = "2010/Abercrombie  Fitch Co.csv"  # Replace with the path to your test file

# Load the CSV file into a DataFrame
df = pd.read_csv(file_path)

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()


# Check if the 'mostimportantdateutc' column exists
if 'mostimportantdateutc' not in df.columns:
    print(f"'mostimportantdateutc' column not found in {file_path}")
else:
    # Extract unique dates from the 'mostimportantdateutc' column
    df['mostimportantdateutc'] = pd.to_datetime(df['mostimportantdateutc'], errors='coerce')
    unique_dates = df['mostimportantdateutc'].dropna().dt.date.unique()

    # Process the first unique date for testing
    if len(unique_dates) > 0:
        date = unique_dates[0]
        subset = df[df['mostimportantdateutc'].dt.date == date]

        # Initialize word count and sentiment score for each speaker type
        speaker_stats = {
            'Operator': {'word_count': 0, 'sentiment_sum': 0, 'row_count': 0},
            'Executives': {'word_count': 0, 'sentiment_sum': 0, 'row_count': 0},
            'Analysts': {'word_count': 0, 'sentiment_sum': 0, 'row_count': 0}
        }

        # Process each row in the subset
        for _, row in subset.iterrows():
            speaker_type = row.get('speakertypename', None)
            word_count = row.get('word_count', 0)
            component_text = row.get('componenttext', '')

            # Ensure component_text is a string
            if not isinstance(component_text, str):
                component_text = ""

            if speaker_type in speaker_stats:
                # Update word count
                speaker_stats[speaker_type]['word_count'] += word_count

                # Calculate sentiment score for the text
                sentiment_score = sia.polarity_scores(component_text)['compound']
                speaker_stats[speaker_type]['sentiment_sum'] += sentiment_score
                speaker_stats[speaker_type]['row_count'] += 1

        # Calculate average sentiment scores
        for speaker_type in speaker_stats:
            if speaker_stats[speaker_type]['row_count'] > 0:
                speaker_stats[speaker_type]['avg_sentiment'] = (
                    speaker_stats[speaker_type]['sentiment_sum'] / speaker_stats[speaker_type]['row_count']
                )
            else:
                speaker_stats[speaker_type]['avg_sentiment'] = None

        # Print the results for testing
        print(f"Date: {date}")
        print("Speaker Stats:", speaker_stats)