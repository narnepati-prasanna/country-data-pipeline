"""Small standard-library tests for the SQLite CRUD layer."""
import tempfile
import unittest
from pathlib import Path

from database import CountryDatabaseManager


class CountryDatabaseManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_countries.db"
        self.database = CountryDatabaseManager(self.db_path)
        self.country = {
            "name": "Testland",
            "capital": "Test City",
            "population": 1000,
            "area": 25.5,
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_and_read_country(self):
        self.database.create_country(self.country)
        self.assertEqual(self.database.get_country("Testland")["population"], 1000)
        self.assertEqual(len(self.database.get_all_countries()), 1)

    def test_update_country(self):
        self.database.create_country(self.country)
        updated = self.database.update_country(
            "Testland",
            {"name": "Testland", "capital": "New City", "population": 2000, "area": 30.0},
        )
        self.assertEqual(updated["capital"], "New City")
        self.assertEqual(updated["population"], 2000)

    def test_delete_country(self):
        self.database.create_country(self.country)
        self.assertTrue(self.database.delete_country("Testland"))
        self.assertIsNone(self.database.get_country("Testland"))
        self.assertFalse(self.database.delete_country("Testland"))

    def test_upsert_does_not_duplicate(self):
        self.database.upsert_country(self.country)
        changed = self.country | {"population": 1500}
        self.database.upsert_country(changed)
        self.assertEqual(len(self.database.get_all_countries()), 1)
        self.assertEqual(self.database.get_country("Testland")["population"], 1500)


if __name__ == "__main__":
    unittest.main()
