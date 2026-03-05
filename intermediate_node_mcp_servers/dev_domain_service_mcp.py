#!/usr/bin/env python3
"""Dev Domain MCP Router Server

This MCP server exposes a tool that forwards user queries to a routing agent.
The routing agent determines which downstream MCP service should handle the request.

The server acts as a semantic router in the MCP hierarchy:

Client
   ↓
Root MCP
   ↓
Dev Domain MCP (this server)
   ↓
Service MCP (file / analysis)
"""

import asyncio
import sys
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor

from mcp.server.fastmcp import FastMCP
from dev_domain_agent import root_agent

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part


# Suppress warnings to stderr (MCP protocol uses stderr)
logging.basicConfig(level=logging.CRITICAL, stream=sys.stderr)


# Create MCP server
mcp = FastMCP("dev-domain-router")


# Create session service (shared across requests)
session_service = InMemorySessionService()


# Thread pool executor
executor = ThreadPoolExecutor(max_workers=4)


def _run_agent_sync(prompt: str) -> str:
    """
    Run the ADK routing agent synchronously inside a worker thread.

    Parameters
    ----------
    prompt : str
        Natural language query describing the user's request.

        Examples:
            "analyze this repository"
            "load the csv file"

    Returns
    -------
    str
        JSON string returned by the routing agent.

        Expected schema:
        {
          "status": "success",
          "node_type": "leaf",
          "service_name": string,
          "endpoint": string,
          "description": string,
          "confidence": float,
          "reason": string
        }
    """

    try:
        session_id = str(uuid.uuid4())

        # Create event loop for thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Create session
            loop.run_until_complete(
                session_service.create_session(
                    app_name="dev-domain-router",
                    session_id=session_id,
                    user_id="mcp_user",
                )
            )

            # Create ADK runner
            runner = Runner(
                agent=root_agent,
                app_name="dev-domain-router",
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
async def route_dev_query(prompt: str) -> str:
    """
    Route a user query to the appropriate downstream MCP service.

    PURPOSE
    -------
    This tool forwards the user's query to the Dev Domain routing agent.
    The agent analyzes the query and determines which service MCP should
    handle the request.

    The Dev Domain MCP does NOT execute tools itself.
    It only performs service discovery.

    INPUT
    -----
    prompt : str
        Natural language query from the user.

        Examples:
            "analyze this repository"
            "load this json file"

    OUTPUT
    ------
    str
        JSON string describing the selected service.

        Example output:

        {
          "status": "success",
            "node_type": "leaf",
          "service_name": "analysis_service",
          "endpoint": "http://localhost:10000/analysis-service-mcp/mcp",
          "description": "Analyzes datasets and text content. Supports statistical analysis, text analysis, and repository analysis.",
          "confidence": 0.95,
          "reason": "The query was routed to analysis_service."
        }

    CLIENT BEHAVIOR
    ---------------
    The MCP client receiving this response should:

    1. Parse the JSON response.
    2. Extract the "endpoint" field.
    3. Check the "confidence" score before proceeding.
       - confidence >= 0.7 : Proceed with the returned endpoint.
       - confidence < 0.7  : Warn the user or ask for clarification.
    4. Connect directly to the returned MCP server.
    5. Discover available tools via MCP native tools/list.
    6. Invoke the appropriate tool from that service.

    Example flow:

        Client → Dev Domain MCP
                → route_dev_query("analyze this repository")

        Dev Domain MCP → Agent
                       → returns service endpoint with confidence 0.95

        Client → Analysis Service MCP (http://localhost:10000/analysis-service-mcp/mcp)
                → tools/list → repo_analysis()

    ARCHITECTURE ROLE
    -----------------
    This server represents the Dev Domain layer in the MCP routing graph.

    MCP hierarchy:

        Root MCP
            ↓
        Dev Domain MCP (this server)
            ↓
        Service MCP
            ├ file_service
            └ analysis_service
    """

    loop = asyncio.get_event_loop()

    response = await loop.run_in_executor(
        executor,
        _run_agent_sync,
        prompt
    )

    return response