# Generates fg-data-profiling reports for the datasets in the data/ directory.
# The reports are generated in the reports/ directory.

from pathlib import Path

import pandas as pd
from data_profiling import ProfileReport

DATA_DIR = Path("../data/cleaned")
REPORT_DIR = Path("reports")


def main() -> None:
    # Create the reports/ directory if it doesn't exist
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Get all CSV files in the data/ directory
    csv_files = sorted(DATA_DIR.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in '{DATA_DIR}'.")
        return

    for csv_file in csv_files:
        print(f"Generating report for {csv_file.name}...")

        try:
            df = pd.read_csv(csv_file)

            profile = ProfileReport(
                df,
                title=f"Data Profile: {csv_file.name}"
            )

            # Save the report as an HTML file in the reports/ directory
            output_file = REPORT_DIR / f"{csv_file.stem}.html"
            profile.to_file(output_file)

            print(f"Report saved to {output_file}")

        except Exception as exc:
            print(f"Failed to process {csv_file.name}: {exc}")


if __name__ == "__main__":
    main()