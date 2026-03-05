from mcp.server.fastmcp import FastMCP

import csv
import json
import xml.etree.ElementTree as ET
import requests
from io import StringIO
from urllib.parse import urlparse
import os


mcp = FastMCP("file-service-mcp")


# ---------------------------------------------------------------------
# Output Limits
# ---------------------------------------------------------------------

MAX_ROWS = 50          # Max rows returned for CSV
MAX_CHARS = 5000       # Max characters for JSON/XML output
MAX_XML_CHILDREN = 50  # Max children per XML node


# ---------------------------------------------------------------------
# File Reader
# ---------------------------------------------------------------------

def read_file(file_url: str) -> str:
    """
    Reads a file from either:
    1) Public URL (http/https)
    2) Local file path

    Parameters
    ----------
    file_url : str

    Examples
    --------
    URL:
        https://example.com/data/users.csv

    Local file:
        /Users/pranay/data/users.csv
        ./data/users.csv

    Returns
    -------
    str
        File content as text.
    """

    parsed = urlparse(file_url)

    # Case 1 — URL
    if parsed.scheme in ("http", "https"):
        response = requests.get(file_url, timeout=15)
        response.raise_for_status()
        return response.text

    # Case 2 — Local file
    if os.path.exists(file_url):
        with open(file_url, "r", encoding="utf-8") as f:
            return f.read()

    raise ValueError(f"Invalid path or URL: {file_url}")


# ---------------------------------------------------------------------
# Truncation Metadata Helper
# ---------------------------------------------------------------------

def _truncation_meta(total: int, returned: int, unit: str = "rows") -> dict:
    """
    Build a metadata dict describing truncation status.

    Parameters
    ----------
    total : int
        Total number of items available.
    returned : int
        Number of items actually returned.
    unit : str
        Label for the unit (e.g. "rows", "chars").

    Returns
    -------
    dict
        {
            "truncated": bool,
            "total_{unit}": int,
            "returned_{unit}": int
        }
    """
    return {
        "truncated": total > returned,
        f"total_{unit}": total,
        f"returned_{unit}": returned,
    }


# ---------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------

@mcp.tool()
def csv_loader(file_url: str) -> dict:
    """
    CSV Loader

    Reads a CSV file from either a local path or URL and converts it
    into structured dictionary data.

    Parameters
    ----------
    file_url : str

    Examples
    --------
    URL:
        https://example.com/data/users.csv

    Local:
        /Users/pranay/data/users.csv

    Returns
    -------
    dict

    {
        "format": "csv",
        "total_rows": int,
        "returned_rows": int,
        "truncated": bool,
        "columns": list[str],
        "data": list[dict]      # limited to MAX_ROWS
    }
    """

    content = read_file(file_url)

    reader = csv.DictReader(StringIO(content))
    rows = list(reader)

    truncated_rows = rows[:MAX_ROWS]

    return {
        "format": "csv",
        "columns": reader.fieldnames,
        "data": truncated_rows,
        **_truncation_meta(len(rows), len(truncated_rows), "rows"),
    }


@mcp.tool()
def json_loader(file_url: str) -> dict:
    """
    JSON Loader

    Reads JSON from a URL or local file.

    Parameters
    ----------
    file_url : str

    Returns
    -------
    dict

    {
        "format": "json",
        "truncated": bool,
        "total_chars": int,
        "returned_chars": int,
        "data": parsed_json | str   # truncated string if too large
    }
    """

    content = read_file(file_url)
    parsed = json.loads(content)

    serialized = json.dumps(parsed, indent=2)
    total_chars = len(serialized)

    if total_chars > MAX_CHARS:
        return {
            "format": "json",
            "data": serialized[:MAX_CHARS],
            **_truncation_meta(total_chars, MAX_CHARS, "chars"),
        }

    return {
        "format": "json",
        "data": parsed,
        **_truncation_meta(total_chars, total_chars, "chars"),
    }


@mcp.tool()
def xml_loader(file_url: str) -> dict:
    """
    XML Loader

    Reads XML from URL or local path and converts it to a nested dict.

    Parameters
    ----------
    file_url : str

    Returns
    -------
    dict

    {
        "format": "xml",
        "root_tag": str,
        "truncated": bool,
        "total_chars": int,
        "returned_chars": int,
        "data": nested_dict | str   # truncated string if too large
    }
    """

    content = read_file(file_url)
    total_chars = len(content)

    root = ET.fromstring(content)

    def xml_to_dict(element):
        children = list(element)

        if not children:
            return element.text

        result = {}
        for child in children[:MAX_XML_CHILDREN]:
            result.setdefault(child.tag, []).append(xml_to_dict(child))

        return result

    data = xml_to_dict(root)
    serialized = json.dumps(data)
    serialized_chars = len(serialized)

    if serialized_chars > MAX_CHARS:
        return {
            "format": "xml",
            "root_tag": root.tag,
            "data": serialized[:MAX_CHARS],
            **_truncation_meta(total_chars, MAX_CHARS, "chars"),
        }

    return {
        "format": "xml",
        "root_tag": root.tag,
        "data": data,
        **_truncation_meta(total_chars, total_chars, "chars"),
    }
