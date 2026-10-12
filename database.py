"""SQLite persistence layer for country records."""
from pathlib import Path
import sqlite3
from typing import Any


DEFAULT_DB_PATH = Path(__file__).resolve().parent / "countries.db"


class CountryDatabaseManager:
    """Owns all SQLite operations for the countries table."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = str(db_path)
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _create_table(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS countries (
                    name TEXT PRIMARY KEY COLLATE NOCASE,
                    capital TEXT NOT NULL,
                    population INTEGER NOT NULL CHECK (population >= 0),
                    area REAL NOT NULL CHECK (area >= 0)
                )
                """
            )

    @staticmethod
    def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
        return dict(row) if row is not None else None

    @staticmethod
    def _validate_country(country: dict[str, Any]) -> None:
        required = {"name", "capital", "population", "area"}
        missing = required - country.keys()
        if missing:
            raise ValueError(f"Missing country fields: {', '.join(sorted(missing))}")
        if not isinstance(country["name"], str) or not country["name"].strip():
            raise ValueError("Country name must be a non-empty string.")
        if not isinstance(country["capital"], str) or not country["capital"].strip():
            raise ValueError("Capital must be a non-empty string.")
        if isinstance(country["population"], bool) or not isinstance(country["population"], int):
            raise ValueError("Population must be an integer.")
        if country["population"] < 0:
            raise ValueError("Population cannot be negative.")
        if isinstance(country["area"], bool) or not isinstance(country["area"], (int, float)):
            raise ValueError("Area must be numeric.")
        if country["area"] < 0:
            raise ValueError("Area cannot be negative.")

    def create_country(self, country: dict[str, Any]) -> dict[str, Any]:
        """Insert a new record; raises sqlite3.IntegrityError for duplicate names."""
        self._validate_country(country)
        cleaned = {
            "name": country["name"].strip(),
            "capital": country["capital"].strip(),
            "population": int(country["population"]),
            "area": float(country["area"]),
        }
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO countries (name, capital, population, area) VALUES (?, ?, ?, ?)",
                (cleaned["name"], cleaned["capital"], cleaned["population"], cleaned["area"]),
            )
        return cleaned

    def upsert_country(self, country: dict[str, Any]) -> dict[str, Any]:
        """Insert or refresh a scraped country by its natural key."""
        self._validate_country(country)
        cleaned = {
            "name": country["name"].strip(),
            "capital": country["capital"].strip(),
            "population": int(country["population"]),
            "area": float(country["area"]),
        }
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO countries (name, capital, population, area)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    capital = excluded.capital,
                    population = excluded.population,
                    area = excluded.area
                """,
                (cleaned["name"], cleaned["capital"], cleaned["population"], cleaned["area"]),
            )
        return cleaned

    def get_all_countries(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT name, capital, population, area FROM countries ORDER BY name COLLATE NOCASE"
            ).fetchall()
        return [dict(row) for row in rows]

    def get_country(self, country_name: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT name, capital, population, area
                FROM countries WHERE name = ? COLLATE NOCASE
                """,
                (country_name.strip(),),
            ).fetchone()
        return self._row_to_dict(row)

    def update_country(self, country_name: str, country: dict[str, Any]) -> dict[str, Any] | None:
        """Update an existing record without changing its primary-key name."""
        self._validate_country(country)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE countries
                SET capital = ?, population = ?, area = ?
                WHERE name = ? COLLATE NOCASE
                """,
                (
                    country["capital"].strip(),
                    int(country["population"]),
                    float(country["area"]),
                    country_name.strip(),
                ),
            )
            if cursor.rowcount == 0:
                return None
            row = connection.execute(
                """
                SELECT name, capital, population, area
                FROM countries WHERE name = ? COLLATE NOCASE
                """,
                (country_name.strip(),),
            ).fetchone()
        return self._row_to_dict(row)

    def delete_country(self, country_name: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM countries WHERE name = ? COLLATE NOCASE",
                (country_name.strip(),),
            )
        return cursor.rowcount > 0
