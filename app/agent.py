import asyncio
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from langchain_groq import ChatGroq
from mcp import Client

from app.server import mcp as database_mcp
from app.api_server import mcp as country_mcp


load_dotenv()
MCP_API_KEY = os.getenv("MCP_API_KEY")


llm = ChatGroq(
    model=os.getenv("GROQ_MODEL"),
    temperature=0,
)


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_orders_over_amount",
            "description": "Return customers with orders greater than a given amount.",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_amount": {
                        "type": "number",
                        "description": "Minimum order amount",
                    }
                },
                "required": ["min_amount"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_orders",
            "description": "Return all orders for a customer by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Customer name",
                    }
                },
                "required": ["customer_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_country_info",
            "description": "Return country information such as capital, region, population, and currencies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country_name": {
                        "type": "string",
                        "description": "Country name",
                    }
                },
                "required": ["country_name"],
            },
        },
    },
]

llm_with_tools = llm.bind_tools(tools)


async def run_agent(question: str):
    messages = [
    SystemMessage(
        content="""
You are a data agent.

Always use the available tools when the user asks about:
- customers
- orders
- countries
- capitals
- population
- currencies
- regions

Do not answer these questions from your own knowledge.

Use:
- get_orders_over_amount for order threshold questions
- get_customer_orders for customer order questions
- get_country_info for country information
"""
    ),
    HumanMessage(content=question),
]

    response = await llm_with_tools.ainvoke(messages)
    messages.append(response)

    if not response.tool_calls:
        print("\nAgent:", response.content)
        return

    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        print(f"\nTool selected: {tool_name}")
        print(f"Arguments: {tool_args}")

        if tool_name in {
            "get_orders_over_amount",
            "get_customer_orders",
        }:
            tool_args["api_key"] = MCP_API_KEY

            async with Client(database_mcp) as client:
                result = await client.call_tool(
                    tool_name,
                    tool_args,
            )
        elif tool_name == "get_country_info":
            tool_args["api_key"] = MCP_API_KEY
            async with Client(country_mcp) as client:
                result = await client.call_tool(
                    tool_name,
                    tool_args,
                )

        else:
            print("Unknown tool:", tool_name)
            return

        if result.is_error:
            print("Tool failed:", result.content)
            return

        if result.structured_content is not None:
            tool_result = result.structured_content
        else:
            tool_result = result.content

        messages.append(
            ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call["id"],
            )
        )

    final_response = await llm_with_tools.ainvoke(messages)

    print("\nAgent:", final_response.content)


if __name__ == "__main__":
    question = input("Ask the data agent: ")

    asyncio.run(run_agent(question))