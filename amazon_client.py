import subprocess
import logging
import os
import pandas as pd
import re


def search_on_amazon(search_term, number=100, country="US", filetype="csv"):
    logging.info(
        f"Searching for '{search_term}' on Amazon using amazon-buddy-yitz-version..."
    )
    try:
        result = subprocess.run(
            [
                "amazon-buddy-yitz-version",
                "products",
                "-k", search_term,
                "-n", str(number),
                "--country", country,
                "--filetype", filetype,
                "--random-ua",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logging.error(f"Amazon search failed: {result.stderr}")
            return None, 0, None

        output_text = result.stdout.strip()
        logging.info(f"Amazon-buddy output: {output_text}")

        # Adjusted regex pattern and file extension handling
        match = re.search(r"products\(.+\)_\d+", output_text)
        if match:
            filename = match.group(0).strip() + ".csv"  # Append the .csv extension
            logging.info(f"Regex match found: {filename}")
            if os.path.exists(filename):
                df = pd.read_csv(filename)
                num_results = len(df)
                list_length = (
                    df.iloc[-1]["listLength"] if "listLength" in df.columns else None
                )
                logging.info(
                    f"Found {num_results} results for '{search_term}' on Amazon."
                )
                return filename, num_results, list_length
            else:
                logging.warning(
                    f"File '{filename}' does not exist, although it was stated in the output."
                )
                return None, 0, None
        else:
            logging.warning(
                "Regex did not match any part of the output. Double-check the output format."
            )

        logging.warning(f"No filename found in output for term '{search_term}'.")
        return None, 0, None

    except Exception as e:
        logging.error(f"Failed to search '{search_term}' on Amazon: {str(e)}")
        return None, 0, None
