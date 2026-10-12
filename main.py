"""FastAPI service exposing CRUD endpoints for country records."""
import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Path, Response, status
from pydantic import BaseModel, ConfigDict, Field

from database import CountryDatabaseManager


database = CountryDatabaseManager()


class CountryPayload(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    capital: str = Field(min_length=1, max_length=100)
    population: int = Field(ge=0)
    area: float = Field(ge=0, allow_inf_nan=False)


class CountryUpdatePayload(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    capital: str = Field(min_length=1, max_length=100)
    population: int = Field(ge=0)
    area: float = Field(ge=0, allow_inf_nan=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database manager creates the table during initialization.
    yield


app = FastAPI(
    title="Country Data API",
    description="CRUD API for the Country Data Pipeline capstone project.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/countries", response_model=list[CountryPayload])
def get_countries():
    return database.get_all_countries()


@app.get("/countries/{country_name}", response_model=CountryPayload)
def get_country(
    country_name: str = Path(min_length=1, description="Country's natural-key name")
):
    country = database.get_country(country_name)
    if country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return country


@app.post("/countries", response_model=CountryPayload, status_code=status.HTTP_201_CREATED)
def create_country(payload: CountryPayload):
    try:
        return database.create_country(payload.model_dump())
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="A country with this name already exists")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.put("/countries/{country_name}", response_model=CountryPayload)
def update_country(
    payload: CountryUpdatePayload,
    country_name: str = Path(min_length=1, description="Country's natural-key name"),
):
    updated = database.update_country(country_name, payload.model_dump() | {"name": country_name})
    if updated is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return updated


@app.delete("/countries/{country_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(
    country_name: str = Path(min_length=1, description="Country's natural-key name")
):
    if not database.delete_country(country_name):
        raise HTTPException(status_code=404, detail="Country not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
