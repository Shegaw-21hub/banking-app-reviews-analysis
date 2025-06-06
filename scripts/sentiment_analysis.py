import pandas as pd
from transformers import pipeline
from tqdm import tqdm
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data(file_path):
    """Load and validate review data"""
    try:
        df = pd.read_csv(file_path)
        
        # Validate required columns
        required_cols = ['review', 'rating', 'date', 'bank']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Missing required columns. Needed: {required_cols}")
            
        # Ensure review column contains strings
        df['review'] = df['review'].astype(str)
        
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def analyze_sentiment(df, batch_size=32):
    """Perform sentiment analysis with robust error handling"""
    try:
        logger.info("Initializing sentiment analysis pipeline...")
        
        # Initialize pipeline with error handling
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=0 if torch.cuda.is_available() else -1,  # Use GPU if available
            truncation=True,
            padding=True,
            max_length=512
        )
        
        sentiments = []
        scores = []
        
        # Process reviews in batches with progress tracking
        logger.info("Starting sentiment analysis...")
        for i in tqdm(range(0, len(df), batch_size), desc="Analyzing sentiment"):
            batch = df['review'].iloc[i:i+batch_size].tolist()
            
            # Skip empty batches
            if not batch:
                continue
                
            try:
                results = sentiment_pipeline(batch)
                
                for result in results:
                    sentiments.append(result['label'])
                    scores.append(result['score'])
            except Exception as batch_error:
                logger.warning(f"Error processing batch {i//batch_size}: {batch_error}")
                # Fill with neutral sentiment if batch fails
                sentiments.extend(['NEUTRAL'] * len(batch))
                scores.extend([0.5] * len(batch))
                
        # Handle case where analysis failed completely
        if not sentiments:
            raise RuntimeError("Sentiment analysis failed for all batches")
            
        df['sentiment'] = sentiments
        df['sentiment_score'] = scores
        
        # Convert to numeric sentiment (positive=1, negative=0, neutral=0.5)
        sentiment_map = {'POSITIVE': 1, 'NEGATIVE': 0, 'NEUTRAL': 0.5}
        df['sentiment_numeric'] = df['sentiment'].map(sentiment_map)
        
        return df
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise

def aggregate_sentiment(df):
    """Aggregate sentiment results with error handling"""
    try:
        # Overall sentiment by bank
        bank_sentiment = df.groupby('bank')['sentiment_numeric'].mean().reset_index()
        
        # Sentiment by rating for each bank
        rating_sentiment = df.groupby(['bank', 'rating'])['sentiment_numeric'].mean().unstack()
        
        return bank_sentiment, rating_sentiment
    except Exception as e:
        logger.error(f"Aggregation failed: {e}")
        return None, None

def save_results(df, output_file):
    """Save results with validation"""
    try:
        required_cols = ['review', 'rating', 'date', 'bank', 'sentiment', 'sentiment_score']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Missing required columns for output. Needed: {required_cols}")
            
        df.to_csv(output_file, index=False)
        logger.info(f"Results saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save results: {e}")
        raise

def main():
    try:
        # Input/output paths
        input_file = 'data/bank_reviews_clean.csv'
        output_file = 'data/bank_reviews_with_sentiment.csv'
        
        # Load data
        logger.info(f"Loading data from {input_file}")
        df = load_data(input_file)
        
        # Analyze sentiment
        df = analyze_sentiment(df)
        
        # Aggregate results
        bank_sentiment, rating_sentiment = aggregate_sentiment(df)
        
        # Save results
        save_results(df, output_file)
        
        # Print summary
        logger.info("\nSentiment Analysis Summary:")
        print(bank_sentiment)
        logger.info("\nSentiment by Rating:")
        print(rating_sentiment)
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        return 1
        
    return 

if __name__ == "__main__":
    import torch  # Import here to properly handle GPU availability
    exit(main())