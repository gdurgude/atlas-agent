import os

import pytest
from dotenv import load_dotenv
from mcp import Client

from app.server import mcp


load_dotenv()


@pytest.mark.anyio
async def test_get_orders_over_amount():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_orders_over_amount",
            {
                "min_amount": 500,
                "api_key": os.getenv("MCP_API_KEY"),
            },
        )

        assert result.is_error is False

        data = result.structured_content["result"]

        assert len(data) == 2
        assert data[0]["name"] == "Bob Smith"
        assert data[1]["name"] == "Alice Johnson"


@pytest.mark.anyio
async def test_get_customer_orders():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_customer_orders",
            {
                "customer_name": "Alice Johnson",
                "api_key": os.getenv("MCP_API_KEY"),
            },
        )

        assert result.is_error is False

        data = result.structured_content["result"]

        assert len(data) == 2
        assert data[0]["name"] == "Alice Johnson"


@pytest.mark.anyio
async def test_negative_order_amount():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_orders_over_amount",
            {
                "min_amount": -100,
                "api_key": os.getenv("MCP_API_KEY"),
            },
        )

        assert result.is_error is True


@pytest.mark.anyio
async def test_empty_customer_name():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_customer_orders",
            {
                "customer_name": "",
                "api_key": os.getenv("MCP_API_KEY"),
            },
        )

        assert result.is_error is True


@pytest.mark.anyio
async def test_invalid_api_key():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_orders_over_amount",
            {
                "min_amount": 500,
                "api_key": "wrong-key",
            },
        )

        assert result.is_error is True