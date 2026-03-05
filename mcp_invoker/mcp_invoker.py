#!/usr/bin/env python3

import asyncio
import sys
import logging
import uuid
import json
import traceback
from concurrent.futures import ThreadPoolExecutor

from mcp.server.fastmcp import FastMCP
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agent import tool_planner_agent


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

mcp = FastMCP("mcp-invoker")

session_service = InMemorySessionService()

executor = ThreadPoolExecutor(max_workers=4)

TOOL_CACHE = {}


def _safe_json_parse(raw: str):

    try:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
        return json.loads(raw)
    except Exception:
        return None


def _run_agent_sync(prompt: str):

    try:

        session_id = str(uuid.uuid4())

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(
            session_service.create_session(
                app_name="mcp-invoker",
                session_id=session_id,
                user_id="mcp_user",
            )
        )

        runner = Runner(
            agent=tool_planner_agent,
            app_name="mcp-invoker",
            session_service=session_service,
        )

        result = runner.run(
            user_id="mcp_user",
            session_id=session_id,
            new_message=Content(parts=[Part.from_text(text=prompt)]),
        )

        response_text = ""

        for event in result:
            if event.is_final_response():
                response_text = event.content.parts[0].text
                break

        return response_text

    except Exception as e:
        return f"Agent Error: {str(e)}"


async def plan_execution(query, tools):

    tool_specs = []

    for tool in tools:
        tool_specs.append({
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        })

    prompt = f"""
User Query:
{query}

Available Tools:
{json.dumps(tool_specs, indent=2)}

Choose the correct tool and generate arguments.

Return JSON only.
"""

    loop = asyncio.get_event_loop()

    raw = await loop.run_in_executor(
        executor,
        _run_agent_sync,
        prompt
    )

    parsed = _safe_json_parse(raw)

    if parsed is None:
        raise Exception("Planner returned invalid JSON")

    return parsed


async def invoke_remote(endpoint: str, query: str):

    if not endpoint.startswith("http"):
        raise ValueError("Invalid MCP endpoint")

    async with streamablehttp_client(endpoint) as streams:

        read_stream = streams[0]
        write_stream = streams[1]

        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()

            if endpoint in TOOL_CACHE:
                tools = TOOL_CACHE[endpoint]
            else:
                tools_result = await session.list_tools()
                tools = tools_result.tools
                TOOL_CACHE[endpoint] = tools

            logging.info(f"Discovered tools: {[t.name for t in tools]}")

            plan = await plan_execution(query, tools)

            tool_name = plan["tool_name"]
            arguments = plan.get("arguments", {})

            logging.info(f"Selected tool: {tool_name}")
            logging.info(f"Arguments: {arguments}")

            result = await asyncio.wait_for(
                session.call_tool(tool_name, arguments),
                timeout=60
            )

            if hasattr(result, "content"):

                parts = []

                for item in result.content:
                    if hasattr(item, "text"):
                        parts.append(item.text)

                return "\n".join(parts)

            return str(result)


@mcp.tool()
async def invoke_mcp(endpoint: str, prompt: str) -> str:

    """
    Universal MCP tool executor.

    INPUT
    -----

    endpoint : str
        Target MCP server endpoint

    prompt : str
        Natural language request

    OUTPUT
    -----

    str
        Result returned by executed MCP tool
    """

    try:
        return await invoke_remote(endpoint, prompt)

    except Exception as e:
        return f"Invoker Error: {str(e)}\n{traceback.format_exc()}"