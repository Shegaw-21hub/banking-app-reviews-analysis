import pandas as pd
import spacy
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load English language model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.error("Spacy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
    raise

# Extract keywords from text
def extract_keywords(text, pos_tags=['NOUN', 'ADJ', 'VERB']):
    if not isinstance(text, str) or not text.strip():
        return []
    try:
        doc = nlp(text)
        return [
            token.lemma_.lower() for token in doc
            if token.pos_ in pos_tags and not token.is_stop and token.is_alpha and len(token) > 2
        ]
    except Exception as e:
        logger.warning(f"Error processing text: {str(e)}")
        return []

# Perform thematic analysis
def analyze_themes(df):
    themes = {
        'bank': [], 'review_id': [], 'theme': [], 'keywords': [],
        'sentiment': [], 'review_text': [], 'sentiment_label': [], 'sentiment_score': []
    }

    theme_mapping = {
        'Account Access': ['login', 'password', 'account', 'access', 'authenticate', 'pin', 'security'],
        'Transaction Issues': ['transfer', 'transaction', 'send', 'money', 'payment', 'failed', 'stuck'],
        'App Performance': ['slow', 'crash', 'lag', 'freeze', 'speed', 'loading', 'hang'],
        'User Interface': ['interface', 'ui', 'design', 'layout', 'button', 'menu', 'navigation'],
        'Customer Support': ['support', 'help', 'response', 'service', 'contact', 'complaint', 'assistance'],
        'Features': ['feature', 'missing', 'request', 'functionality', 'update', 'version', 'option']
    }

    df = df.copy()
    df['cleaned_review'] = df['cleaned_review'].fillna('').astype(str)

    for idx, row in df.iterrows():
        try:
            keywords = extract_keywords(row['cleaned_review'])
            matched_themes = {
                theme for theme, keywords_list in theme_mapping.items()
                if any(word in keywords_list for word in keywords)
            }
            if not matched_themes:
                matched_themes.add('Other')

            for theme in matched_themes:
                themes['bank'].append(row['bank'])
                themes['review_id'].append(idx)
                themes['theme'].append(theme)
                themes['keywords'].append(', '.join(keywords))
                themes['sentiment'].append(row.get('sentiment', 'UNKNOWN'))
                themes['review_text'].append(row.get('review', ''))
                themes['sentiment_label'].append(row.get('sentiment_label', ''))
                themes['sentiment_score'].append(row.get('sentiment_score', ''))

        except Exception as e:
            logger.error(f"Error processing review ID {idx}: {str(e)}")
            continue

    return pd.DataFrame(themes)

# Generate word clouds per bank
def generate_word_clouds(df, text_column='cleaned_review'):
    for bank in df['bank'].unique():
        try:
            text = ' '.join(df[df['bank'] == bank][text_column].astype(str))
            if not text.strip():
                continue
            wordcloud = WordCloud(
                width=800, height=400, background_color='white',
                stopwords=set(nlp.Defaults.stop_words), collocations=False
            ).generate(text)

            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.title(f'Word Cloud for {bank}', pad=20)
            plt.axis('off')
            plt.savefig(f'visualizations/wordcloud_{bank.lower().replace(" ", "_")}.png', dpi=300, bbox_inches='tight')
            plt.close()
        except Exception as e:
            logger.error(f"Word cloud failed for {bank}: {str(e)}")

# Plot bar charts per bank
def generate_bar_charts(themes_df):
    for bank in themes_df['bank'].unique():
        try:
            bank_data = themes_df[themes_df['bank'] == bank]
            plt.figure(figsize=(10, 5))
            sns.countplot(data=bank_data, y='theme', order=bank_data['theme'].value_counts().index)
            plt.title(f'Theme Distribution for {bank}')
            plt.tight_layout()
            plt.savefig(f'visualizations/themes_bar_{bank.lower().replace(" ", "_")}.png')
            plt.close()
        except Exception as e:
            logger.error(f"Bar plot failed for {bank}: {str(e)}")

# Main execution
def main():
    try:
        os.makedirs('data', exist_ok=True)
        os.makedirs('visualizations', exist_ok=True)

        logger.info("📥 Loading data...")
        df = pd.read_csv('data/bank_reviews_with_sentiment.csv')

        if 'cleaned_review' not in df.columns:
            df['cleaned_review'] = df['review'].fillna('').astype(str)

        logger.info("🔍 Performing thematic analysis...")
        themes_df = analyze_themes(df)
        themes_df.to_csv('data/bank_reviews_themes.csv', index=False)
        logger.info("✅ Saved thematic analysis to data/bank_reviews_themes.csv")

        logger.info("🌥️ Generating word clouds...")
        generate_word_clouds(df)

        logger.info("📊 Generating bar charts...")
        generate_bar_charts(themes_df)

        logger.info("📈 Saving per-bank theme distribution...")
        per_bank_theme = themes_df.groupby(['bank', 'theme']).size().unstack(fill_value=0)
        print("\n🎯 Themes Distribution Per Bank:\n", per_bank_theme)
        per_bank_theme.to_csv('data/themes_distribution_per_bank.csv')

    except Exception as e:
        logger.error(f"🚨 Script failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
