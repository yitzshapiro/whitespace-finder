# main.py

import logging
from ollama_client import generate_search_terms
from pytrends_client import (
    get_trend_data, 
    save_to_csv, 
    save_combined_csv, 
    plot_combined_trend_data
)
from utils import handle_errors, validate_search_terms
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@handle_errors
def main():
    prompt = """
    Generate 10 search terms (no more than 2 words each) for random niche etsy search terms in 2024. 
    Respond with a JSON object in the following format:
    {
        "search_terms": [
            "term1",
            "term2",
            ...
        ]
    }
    """
    search_terms = generate_search_terms(prompt)
    validate_search_terms(search_terms)
    
    combined_trend_data = pd.DataFrame()
    combined_related_queries = pd.DataFrame()
    
    for term in search_terms:
        try:
            logging.info(f"Processing term: '{term}'")
            trend_data, related_queries = get_trend_data(term)
            if trend_data is None:
                logging.warning(f"Skipping '{term}' due to lack of trend data.")
                continue
            combined_trend_data, combined_related_queries = save_to_csv(
                trend_data, 
                related_queries, 
                term, 
                combined_trend_data, 
                combined_related_queries
            )
        except Exception as e:
            logging.error(f"Failed to process term '{term}': {str(e)}")
    
    # Save combined CSV files
    save_combined_csv(combined_trend_data, combined_related_queries)

    # Generate and save the combined trend plot
    plot_combined_trend_data(combined_trend_data)

    logging.info("Data collection, CSV creation, and chart generation complete.")

if __name__ == "__main__":
    main()
