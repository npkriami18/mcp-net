"""
Dev Domain Routing Agent

This agent determines which downstream MCP service should handle a user's query.

The agent performs semantic reasoning over service descriptions and capabilities
to select the most appropriate service endpoint.

Architecture role:

Client
  ↓
Root MCP
  ↓
Dev Domain MCP
  ↓
Routing Agent (this file)
  ↓
Service MCP (file / analysis)

Reference:
https://google.github.io/adk-docs/tools-custom/
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from leaf_node_services import SERVICES, DEV_DOMAIN_SERVICE_NAMES

API_KEY = ""
API_ENDPOINT = ""

custom_openai_model = LiteLlm(
    model="azure/gpt-5",
    api_key=API_KEY,
    api_base=API_ENDPOINT
)

# ------------------------------
# Service Registry
# ------------------------------

SERVICES = {service_name: SERVICES[service_name] for service_name in DEV_DOMAIN_SERVICE_NAMES}


# ------------------------------
# Dynamic Tool Generation
# ------------------------------

def make_routing_tool(service_name: str, service_info: dict):
    """Generates a routing function for a given service dynamically."""

    def routing_tool(query: str, confidence: float) -> dict:
        """
        Args:
            query (str): User request
            confidence (float): Confidence score between 0.0 and 1.0 indicating
                                 how well this service matches the user's intent.
        """
        return {
            "status": "success",
            "node_type": "leaf",
            "service_name": service_name,
            "endpoint": service_info["endpoint"],
            "description": service_info.get("description", ""),
            "confidence": confidence,
            "reason": f"The query was routed to {service_name}."
        }

    routing_tool.__name__ = f"route_to_{service_name}"
    routing_tool.__doc__ = f"""
    Routes queries to {service_name}.

    {service_info.get("description", "")}

    Args:
        query (str): User request.
        confidence (float): Confidence score between 0.0 and 1.0 indicating
                            how well this service matches the user's intent.
                            Example: 0.95 means highly confident this is the right service.

    Returns:
        dict: Routing result with service name, endpoint, confidence score, and node_type.
    """

    return routing_tool


dynamic_tools = [
    make_routing_tool(service_name, service_info)
    for service_name, service_info in SERVICES.items()
]


# ------------------------------
# Build dynamic service descriptions for instructions
# ------------------------------

service_descriptions = "\n".join(
    f"- **{name}**: {info.get('description', 'No description provided.')}"
    for name, info in SERVICES.items()
)


# ------------------------------
# Routing Agent
# ------------------------------

root_agent = Agent(
    model=custom_openai_model,
    name="dev_domain_router_agent",
    description=(
        "Routes user queries to the correct downstream MCP service "
        "within the Dev Domain."
    ),
    instruction=f"""
You are a service routing agent in a distributed MCP architecture.

Your task is to determine which service MCP should handle the user's request.

# Available Services

{service_descriptions}

# Decision Guidelines

Choose the correct routing tool based on the user's intent and the service descriptions above.

# Confidence Score

You must provide a confidence score (0.0 to 1.0) when calling a routing tool:
- 0.9 - 1.0 : Query clearly matches the service capabilities.
- 0.7 - 0.89: Query likely matches but has some ambiguity.
- 0.5 - 0.69: Query partially matches, best available option.
- Below 0.5 : Query does not clearly match any service.

# Output Format

Always return a structured JSON response from the selected tool.

Never invent services or endpoints.
Always use one of the available routing tools.
Always provide a confidence score.
""",
    tools=dynamic_tools,
)