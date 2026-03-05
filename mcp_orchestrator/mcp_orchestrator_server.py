#!/usr/bin/env python3
"""MCP Orchestrator Server

This MCP server exposes a tool that forwards user queries to the MCP
Orchestrator Agent.

The orchestrator agent coordinates routing and execution across the
distributed MCP network.

Unlike other MCP routers, the orchestrator does not return an endpoint
to the client. Instead, it executes the full routing workflow internally
and returns the final tool result.

Architecture

Client
   ↓
MCP Orchestrator (this server)
   ↓
Root MCP
   ↓
Domain MCP
   ↓
Service MCP
   ↓
Tool Execution
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


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

# MCP protocol uses stderr, so suppress noisy logs
logging.basicConfig(level=logging.CRITICAL, stream=sys.stderr)


# ---------------------------------------------------------
# MCP Server
# ---------------------------------------------------------

mcp = FastMCP("mcp-orchestrator")


# ---------------------------------------------------------
# ADK Session Service
# ---------------------------------------------------------

session_service = InMemorySessionService()


# ---------------------------------------------------------
# Thread Pool
# ---------------------------------------------------------

executor = ThreadPoolExecutor(max_workers=4)


# ---------------------------------------------------------
# Agent Execution
# ---------------------------------------------------------

def _run_agent_sync(prompt: str) -> str:
    """
    Run the MCP orchestrator agent synchronously in a worker thread.

    The orchestrator agent performs multi-hop MCP routing and execution.

    Steps performed:

    1. Send the user query to Root MCP
    2. Receive domain routing metadata
    3. Continue routing through Domain MCP
    4. Reach the leaf Service MCP
    5. Execute the appropriate tool
    6. Return the final tool response

    Parameters
    ----------
    prompt : str

        Natural language user request.

        Examples:

            "convert csv dataset to json"
            "load dataset from url"
            "analyze repository statistics"
            "calculate matrix average"

    Returns
    -------
    str

        Final response returned by the executed MCP tool.

        Example:

            {
              "status": "success",
              "result": "...tool output..."
            }
    """

    try:
        session_id = str(uuid.uuid4())

        # Create new event loop for thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:

            # Create ADK session
            loop.run_until_complete(
                session_service.create_session(
                    app_name="mcp-orchestrator",
                    session_id=session_id,
                    user_id="mcp_user",
                )
            )

            # Initialize runner
            runner = Runner(
                agent=root_agent,
                app_name="mcp-orchestrator",
                session_service=session_service,
            )

            # Send query to orchestrator agent
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

            return response_text if response_text else "No response from orchestrator agent"

        finally:
            loop.close()

    except Exception as e:
        return f"Error executing orchestrator agent: {str(e)}"


# ---------------------------------------------------------
# MCP Tool
# ---------------------------------------------------------

@mcp.tool()
async def orchestrate_query(prompt: str) -> str:
    """
    Execute a user request through the distributed MCP network.

    PURPOSE
    -------
    This tool acts as the single entry point for executing tasks
    in the MCP architecture.

    The orchestrator performs full multi-hop routing and execution
    internally.

    The client does NOT need to manually connect to other MCP servers.

    INPUT
    -----
    prompt : str

        Natural language query.

        Examples:

            "convert csv dataset to json"
            "load dataset from file"
            "analyze repository commits"
            "calculate average of numbers"

    OUTPUT
    ------
    str

        Final response produced by the executed MCP tool.

        Example:

        {
          "status": "success",
          "result": "Converted dataset to JSON successfully"
        }

    CLIENT BEHAVIOR
    ---------------
    The client only needs to:

    1. Send the user query to this MCP server.
    2. Receive the final response.

    The client does NOT need to perform:

    • Domain routing
    • Service discovery
    • Tool selection
    • MCP invocation

    All orchestration happens internally.

    ARCHITECTURE ROLE
    -----------------

    This server represents the top-level execution layer in the MCP system.

    MCP architecture:

        Client
            ↓
        MCP Orchestrator (this server)
            ↓
        Root MCP
            ↓
        Domain MCP
            ↓
        Service MCP
            ↓
        Tool Execution
    """

    loop = asyncio.get_event_loop()

    response = await loop.run_in_executor(
        executor,
        _run_agent_sync,
        prompt
    )

    return response
