# pytrends_client.py

from pytrends.request import TrendReq
import pandas as pd
import matplotlib.pyplot as plt
import logging
import os

# Initialize logging for detailed output
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_trend_data(search_term):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([search_term], cat=0, timeframe='today 12-m', geo='', gprop='')

    # Fetch trend data
    trend_data = pytrends.interest_over_time()
    if trend_data.empty:
        logging.warning(f"No trend data found for '{search_term}'.")
        return None, None
    
    # Fetch related queries
    try:
        related_queries = pytrends.related_queries()
        logging.debug(f"Full related queries response for '{search_term}': {related_queries}")
    except Exception as e:
        logging.error(f"Error fetching related queries for '{search_term}': {str(e)}")
        return trend_data, pd.DataFrame()

    # Safely retrieve top related queries
    if related_queries and search_term in related_queries:
        top_related_queries = related_queries.get(search_term, {}).get('top', pd.DataFrame())
        if top_related_queries.empty:
            logging.warning(f"No 'top' related queries data found for '{search_term}'.")
    else:
        logging.warning(f"No related queries data found for '{search_term}'.")
        top_related_queries = pd.DataFrame()

    return trend_data, top_related_queries

def save_to_csv(trend_data, related_queries, search_term, combined_trend_data, combined_related_queries):
    # Create the directory for this search term
    output_dir = os.path.join('output', search_term)
    os.makedirs(output_dir, exist_ok=True)
    
    if trend_data is not None:
        trend_data_file = os.path.join(output_dir, f'{search_term}_trend_data.csv')
        trend_data.to_csv(trend_data_file)
        logging.info(f"Trend data saved to {trend_data_file}")

        # Append to combined trend data
        combined_trend_data = pd.concat([combined_trend_data, trend_data], axis=1)
    
    if related_queries is not None and not related_queries.empty:
        related_queries_file = os.path.join(output_dir, f'{search_term}_related_queries.csv')
        related_queries.to_csv(related_queries_file)
        logging.info(f"Related queries saved to {related_queries_file}")

        # Append to combined related queries
        combined_related_queries = pd.concat([combined_related_queries, related_queries], axis=0)
    
    return combined_trend_data, combined_related_queries

def save_combined_csv(combined_trend_data, combined_related_queries):
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    if combined_trend_data is not None:
        combined_trend_data_file = os.path.join(output_dir, 'combined_trend_data.csv')
        combined_trend_data.to_csv(combined_trend_data_file)
        logging.info(f"Combined trend data saved to {combined_trend_data_file}")
    
    if combined_related_queries is not None and not combined_related_queries.empty:
        combined_related_queries_file = os.path.join(output_dir, 'combined_related_queries.csv')
        combined_related_queries.to_csv(combined_related_queries_file)
        logging.info(f"Combined related queries saved to {combined_related_queries_file}")

def plot_combined_trend_data(combined_trend_data):
    if combined_trend_data is not None:
        plt.figure(figsize=(14, 8))
        for column in combined_trend_data.columns:
            if column != "isPartial":  # Exclude 'isPartial' from the plot
                plt.plot(combined_trend_data.index, combined_trend_data[column], marker='o', label=column)
        
        plt.title(f"Trend Over Time for All Search Terms")
        plt.xlabel('Date')
        plt.ylabel('Interest')
        plt.grid(True)
        
        # Move the legend outside the plot
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1, fontsize='small', frameon=False)
        
        # Adjust layout to accommodate the legend
        plt.tight_layout(rect=[0, 0, 0.85, 1])
        
        # Save the collective plot
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        plot_file = os.path.join(output_dir, 'combined_trend_chart.png')
        plt.savefig(plot_file)
        plt.close()  # Close the plot to avoid displaying it during runtime
        logging.info(f"Combined trend chart saved.")
    else:
        logging.info(f"Skipping collective chart generation due to lack of data.")

