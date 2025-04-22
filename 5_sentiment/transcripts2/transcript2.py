import os
import pandas as pd
from datetime import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import ssl

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context

# nltk.download()
# Ensure the VADER lexicon is downloaded
# nltk.download('vader_lexicon', quiet=True)


# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Directory containing the year folders
base_dir = "/Users/yafan/Desktop/Econ 980Z/final_project/5_sentiment/transcripts2"

# Initialize counters
total_earnings_calls = 0
friday_earnings_calls = 0
non_friday_earnings_calls = 0

# List to store summary data
summary_data = []

# Iterate through each year folder (2011 to 2022)
for year in range(2011, 2023):
    year_folder = os.path.join(base_dir, str(year))
    if not os.path.exists(year_folder):
        continue  # Skip if the folder doesn't exist

    # Iterate through each file in the year folder
    for file_name in os.listdir(year_folder):
        if file_name.endswith(".csv"):  # Process only CSV files
            file_path = os.path.join(year_folder, file_name)
            
            # Load the CSV file into a DataFrame
            try:
                df = pd.read_csv(file_path)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

            # Check if the 'mostimportantdateutc' column exists
            if 'mostimportantdateutc' not in df.columns:
                print(f"'mostimportantdateutc' column not found in {file_path}")
                continue

            # Extract unique dates from the 'mostimportantdateutc' column
            df['mostimportantdateutc'] = pd.to_datetime(df['mostimportantdateutc'], errors='coerce')
            unique_dates = df['mostimportantdateutc'].dropna().dt.date.unique()

            # Tally the dates and collect summary data
            for date in unique_dates:
                total_earnings_calls += 1
                is_friday = datetime.strptime(str(date), "%Y-%m-%d").weekday() == 4  # Friday is weekday 4
                if is_friday:
                    friday_earnings_calls += 1
                else:
                    non_friday_earnings_calls += 1

                # Collect summary data for each unique date
                subset = df[df['mostimportantdateutc'].dt.date == date]
                if not subset.empty:
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

                    # Append the summary data
                    summary_data.append({
                        'companyid': subset['companyid'].iloc[0],
                        'keydevid': subset['keydevid'].iloc[0],
                        'transcriptid': subset['transcriptid'].iloc[0],
                        'keydeveventtypename': subset['keydeveventtypename'].iloc[0],
                        'companyname': subset['companyname'].iloc[0],
                        'date': date,
                        'friday_label': 1 if is_friday else 0,
                        'operator_word_count': speaker_stats['Operator']['word_count'],
                        'executives_word_count': speaker_stats['Executives']['word_count'],
                        'analysts_word_count': speaker_stats['Analysts']['word_count'],
                        'operator_avg_sentiment': speaker_stats['Operator']['avg_sentiment'],
                        'executives_avg_sentiment': speaker_stats['Executives']['avg_sentiment'],
                        'analysts_avg_sentiment': speaker_stats['Analysts']['avg_sentiment']
                    })

# Print the results
print("Earnings Call Statistics:")
print(f"Total Earnings Calls: {total_earnings_calls}")
print(f"Earnings Calls on Fridays: {friday_earnings_calls}")
print(f"Earnings Calls on Other Days: {non_friday_earnings_calls}")

# Save the summary data to an Excel file
summary_df = pd.DataFrame(summary_data)
output_file = "summaryPtranscripts2_with_friday_label_and_speaker_stats.xlsx"
summary_df.to_excel(output_file, index=False)
print(f"Summary saved to {output_file}.")