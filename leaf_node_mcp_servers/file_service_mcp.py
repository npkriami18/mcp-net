from mcp.server.fastmcp import FastMCP

import csv
import json
import xml.etree.ElementTree as ET
import requests
from io import StringIO
from urllib.parse import urlparse
import os


mcp = FastMCP("file-service-mcp")


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
        "row_count": int,
        "columns": list[str],
        "data": list[dict]
    }
    """

    content = read_file(file_url)

    reader = csv.DictReader(StringIO(content))
    rows = list(reader)

    return {
        "format": "csv",
        "row_count": len(rows),
        "columns": reader.fieldnames,
        "data": rows
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
        "data": parsed_json
    }
    """

    content = read_file(file_url)

    parsed = json.loads(content)

    return {
        "format": "json",
        "data": parsed
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
        "data": nested_dict
    }
    """

    content = read_file(file_url)

    root = ET.fromstring(content)

    def xml_to_dict(element):
        children = list(element)

        if not children:
            return element.text

        result = {}
        for child in children:
            result.setdefault(child.tag, []).append(xml_to_dict(child))

        return result

    return {
        "format": "xml",
        "root_tag": root.tag,
        "data": xml_to_dict(root)
    }