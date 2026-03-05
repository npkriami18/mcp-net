"""
Root Domain Routing Agent

This agent determines which domain MCP should handle a user's query.

Domains:
- Data Domain
- Dev Domain
- Utility Domain

Architecture:

Client
  ↓
Root MCP
  ↓
Root Routing Agent (this file)
  ↓
Domain MCP
   ├ Data Domain MCP
   ├ Dev Domain MCP
   └ Utility Domain MCP
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from domains import DOMAINS

API_KEY = ""
API_ENDPOINT = ""

custom_openai_model = LiteLlm(
    model="azure/gpt-5",
    api_key=API_KEY,
    api_base=API_ENDPOINT
)

# ------------------------------
# Dynamic Tool Generation
# ------------------------------

def make_domain_routing_tool(domain_name: str, domain_info: dict):
    """Generates a routing function for a given domain dynamically."""

    def routing_tool(query: str, confidence: float) -> dict:
        """
        Args:
            query (str): User request
            confidence (float): Confidence score between 0.0 and 1.0 indicating
                                 how well this domain matches the user's intent.
        """
        return {
            "status": "success",
            "node_type": "intermediate",
            "service_name": domain_name,
            "endpoint": domain_info["endpoint"],
            "description": domain_info.get("description", ""),
            "confidence": confidence,
            "reason": f"The query was routed to {domain_name}."
        }

    routing_tool.__name__ = f"route_to_{domain_name}"
    routing_tool.__doc__ = f"""
    Routes queries to {domain_name}.

    {domain_info.get("description", "")}

    Args:
        query (str): User request.
        confidence (float): Confidence score between 0.0 and 1.0 indicating
                            how well this domain matches the user's intent.
                            Example: 0.95 means highly confident this is the right domain.

    Returns:
        dict: Routing result with service_name, endpoint, confidence score, and node_type.
    """

    return routing_tool


dynamic_tools = [
    make_domain_routing_tool(domain_name, domain_info)
    for domain_name, domain_info in DOMAINS.items()
]

# ------------------------------
# Build dynamic domain descriptions for instructions
# ------------------------------

domain_descriptions = "\n".join(
    f"- **{name}**: {info.get('description', 'No description provided.')}"
    for name, info in DOMAINS.items()
)

# ------------------------------
# Root Routing Agent
# ------------------------------

root_agent = Agent(
    model=custom_openai_model,
    name="root_domain_router_agent",
    description=(
        "Routes user queries to the correct MCP domain."
    ),
    instruction=f"""
You are the root routing agent in a hierarchical MCP architecture.

Your task is to determine which DOMAIN should handle the user's request.

# Available Domains

{domain_descriptions}

# Decision Guidelines

Choose the correct routing tool based on the user's intent and the domain descriptions above.

# Confidence Score

You must provide a confidence score (0.0 to 1.0) when calling a routing tool:
- 0.9 - 1.0 : Query clearly matches the domain capabilities.
- 0.7 - 0.89: Query likely matches but has some ambiguity.
- 0.5 - 0.69: Query partially matches, best available option.
- Below 0.5 : Query does not clearly match any domain.

# Output Format

Always return a structured JSON response from the selected tool.

Never invent endpoints.
Always use one of the available routing tools.
Always provide a confidence score.
""",
    tools=dynamic_tools,
)