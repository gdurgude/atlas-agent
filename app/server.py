from pydantic import BaseModel, Field
import os
import psycopg

from dotenv import load_dotenv
from mcp.server import MCPServer

load_dotenv()

mcp = MCPServer("MCP Data Agent")
import psycopg
from mcp.server import MCPServer

mcp = MCPServer("MCP Data Agent")

class OrderAmountInput(BaseModel):
    min_amount: float = Field(gt=0)


class CustomerNameInput(BaseModel):
    customer_name: str = Field(min_length=1)


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5434")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
def validate_api_key(api_key: str):
    expected_key = os.getenv("MCP_API_KEY")

    if api_key != expected_key:
        raise ValueError("Invalid API key")


@mcp.tool()
def get_orders_over_amount(min_amount: float, api_key: str) -> list[dict]:
    """Return customers with orders greater than a given amount."""
    validate_api_key(api_key)

    validated = OrderAmountInput(min_amount=min_amount)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    customers.name,
                    customers.email,
                    orders.amount,
                    orders.status
                FROM customers
                JOIN orders
                    ON customers.id = orders.customer_id
                WHERE orders.amount > %s
                ORDER BY orders.amount DESC;
                """,
                (validated.min_amount,),
            )

            rows = cursor.fetchall()

    return [
        {
            "name": row[0],
            "email": row[1],
            "amount": float(row[2]),
            "status": row[3],
        }
        for row in rows
    ]
@mcp.tool()
def get_customer_orders(customer_name: str, api_key: str) -> list[dict]:
    """Return all orders for a customer by name."""
    validate_api_key(api_key)

    validated = CustomerNameInput(
        customer_name=customer_name.strip()
    )

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    customers.name,
                    customers.email,
                    orders.amount,
                    orders.status,
                    orders.created_at
                FROM customers
                JOIN orders
                    ON customers.id = orders.customer_id
                WHERE LOWER(customers.name) = LOWER(%s)
                ORDER BY orders.created_at DESC;
                """,
                (validated.customer_name,),
            )

            rows = cursor.fetchall()

    return [
        {
            "name": row[0],
            "email": row[1],
            "amount": float(row[2]),
            "status": row[3],
            "created_at": row[4].isoformat(),
        }
        for row in rows
    ]


if __name__ == "__main__":
    mcp.run()