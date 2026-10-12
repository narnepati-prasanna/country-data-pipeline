"""Scrape the first 20 countries from the trainer's target website."""
import math
import requests
from bs4 import BeautifulSoup

from database import CountryDatabaseManager

SOURCE_URL = "https://www.scrapethissite.com/pages/simple/"
COUNTRY_LIMIT = 20
REQUEST_TIMEOUT_SECONDS = 20


def scrape_countries(limit: int = COUNTRY_LIMIT) -> list[dict]:
    """Fetch and parse country records, converting values to numeric types."""
    response = requests.get(
        SOURCE_URL,
        timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": "CountryDataCapstone/1.0 (educational project)"},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    country_cards = soup.select(".country")

    if not country_cards:
        raise RuntimeError(
            "No country cards were found. The website's HTML structure may have changed."
        )

    countries = []
    for card in country_cards[:limit]:
        name_node = card.select_one(".country-name")
        capital_node = card.select_one(".country-capital")
        population_node = card.select_one(".country-population")
        area_node = card.select_one(".country-area")

        if not all((name_node, capital_node, population_node, area_node)):
            raise RuntimeError("A country record is missing one or more expected fields.")

        name = name_node.get_text(" ", strip=True)
        capital = capital_node.get_text(" ", strip=True)
        population_text = population_node.get_text(" ", strip=True).replace(",", "")
        area_text = area_node.get_text(" ", strip=True).replace(",", "")

        try:
            population = int(float(population_text))
            area = float(area_text)
        except ValueError as exc:
            raise RuntimeError(
                f"Could not convert population/area to numbers for {name!r}."
            ) from exc

        if not math.isfinite(area) or population < 0 or area < 0:
            raise RuntimeError(f"Invalid numeric data found for {name!r}.")

        countries.append({
            "name": name,
            "capital": capital,
            "population": population,
            "area": area,
        })

    if len(countries) != min(limit, len(country_cards)):
        raise RuntimeError("The scraper did not produce the expected number of records.")
    return countries


def main() -> None:
    countries = scrape_countries()
    database = CountryDatabaseManager()
    for country in countries:
        database.upsert_country(country)

    print(f"Scraped and saved {len(countries)} countries from {SOURCE_URL}")
    for country in countries:
        print(
            f"- {country['name']}: capital={country['capital']}, "
            f"population={country['population']:,}, area={country['area']:,.2f} sq. km"
        )


if __name__ == "__main__":
    main()
