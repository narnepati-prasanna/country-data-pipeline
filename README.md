# End-to-End Country Data Pipeline & Analytics System

A Python capstone project that scrapes the first 20 countries from
[Scrape This Site](https://www.scrapethissite.com/pages/simple/), stores the
records in SQLite, exposes CRUD operations through FastAPI, and uses a client
to export CSV data and generate a scatter plot.

## Features

- Scrapes exactly the first 20 country cards from the target page.
- Converts population to an integer and area to a float.
- Stores records in `countries.db`, using country name as the natural primary key.
- Implements Create, Read, Update, and Delete through `CountryDatabaseManager`.
- Exposes five FastAPI endpoints.
- Uses `requests` and Pandas to fetch and display API data.
- Exports `exported_countries.csv`.
- Saves `population_vs_area.png` with labeled axes, title, and gridlines.

## Project structure

```text
country_data_pipeline/
├── scraper.py
├── database.py
├── main.py
├── client.py
├── requirements.txt
├── .gitignore
└── README.md
```

Generated files (`countries.db`, `exported_countries.csv`, and
`population_vs_area.png`) are created when you run the project. The database
is excluded from Git because it is a generated runtime artifact.

## 1. Create and activate a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

## 2. Scrape and store the first 20 countries

Run from the project directory:

```bash
python scraper.py
```

This creates `countries.db` and inserts or refreshes the first 20 countries.

## 3. Start the FastAPI service

Open a terminal in the project directory, activate the virtual environment, then run:

```bash
uvicorn main:app --reload
```

Useful URLs:

- API root endpoint: `http://127.0.0.1:8000/countries`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

Keep this terminal running while using the client.

## 4. Run the client and generate analytics outputs

Open a second terminal in the project directory, activate the virtual environment, and run:

```bash
python client.py
```

The script prints the DataFrame and creates:

- `exported_countries.csv`
- `population_vs_area.png`

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/countries` | List all countries |
| GET | `/countries/{country_name}` | Retrieve one country by name |
| POST | `/countries` | Create a country |
| PUT | `/countries/{country_name}` | Update capital, population, and area |
| DELETE | `/countries/{country_name}` | Delete a country |

### Example POST body

```json
{
  "name": "Exampleland",
  "capital": "Example City",
  "population": 123456,
  "area": 789.5
}
```

For PUT, send `capital`, `population`, and `area`; the path country name remains
the primary key.

## Troubleshooting

- **No countries returned:** run `python scraper.py` and check the terminal for errors.
- **Connection refused in client:** make sure `uvicorn main:app --reload` is running.
- **Dependency missing:** activate `.venv` and run `pip install -r requirements.txt`.
- **Scraper selectors changed:** inspect the target page and update the selectors in `scraper.py`.

## GitHub submission checklist

- [ ] Run `python scraper.py` successfully.
- [ ] Start the API and test all five endpoints at `/docs`.
- [ ] Run `python client.py`.
- [ ] Confirm both output files are generated.
- [ ] Check that `.venv/`, `__pycache__/`, and `countries.db` are not committed.
- [ ] Push the source files and README to GitHub.
- [ ] Share the repository URL with the trainer.
