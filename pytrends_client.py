from pytrends.request import TrendReq
import matplotlib.pyplot as plt
import logging
import os

# Initialize logging for detailed output
logging.basicConfig(level=logging.INFO)


def get_trend_data(search_term):
    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload(
        [search_term], cat=0, timeframe="today 12-m", geo="", gprop=""
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
    if combined_trend_data is not None:
        plt.figure(figsize=(14, 8))
        for column in combined_trend_data.columns:
            if column != "isPartial":  # Exclude 'isPartial' from the plot
                plt.plot(
                    combined_trend_data.index,
                    combined_trend_data[column],
                    marker="o",
                    label=column,
                )

        plt.title("Trend Over Time for All Search Terms")
        plt.xlabel("Date")
        plt.ylabel("Interest")
        plt.grid(True)

        plt.legend(
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            ncol=1,
            fontsize="small",
            frameon=False,
        )
        plt.tight_layout(rect=[0, 0, 0.85, 1])

        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        plot_file = os.path.join(output_dir, "combined_trend_chart.png")
        plt.savefig(plot_file)
        plt.close()
        logging.info("Combined trend chart saved.")
    else:
        logging.info("Skipping collective chart generation due to lack of data.")
