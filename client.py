"""Fetch country records from the API, export CSV, and create a scatter plot."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Allows saving a chart in headless environments.
import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = "http://127.0.0.1:8000/countries"
TIMEOUT_SECONDS = 20
OUTPUT_DIR = Path(__file__).resolve().parent
CSV_PATH = OUTPUT_DIR / "exported_countries.csv"
PLOT_PATH = OUTPUT_DIR / "population_vs_area.png"


def fetch_countries() -> list[dict]:
    try:
        response = requests.get(API_URL, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SystemExit(
            "Could not reach the Country Data API. Start it first with "
            "'uvicorn main:app --reload'."
        ) from exc

    data = response.json()
    if not isinstance(data, list):
        raise SystemExit("The API returned an unexpected response format.")
    return data


def main() -> None:
    countries = fetch_countries()
    if not countries:
        raise SystemExit(
            "The API returned no countries. Run 'python scraper.py' before this client."
        )

    dataframe = pd.DataFrame(
        countries,
        columns=["name", "capital", "population", "area"],
    )
    dataframe["population"] = pd.to_numeric(dataframe["population"], errors="raise").astype("int64")
    dataframe["area"] = pd.to_numeric(dataframe["area"], errors="raise").astype(float)

    print("\nCountry DataFrame:")
    print(dataframe.to_string(index=False))

    dataframe.to_csv(CSV_PATH, index=False, encoding="utf-8")
    print(f"\nCSV exported to: {CSV_PATH}")

    figure, axis = plt.subplots(figsize=(10, 6))
    axis.scatter(dataframe["population"], dataframe["area"], alpha=0.75)
    axis.set_title("Population vs Area of Countries")
    axis.set_xlabel("Population")
    axis.set_ylabel("Area (sq. km)")
    axis.grid(True, linestyle="--", alpha=0.5)
    figure.tight_layout()
    figure.savefig(PLOT_PATH, dpi=150, bbox_inches="tight")
    plt.close(figure)
    print(f"Scatter plot saved to: {PLOT_PATH}")


if __name__ == "__main__":
    main()
