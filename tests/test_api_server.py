import pytest
from mcp import Client

from app.api_server import mcp


@pytest.mark.anyio
async def test_get_country_info():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_country_info",
            {"country_name": "Japan"},
        )

        assert result.is_error is False

        data = result.structured_content

        assert data["name"] == "Japan"
        assert data["capital"] == "Tokyo"