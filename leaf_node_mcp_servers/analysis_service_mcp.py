from mcp.server.fastmcp import FastMCP
import statistics
import json
import re
from collections import Counter

mcp = FastMCP("analysis-service-mcp")


@mcp.tool()
def repo_analyzer(repo_structure: dict) -> dict:
    """
    Repository Structure Analyzer

    PURPOSE
    -------
    Analyzes a repository structure and returns insights such as
    number of files, number of directories, and file type distribution.

    INPUT FORMAT
    ------------
    repo_structure : dict

    Expected structure:

    {
        "files": [
            "src/main.py",
            "src/utils.py",
            "README.md",
            "requirements.txt"
        ]
    }

    OUTPUT FORMAT
    -------------
    dict

    {
        "analysis_type": "repository",
        "file_count": int,
        "file_extensions": {extension: count},
        "summary": str,
        "file_recommendation": {...}
    }

    CLIENT FILE CREATION INSTRUCTIONS
    ---------------------------------

    If the user wishes to persist the analysis:

    1. Create a file named "repo_analysis.json".
    2. Serialize the returned result as JSON.
    3. Save the file locally.

    Example:

        with open("repo_analysis.json", "w") as f:
            json.dump(result, f, indent=2)
    """

    files = repo_structure.get("files", [])

    extension_counter = Counter()

    for f in files:
        parts = f.split(".")
        if len(parts) > 1:
            extension_counter[parts[-1]] += 1

    return {
        "analysis_type": "repository",
        "file_count": len(files),
        "file_extensions": dict(extension_counter),
        "summary": f"The repository contains {len(files)} files.",
        "file_recommendation": {
            "suggested_filename": "repo_analysis.json",
            "file_extension": ".json",
            "instructions": [
                "Create a file named 'repo_analysis.json'",
                "Serialize the result object as JSON",
                "Write the JSON to the file",
                "Save it on the user's device"
            ]
        }
    }


@mcp.tool()
def text_analyzer(text: str) -> dict:
    """
    Text Analyzer Tool

    PURPOSE
    -------
    Performs simple natural language analysis on input text.

    The tool computes:

    - word count
    - sentence count
    - most frequent words

    INPUT FORMAT
    ------------
    text : str

    Example:

    "MCP servers allow agents to discover and use tools dynamically."

    OUTPUT FORMAT
    -------------
    dict

    {
        "analysis_type": "text",
        "word_count": int,
        "sentence_count": int,
        "top_words": list[(word, count)],
        "file_recommendation": {...}
    }

    CLIENT FILE CREATION INSTRUCTIONS
    ---------------------------------

    To store the analysis:

    1. Create a file named "text_analysis.json".
    2. Serialize the returned dictionary as JSON.
    3. Save locally.

    Example:

        with open("text_analysis.json", "w") as f:
            json.dump(result, f, indent=2)
    """

    words = re.findall(r"\b\w+\b", text.lower())
    sentences = re.split(r"[.!?]+", text)

    word_count = len(words)
    sentence_count = len([s for s in sentences if s.strip()])

    counter = Counter(words)
    top_words = counter.most_common(5)

    return {
        "analysis_type": "text",
        "word_count": word_count,
        "sentence_count": sentence_count,
        "top_words": top_words,
        "file_recommendation": {
            "suggested_filename": "text_analysis.json",
            "file_extension": ".json",
            "instructions": [
                "Create a file named 'text_analysis.json'",
                "Serialize the analysis result as JSON",
                "Write the JSON content to the file",
                "Save the file locally"
            ]
        }
    }


@mcp.tool()
def statistics_analyzer(numbers: list[float]) -> dict:
    """
    Numerical Statistics Analyzer

    PURPOSE
    -------
    Performs statistical analysis on a list of numbers.

    Computes:

    - mean
    - median
    - minimum
    - maximum
    - standard deviation

    INPUT FORMAT
    ------------
    numbers : list[float]

    Example:

    [10, 20, 30, 40, 50]

    OUTPUT FORMAT
    -------------
    dict

    {
        "analysis_type": "statistics",
        "count": int,
        "mean": float,
        "median": float,
        "min": float,
        "max": float,
        "std_dev": float,
        "file_recommendation": {...}
    }

    CLIENT FILE CREATION INSTRUCTIONS
    ---------------------------------

    To store the results:

    1. Create a file named "statistics_analysis.json".
    2. Serialize the result dictionary as JSON.
    3. Save to disk.

    Example:

        with open("statistics_analysis.json", "w") as f:
            json.dump(result, f, indent=2)
    """

    if not numbers:
        raise ValueError("Input number list cannot be empty.")

    return {
        "analysis_type": "statistics",
        "count": len(numbers),
        "mean": statistics.mean(numbers),
        "median": statistics.median(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "std_dev": statistics.stdev(numbers) if len(numbers) > 1 else 0,
        "file_recommendation": {
            "suggested_filename": "statistics_analysis.json",
            "file_extension": ".json",
            "instructions": [
                "Create a file named 'statistics_analysis.json'",
                "Serialize the result dictionary as JSON",
                "Write JSON to the file",
                "Save the file locally"
            ]
        }
    }