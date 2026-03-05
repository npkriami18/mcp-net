DOMAINS = {
    "data_domain": {
        "endpoint": "http://localhost:20000/data-domain-service-mcp/mcp",
        "description": (
            "Handles all operations related to data processing, "
            "data loading, format transformations, analysis, and computations."
        ),
        "capabilities": [
            "load dataset",
            "read csv",
            "read json",
            "transform data",
            "convert csv json",
            "data analysis",
            "statistics",
            "calculate numbers"
        ],
    },

    "dev_domain": {
        "endpoint": "http://localhost:20000/dev-domain-service-mcp/mcp",
        "description": (
            "Handles software development related tasks including "
            "repository inspection, code analysis, debugging assistance, "
            "and development workflows."
        ),
        "capabilities": [
            "analyze repository",
            "code analysis",
            "review code",
            "debug program",
            "software development"
        ],
    },

    "utility_domain": {
        "endpoint": "http://localhost:20000/utility-domain-service-mcp/mcp",
        "description": (
            "Handles general utility operations such as calculations, "
            "averages , matrix operations, date/time operations, string processing, and miscellaneous tasks."
        ),
        "capabilities": [
            "utility tasks",
            "date operations",
            "string processing",
            "general tools"
        ],
    },
}

DOMAIN_NAMES = list(DOMAINS.keys())
