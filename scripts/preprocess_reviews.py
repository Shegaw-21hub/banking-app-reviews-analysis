import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')
nltk.download('stopwords')
import os

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

def clean_text(text):
    """Clean review text"""
    if not isinstance(text, str):
        return ""
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Tokenize and remove stopwords
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    return ' '.join(tokens)

def preprocess_data(input_file, output_file):
    """Preprocess the scraped data"""
    # Create data directory if not exists
    os.makedirs('data', exist_ok=True)
    
    # Load data
    df = pd.read_csv(input_file)
    
    # Clean review text
    df['cleaned_review'] = df['review'].apply(clean_text)
    
    # Ensure proper date format
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    # Save cleaned data
    df.to_csv(output_file, index=False)
    print(f"Preprocessed data saved to {output_file}")

if __name__ == "__main__":
    preprocess_data(
        input_file='data/bank_reviews_raw.csv',
        output_file='data/bank_reviews_clean.csv'
    )