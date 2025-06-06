from google_play_scraper import app, Sort, reviews_all
import pandas as pd
import os
import time
from datetime import datetime

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Updated bank app details with verified package names
banks = {
    "Commercial Bank of Ethiopia": "com.combanketh.mobilebanking",
    "Bank of Abyssinia": "com.boa.boaMobileBanking", 
    "Dashen Bank": "com.dashen.dashensuperapp"
}

def scrape_app_reviews(app_id, bank_name, max_reviews=400):
    """
    Scrape reviews for a given app ID
    """
    try:
        # Get all available reviews (no continuation token in current version)
        all_reviews = reviews_all(
            app_id,
            lang='en',
            country='et',
            sort=Sort.NEWEST,
            count=max_reviews  # Limit directly in the API call
        )
        
        return all_reviews[:max_reviews]
    
    except Exception as e:
        print(f"Error fetching reviews for {bank_name}: {str(e)}")
        return []

def process_reviews(raw_reviews, bank_name):
    """
    Process raw reviews into structured format with error handling
    """
    processed = []
    
    for review in raw_reviews:
        try:
            review_date = review.get('at', datetime.now())
            if isinstance(review_date, str):
                review_date = datetime.strptime(review_date, '%Y-%m-%d %H:%M:%S')
                
            processed.append({
                'review': review.get('content', ''),
                'rating': review.get('score', 0),
                'date': review_date.strftime('%Y-%m-%d'),
                'bank': bank_name,
                'source': 'Google Play'
            })
        except Exception as e:
            print(f"Error processing review: {str(e)}")
            continue
            
    return processed

def main():
    all_reviews = []
    
    for bank_name, app_id in banks.items():
        print(f"\nScraping reviews for {bank_name}...")
        
        # Scrape reviews
        bank_reviews = scrape_app_reviews(app_id, bank_name)
        
        if not bank_reviews:
            print(f"No reviews found for {bank_name}")
            continue
            
        # Process reviews
        processed = process_reviews(bank_reviews, bank_name)
        all_reviews.extend(processed)
        print(f"Successfully collected {len(processed)} reviews for {bank_name}")
        
        # Rate limiting
        time.sleep(5)
    
    if not all_reviews:
        print("\nFailed to collect any reviews. Exiting.")
        return
        
    # Create DataFrame
    df = pd.DataFrame(all_reviews)
    
    # Data cleaning
    df = df.drop_duplicates(subset=['review', 'bank'])
    df = df[df['review'].notna() & (df['review'].str.strip() != '')]
    
    print(f"\nTotal reviews collected: {len(df)}")
    
    # Save to CSV
    csv_path = "data/bank_reviews_raw.csv"
    df.to_csv(csv_path, index=False)
    print(f"Data saved to {csv_path}")

if __name__ == "__main__":
    main()