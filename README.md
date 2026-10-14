<div align="center">

# MCP Data Agent

**A multi-MCP AI agent that can query PostgreSQL and call an external country API.**

Built to learn how MCP servers, tool calling, validation, authentication, and LLM routing work together in one project.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![MCP](https://img.shields.io/badge/MCP-Multi--Server-purple)
![Tests](https://img.shields.io/badge/Tests-6%20Passing-brightgreen)

</div>

---

## What this project does

MCP Data Agent is a small project I built to understand how an AI agent can work with multiple MCP servers instead of directly talking to a database or external API.

The agent currently works with two different data sources:

- **PostgreSQL MCP server** for customer and order data
- **Country MCP server** for country information from an external API

The LLM decides which tool is needed, calls the correct MCP server, gets the result, and turns it into a normal answer.

### Example questions

```text
Which customers have orders over $500?
```

```text
Show me all orders for Alice Johnson
```

```text
What is the capital of Japan?
```

---

## Architecture

```text
                    ┌──────────────────────┐
                    │        User          │
                    └──────────┬───────────┘
                               │
                               v
                    ┌──────────────────────┐
                    │      Groq LLM        │
                    │   Agent / Router     │
                    └──────────┬───────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  v                         v
       ┌────────────────────┐    ┌────────────────────┐
       │ Database MCP       │    │ Country MCP        │
       │ Server             │    │ Server             │
       └─────────┬──────────┘    └─────────┬──────────┘
                 │                         │
                 v                         v
       ┌────────────────────┐    ┌────────────────────┐
       │ PostgreSQL         │    │ REST Countries API │
       └────────────────────┘    └────────────────────┘
```

This setup keeps database and API logic outside the LLM and gives the agent controlled tools instead.

---

## Features

- Multi-server MCP architecture
- PostgreSQL-backed MCP tools
- External API MCP tool
- Groq-powered tool selection
- Pydantic input validation
- API-key authentication for protected database tools
- Parameterized SQL queries
- Environment-based secret management
- Dockerized PostgreSQL
- Pytest coverage for valid and invalid inputs
- Cleaner error handling for database and API failures

---

## MCP Tools

### `get_orders_over_amount`

Returns customers with orders above a given amount.

```text
Which customers have orders over $500?
```

### `get_customer_orders`

Returns all orders for a specific customer.

```text
Show me all orders for Alice Johnson
```

### `get_country_info`

Returns country information such as:

- capital
- region
- population
- currencies

```text
What is the capital of Japan?
```

---

## Tech Stack

| Area | Technology |
|---|---|
| Language | Python |
| Agent / LLM | Groq, LangChain |
| MCP | MCP Python SDK |
| Database | PostgreSQL |
| Database Driver | Psycopg |
| Containers | Docker |
| Validation | Pydantic |
| HTTP | Requests |
| Testing | Pytest |
| Config | python-dotenv |

---

## Project Structure

```text
mcp-data-agent/
│
├── app/
│   ├── __init__.py
│   ├── server.py
│   ├── api_server.py
│   └── agent.py
│
├── tests/
│   ├── test_server.py
│   └── test_api_server.py
│
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

---

## How the agent works

For a database question:

```text
User question
    ↓
Groq LLM
    ↓
Selects database MCP tool
    ↓
MCP server validates input + API key
    ↓
PostgreSQL query
    ↓
Tool result
    ↓
LLM formats final answer
```

For a country question:

```text
User question
    ↓
Groq LLM
    ↓
Selects get_country_info
    ↓
Country MCP server
    ↓
External REST API
    ↓
Tool result
    ↓
LLM formats final answer
```

---

## Input Validation

I used Pydantic to validate tool inputs before they reach the database or external API.

Example:

```python
class OrderAmountInput(BaseModel):
    min_amount: float = Field(gt=0)
```

This rejects values such as:

```text
-100
```

before they are used in the database query.

Customer names are also checked so empty input is rejected.

---

## Security

A few basic security decisions are included in the project:

- Database tools require an MCP API key
- Secrets are stored in `.env`
- `.env` is excluded from Git
- The LLM does not receive the MCP secret key directly
- SQL queries use parameters instead of string concatenation
- Inputs are validated before tool execution

Example parameterized query:

```python
WHERE orders.amount > %s
```

This is safer than inserting user input directly into SQL strings.

---

## Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5434
DB_NAME=mcpdb
DB_USER=mcpuser
DB_PASSWORD=your_database_password

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b

REST_COUNTRIES_API_KEY=your_rest_countries_api_key

MCP_API_KEY=your_private_mcp_key
```

> Keep `.env` private and do not commit it to GitHub.

---

## Quick Start

### 1. Create a virtual environment

```powershell
py -m venv .venv
```

### 2. Activate it

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Start PostgreSQL

```powershell
docker compose up -d
```

### 5. Run the agent

```powershell
python -m app.agent
```

You should see:

```text
Ask the data agent:
```

Try:

```text
Which customers have orders over $500?
```

or:

```text
What is the capital of Japan?
```

---

## Tests

Run all tests with:

```powershell
python -m pytest -v
```

Current tests cover:

- successful order lookup
- customer-specific order lookup
- negative amount validation
- empty customer name validation
- invalid MCP API key
- country API response

**Current status: 6 tests passing.**

---

## A few things I learned

The main reason I built this project was to understand MCP beyond just using an existing server.

I learned how to create MCP tools, connect them to PostgreSQL and an external API, and let an LLM decide which tool to use.

I also ran into a few real debugging problems while building it, including Docker port conflicts, PostgreSQL authentication issues, API response changes, and MCP structured output differences.

Working through those problems helped me understand the full flow much better than just building a simple chatbot.

---

## Possible next steps

- Add observability and tracing
- Add more MCP tools
- Add stronger authentication
- Add automatic tool discovery
- Add tool-selection evaluations
- Add request logging
- Add deployment
- Add a small web UI

---

<div align="center">

Built as a hands-on MCP and agent engineering project.

</div>
