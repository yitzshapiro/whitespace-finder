import logging
from ollama_client import generate_search_terms
from pytrends_client import (
    get_trend_data,
    update_combined_trend_data,
    plot_combined_trend_data,
)
from utils import handle_errors, validate_search_terms
from amazon_client import search_on_amazon
import pandas as pd
import asyncio
import matplotlib.pyplot as plt
import random

logging.basicConfig(level=logging.INFO)


def filter_top_search_terms(combined_trend_data):
    if combined_trend_data.empty or len(combined_trend_data) < 2:
        logging.warning("Not enough data to filter top search terms.")
        return []

    last_two_months = combined_trend_data.iloc[-2:]
    last_two_months.loc[:, "delta"] = last_two_months.diff().iloc[-1]

    filtered_terms = (
        last_two_months[last_two_months["delta"] > 0]
        .sum(axis=0)
        .nlargest(5)
        .index.str.replace("_trend", "")
        .tolist()
    )

    return filtered_terms


def save_final_report(filtered_terms, search_results):
    report_df = pd.DataFrame(search_results)
    report_df.to_csv("final_report.csv", index=False)
    logging.info("Final report saved as 'final_report.csv'")

    plt.figure(figsize=(14, 8))
    plt.bar(report_df["term"], report_df["listLength"])
    plt.title("Top Search Terms by List Length")
    plt.xlabel("Search Terms")
    plt.ylabel("List Length")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("final_report_chart.png")
    plt.close()
    logging.info("Final report chart saved as 'final_report_chart.png'")


@handle_errors
async def main():
    prompt = """
    Generate 50 search terms (no more than 3 words each) for random niche amazon search terms in 2024. 
    Be specific, weird, and ensure there are spaces between the words and no duplicates.
    Respond with a JSON object in the following format:
    {
        "search_terms": [
            "term1",
            "term2",
            ...
        ]
    }
    EACH SEARCH TERM MUST BE NO MORE THAN 3 WORDS.
    """
    search_terms = generate_search_terms(prompt)
    logging.info(f"Generated {len(search_terms)} search terms.")
    logging.info("Search terms:")
    for term in search_terms:  # Comment out for production
        logging.info(f"  - {term}")  # Comment out for production
    validate_search_terms(search_terms)

    combined_trend_data = pd.DataFrame()

    for term in search_terms:
        try:
            logging.info(f"Processing term: '{term}'")
            trend_data = get_trend_data(term)
            if trend_data is None:
                logging.warning(f"Skipping '{term}' due to lack of trend data.")
                continue
            combined_trend_data = update_combined_trend_data(
                trend_data, term, combined_trend_data
            )
        except Exception as e:
            logging.error(f"Failed to process term '{term}': {str(e)}")

    filtered_terms = filter_top_search_terms(combined_trend_data)
    logging.info(f"Top 5 search terms: {filtered_terms}")

    search_results = []
    for term in filtered_terms:
        logging.info(
            f"Searching for '{term}' on Amazon using amazon-buddy-yitz-version..."
        )
        result_file, result_count, list_length = search_on_amazon(
            term, number=40, country="US", filetype="csv"
        )

        if result_file and result_count > 0:
            search_results.append(
                {
                    "term": term,
                    "result_file": result_file,
                    "result_count": result_count,
                    "listLength": list_length,
                }
            )
        await asyncio.sleep(random.uniform(5, 10))

    save_final_report(filtered_terms, search_results)
    plot_combined_trend_data(combined_trend_data)

    logging.info("Data collection, CSV creation, and chart generation complete.")


if __name__ == "__main__":
    asyncio.run(main())
