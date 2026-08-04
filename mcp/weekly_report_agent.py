from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.mcp import MCPToolset, StreamableHttpTransport
import asyncio
import os
import logging
from dotenv import load_dotenv

load_dotenv("/srv/agents/.env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    filename="agent.log",      # remove this to log to stdout
    encoding="utf-8",
)

logger = logging.getLogger(__name__)

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

MODEL = require_env("MODEL")
BASE_URL = require_env("LITELLM_BASE_URL")
API_KEY = require_env("LITELLM_API_KEY")
MCP_URL = require_env("MCP_URL")
MCP_API_KEY = require_env("MCP_API_KEY")

model = OpenAIChatModel(
    MODEL,
    provider=OpenAIProvider(
        base_url=BASE_URL,
        api_key=API_KEY,
    ),
)

mcp_toolset = MCPToolset(
    StreamableHttpTransport(
        MCP_URL,
        headers={
            "x-litellm-api-key": f"Bearer {MCP_API_KEY}"
        },
    )
)

agent = Agent(
    model,
    system_prompt="""

    You are a support operations reporting agent.

    Workflow:
        1. Retrieve all required data using MCP tools.
        2. Produce a report in German following the template below.
        3. Send exactly this report using the send_weekly_report_email tool.

    Rules:
        - Use only tool data.
        - Never invent numbers or trends.
        - If data is unavailable, explicitly state "Keine Daten verfügbar".
        - Use Markdown.
        - Highlight KPIs in bold.
        - You are only done, once you sent the e-mails.

    Template:

    # Supportbericht

    ## Offene Tickets
    - **Gesamt:** X
    - **Kategorie A:** X
    - **Kategorie B:** X
    ...

    ## Letzte Woche
    - Neu geöffnete Tickets: ** X
        - **Kategorie A:** X
        - **Kategorie B:** X
        ...

    - Geschlossene Tickets: ** X
        - **Kategorie A:** X
        - **Kategorie B:** X
        ...
    
    - Noch offene Tickets: ** X
        - **Kategorie A:** X
        - **Kategorie B:** X
        ...

    ## Letzter Monat
    - Neu geöffnete Tickets: ** X
        - **Kategorie A:** X
        - **Kategorie B:** X
        ...

    - Geschlossene Tickets: ** X
        - **Kategorie A:** X
        - **Kategorie B:** X
        ...
    
    - Noch offene Tickets: ** X
        - **Kategorie A:** X
        - **Kategorie B:** X
        ...

    ## Analyse
    4-8 factual sentences only.
    """,
    toolsets=[
        mcp_toolset
    ],
)

async def main():
    try:
        async with agent:
            result = await agent.run(
                "Erstelle den Supportbericht der letzten Woche und sende ihn via E-Mail."
            )
            logger.info("Support report created:\n%s", result.output)
    except Exception:
        logger.exception("Failed to generate weekly support report.")


if __name__ == "__main__":
    asyncio.run(main())