import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_PATH = '../data/bank_reviews_clean.csv'
VISUALS_DIR = '../reports/visuals'

os.makedirs(VISUALS_DIR, exist_ok=True)

def load_data():
    logger.info(f"Loading data from {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    logger.info(f"Data shape: {df.shape}")
    return df

def plot_sentiment_distribution(df):
    plt.figure(figsize=(8,6))
    sns.countplot(x='rating', data=df, palette='coolwarm')
    plt.title('Rating Distribution')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.savefig(os.path.join(VISUALS_DIR, 'rating_distribution.png'))
    plt.close()
    logger.info("Saved rating distribution plot.")

def get_common_keywords(text_series, top_n=10):
    # Tokenize and count words excluding stopwords
    stopwords = set(STOPWORDS)
    words = ' '.join(text_series.dropna()).lower().split()
    words = [w.strip('.,!?()[]') for w in words if w not in stopwords and len(w) > 2]
    counter = Counter(words)
    return counter.most_common(top_n)

def plot_keywords(keywords, title, filename):
    words, counts = zip(*keywords)
    plt.figure(figsize=(8,5))
    sns.barplot(x=list(counts), y=list(words), palette='viridis')
    plt.title(title)
    plt.xlabel('Frequency')
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALS_DIR, filename))
    plt.close()
    logger.info(f"Saved keyword plot: {filename}")

def wordcloud_from_text(text, filename):
    wc = WordCloud(width=800, height=400, background_color='white', stopwords=STOPWORDS).generate(text)
    plt.figure(figsize=(10,5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title('Keyword Wordcloud')
    plt.savefig(os.path.join(VISUALS_DIR, filename))
    plt.close()
    logger.info(f"Saved wordcloud: {filename}")

def analyze_bank(df, bank_name):
    logger.info(f"Analyzing bank: {bank_name}")
    bank_df = df[df['bank'].str.lower() == bank_name.lower()]
    if bank_df.empty:
        logger.warning(f"No data found for bank {bank_name}")
        return None
    
    # Separate positive and negative reviews (e.g., rating >=4 positive, <=2 negative)
    pos_reviews = bank_df[bank_df['rating'] >= 4]['cleaned_review']
    neg_reviews = bank_df[bank_df['rating'] <= 2]['cleaned_review']

    pos_keywords = get_common_keywords(pos_reviews, top_n=10)
    neg_keywords = get_common_keywords(neg_reviews, top_n=10)
    
    logger.info(f"Top positive keywords for {bank_name}: {pos_keywords}")
    logger.info(f"Top negative keywords for {bank_name}: {neg_keywords}")
    
    # Plot keywords
    plot_keywords(pos_keywords, f"{bank_name} - Top Positive Keywords", f"{bank_name}_positive_keywords.png")
    plot_keywords(neg_keywords, f"{bank_name} - Top Negative Keywords", f"{bank_name}_negative_keywords.png")
    
    # Wordclouds
    wordcloud_from_text(' '.join(pos_reviews.dropna()), f"{bank_name}_positive_wordcloud.png")
    wordcloud_from_text(' '.join(neg_reviews.dropna()), f"{bank_name}_negative_wordcloud.png")

    # Return insights summary
    return {
        'bank': bank_name,
        'drivers': [kw for kw, count in pos_keywords],
        'pain_points': [kw for kw, count in neg_keywords]
    }

def main():
    df = load_data()
    plot_sentiment_distribution(df)

    # Example banks to compare
    banks_to_analyze = ['CBE', 'BOA']
    insights = []

    for bank in banks_to_analyze:
        result = analyze_bank(df, bank)
        if result:
            insights.append(result)

    # Print insights summary
    for insight in insights:
        logger.info(f"Insights for {insight['bank']}:")
        logger.info(f"  Drivers (positive): {', '.join(insight['drivers'][:3])}")
        logger.info(f"  Pain points (negative): {', '.join(insight['pain_points'][:3])}")

    # Ethics note (just print here; include in your report)
    logger.info("Note: Reviews may have biases such as negativity bias or fake reviews. Interpret results carefully.")

if __name__ == '__main__':
    main()
