"""
MCP Tool Planning Agent
=======================

This agent determines:

1. Which MCP tool should be executed
2. What arguments should be passed to that tool

The agent receives:
- User query
- List of tools
- Tool schemas

Output:

{
  "tool_name": "tool_name",
  "arguments": { ... }
}
"""

import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

API_KEY = ""
API_ENDPOINT = ""


llm_model = LiteLlm(
    model="azure/gpt-5",
    api_key=API_KEY,
    api_base=API_ENDPOINT
)


tool_planner_agent = Agent(
    model=llm_model,
    name="mcp_tool_planner_agent",
    description="Plans execution of MCP tools by selecting the correct tool and generating arguments.",
    instruction="""
You are an MCP tool execution planner.

You will receive:

1. A user query
2. A list of available tools
3. Each tool includes:
   - name
   - description
   - input_schema

Your job:

1. Select the best tool.
2. Generate arguments matching the input_schema.

Rules:

- Return ONLY JSON
- Do NOT explain
- Keys must match schema exactly
- Use values from the query

Output format:

{
  "tool_name": "tool_name",
  "arguments": { ... }
}

Example:

{
  "tool_name": "csv_to_json",
  "arguments": {
    "file_path": "/data/file.csv"
  }
}
"""
)