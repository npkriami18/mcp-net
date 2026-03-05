#!/usr/bin/env python3
"""Root MCP Router Server

This MCP server exposes a tool that forwards user queries to a root routing agent.
The routing agent determines which downstream DOMAIN MCP should handle the request.

The server acts as the top-level router in the MCP hierarchy:

Client
   ↓
Root MCP (this server)
   ↓
Domain MCP
   ├ Data Domain MCP
   ├ Dev Domain MCP
   └ Utility Domain MCP
"""

import asyncio
import sys
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor

from mcp.server.fastmcp import FastMCP
from agent import root_agent

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part


# Suppress warnings to stderr (MCP protocol uses stderr)
logging.basicConfig(level=logging.CRITICAL, stream=sys.stderr)


# Create MCP server
mcp = FastMCP("root-domain-router")


# Session service (shared across requests)
session_service = InMemorySessionService()


# Thread pool executor
executor = ThreadPoolExecutor(max_workers=4)


def _run_agent_sync(prompt: str) -> str:
    """
    Run the root routing agent synchronously inside a worker thread.

    Steps performed:

    1. Create a unique session for the request.
    2. Initialize ADK Runner.
    3. Send the user query to the routing agent.
    4. Extract the final response.

    Parameters
    ----------
    prompt : str

        Natural language query from the user.

        Examples:

            "convert csv dataset to json"
            "analyze this repository"
            "calculate average of numbers"

    Returns
    -------
    str

        JSON string describing the selected domain.

        Expected schema:

        {
          "status": "success",
          "node_type": "intermediate",
          "service_name": string,
          "endpoint": string,
          "description": string,
          "confidence": float,
          "reason": string
        }
    """

    try:
        session_id = str(uuid.uuid4())

        # Create event loop for worker thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Create session
            loop.run_until_complete(
                session_service.create_session(
                    app_name="root-domain-router",
                    session_id=session_id,
                    user_id="mcp_user",
                )
            )

            # Create ADK runner
            runner = Runner(
                agent=root_agent,
                app_name="root-domain-router",
                session_service=session_service,
            )

            # Send prompt to agent
            result = runner.run(
                user_id="mcp_user",
                session_id=session_id,
                new_message=Content(
                    parts=[Part.from_text(text=prompt)]
                ),
            )

            # Extract final response
            response_text = ""

            for event in result:
                if event.is_final_response():
                    response_text = event.content.parts[0].text
                    break

            return response_text if response_text else "No response from routing agent"

        finally:
            loop.close()

    except Exception as e:
        return f"Error executing routing agent: {str(e)}"


@mcp.tool()
async def route_query(prompt: str) -> str:
    """
    Route a user query to the correct domain MCP.

    PURPOSE
    -------
    This tool forwards the user's query to the Root routing agent.
    The agent determines which domain MCP should handle the request.

    The Root MCP does NOT execute tools itself.
    It only performs domain-level routing.

    INPUT
    -----
    prompt : str

        Natural language query.

        Examples:

            "convert csv dataset to json"
            "analyze this repository"
            "calculate matrix sum"
            "debug this code"

    OUTPUT
    ------
    str

        JSON string describing the selected domain.

        Example output:

        {
          "status": "success",
          "node_type": "intermediate",
          "service_name": "data_domain",
          "endpoint": "http://localhost:10000/data-domain-mcp/mcp",
          "description": "Handles data loading and transformation tasks.",
          "confidence": 0.95,
          "reason": "The query was routed to data_domain."
        }

    CLIENT BEHAVIOR
    ---------------

    The MCP client should:

    1. Parse the JSON response.
    2. Extract the "endpoint" field.
    3. Check the "confidence" score before proceeding.
       - confidence >= 0.7 : Proceed with the returned endpoint.
       - confidence < 0.7  : Warn the user or ask for clarification.
    4. Connect directly to that domain MCP.
    5. Discover available tools via MCP native tools/list.
    6. Continue routing inside that domain.

    Example flow:

        Client → Root MCP
               → route_query("convert csv to json")

        Root MCP → Routing Agent
                 → returns domain endpoint with confidence 0.95

        Client → Data Domain MCP (http://localhost:10000/data-domain-mcp/mcp)
               → tools/list → route_data_query()

    ARCHITECTURE ROLE
    -----------------

    This server represents the Root layer in the MCP routing graph.

    Example hierarchy:

        Root MCP (this server)
            ↓
        Domain MCP
            ├ Data Domain MCP
            ├ Dev Domain MCP
            └ Utility Domain MCP
            ↓
        Service MCP
            ↓
        Tool execution
    """

    loop = asyncio.get_event_loop()

    response = await loop.run_in_executor(
        executor,
        _run_agent_sync,
        prompt
    )

    return response