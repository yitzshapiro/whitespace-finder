import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="pytrends.request")
from pytrends.request import TrendReq
import matplotlib.pyplot as plt
import logging
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Initialize logging for detailed output
logging.basicConfig(level=logging.INFO)


def get_trend_data(search_term):
    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload(
        [search_term], cat=0, timeframe="today 3-m", geo="", gprop=""
    )

    trend_data = pytrends.interest_over_time()
    if trend_data.empty:
        logging.warning(f"No trend data found for '{search_term}'.")
        return None

    return trend_data

def update_combined_trend_data(trend_data, search_term, combined_trend_data):
    if trend_data is not None:
        trend_data = trend_data.rename(columns={search_term: f"{search_term}_trend"})
        combined_trend_data = combined_trend_data.join(
            trend_data[f"{search_term}_trend"], how="outer"
        )

    return combined_trend_data


def plot_combined_trend_data(combined_trend_data):
    if combined_trend_data is not None and not combined_trend_data.empty:
        # Filter out the 'isPartial' column
        trend_columns = [col for col in combined_trend_data.columns if col != 'isPartial']
        
        # Create a single plot with all trends
        fig = go.Figure()

        for column in trend_columns:
            fig.add_trace(
                go.Scatter(x=combined_trend_data.index, y=combined_trend_data[column],
                           mode='lines+markers', name=column)
            )

        # Update layout
        fig.update_layout(
            height=600, 
            width=1000,
            title_text="Trend Over Time for All Search Terms",
            xaxis_title="Date",
            yaxis_title="Interest",
            legend_title="Search Terms",
            hovermode="x unified"
        )
        
        # Save the plot as an interactive HTML file
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        plot_file = os.path.join(output_dir, "combined_trend_chart.html")
        fig.write_html(plot_file)
        logging.info("Interactive combined trend chart saved as HTML.")
    else:
        logging.info("Skipping chart generation due to lack of data.")
