import os
import requests
import psycopg
from pydantic import ValidationError

from dotenv import load_dotenv
from mcp.server import MCPServer
from pydantic import BaseModel, Field


load_dotenv()

mcp = MCPServer("Country Info MCP Server")


class CountryInput(BaseModel):
    country_name: str = Field(min_length=1)


class CountryInfo(BaseModel):
    name: str
    capital: str
    region: str | None = None
    population: int | None = None
    currencies: list


@mcp.tool()
def get_country_info(country_name: str) -> CountryInfo:
    """Return basic information about a country."""

    validated = CountryInput(
        country_name=country_name.strip()
    )

    api_key = os.getenv("REST_COUNTRIES_API_KEY")

    response = requests.get(
        "https://api.restcountries.com/countries/v5/names.common/"
        + validated.country_name,
        headers={
            "Authorization": f"Bearer {api_key}"
        },
        timeout=10,
    )

    response.raise_for_status()

    payload = response.json()
    data = payload["data"]["objects"][0]

    return CountryInfo(
        name=data["names"]["common"],
        capital=data.get("capitals", [{}])[0].get("name", "Unknown"),
        region=data.get("region"),
        population=data.get("population"),
        currencies=data.get("currencies", []),
    )


if __name__ == "__main__":
    mcp.run()