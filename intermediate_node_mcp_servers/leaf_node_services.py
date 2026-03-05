SERVICES = {
    "file_service": {
        "endpoint": "http://localhost:10000/file-service-mcp/mcp",
        "description": (
            "Loads datasets from local files or cloud URLs. "
            "Supports CSV, JSON, and XML file parsing and returns structured data."
        ),
        "capabilities": [
            "load file",
            "read csv",
            "read json",
            "read xml",
            "parse dataset"
        ],
    },
    "transform_service": {
        "endpoint": "http://localhost:10000/transform-service-mcp/mcp",
        "description": (
            "Converts data between formats. "
            "Supports CSV to JSON, JSON to CSV, and JSON to XML transformations."
        ),
        "capabilities": [
            "convert csv json",
            "convert json csv",
            "convert json xml",
            "data transformation"
        ],
    },
    "analysis_service": {
        "endpoint": "http://localhost:10000/analysis-service-mcp/mcp",
        "description": (
            "Analyzes datasets and text content. "
            "Supports statistical analysis, text analysis, and repository analysis."
        ),
        "capabilities": [
            "statistics",
            "text analysis",
            "repo analysis"
        ],
    },
     "compute_service": {
        "endpoint": "http://localhost:10000/compute-service-mcp/mcp",
        "description": (
            "Performs mathematical computations including arithmetic operations, "
            "averages, and matrix calculations."
        ),
        "capabilities": [
            "calculate",
            "math",
            "average",
            "matrix"
        ],
    },
}

DATA_DOMAIN_SERVICE_NAMES = ["file_service", "transform_service"]
DEV_DOMAIN_SERVICE_NAMES = ["file_service", "analysis_service"]
UTILITY_DOMAIN_SERVICE_NAMES = ["transform_service", "analysis_service", "compute_service"]