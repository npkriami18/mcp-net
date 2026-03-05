from mcp.server.fastmcp import FastMCP
import csv
import json
import xml.etree.ElementTree as ET
from io import StringIO
from typing import Optional
import urllib.request

mcp = FastMCP("transform-service-mcp")


# ---------------------------------------------------------------------
# Internal Helper: Resolve Data
# ---------------------------------------------------------------------

def _resolve_data(url: Optional[str], data: Optional[list]) -> list[dict]:
    """
    Resolve input data from either a URL or a direct list.

    Parameters
    ----------
    url : str, optional
        HTTP/HTTPS URL pointing to a JSON array.
    data : list, optional
        Pre-loaded list of dicts.

    Returns
    -------
    list[dict]
        Resolved data as a list of dictionaries.
    """
    if url:
        with urllib.request.urlopen(url) as response:
            raw = response.read().decode("utf-8")
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                # Some APIs wrap arrays: {"data": [...]}
                for v in parsed.values():
                    if isinstance(v, list):
                        return v
            raise ValueError(f"URL did not return a JSON array: {url}")
    if data:
        return data
    raise ValueError("Either 'url' or 'data' must be provided.")


# ---------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------

@mcp.tool()
def csv_to_json(
    data: Optional[list[dict]] = None,
    url: Optional[str] = None
) -> dict:
    """
    CSV → JSON Transformation Tool

    PURPOSE
    -------
    Converts tabular CSV-style data into JSON format.

    Accepts either:
    - A direct list of dicts via `data`
    - A URL pointing to a JSON array via `url`

    INPUT
    -----
    data : list[dict], optional
        Pre-loaded rows as list of dicts.

    url : str, optional
        HTTP URL to a JSON array resource.
        Example: https://example.com/data.json

    OUTPUT
    ------
    dict
        {
            "format": "json",
            "transformed_data": [...],
            "file_recommendation": {...}
        }
    """
    records = _resolve_data(url, data)

    return {
        "format": "json",
        "transformed_data": records,
        "file_recommendation": {
            "suggested_filename": "output.json",
            "file_extension": ".json",
            "instructions": [
                "Create a file named 'output.json'",
                "Serialize the transformed_data field as JSON",
                "Write the JSON content to the file",
                "Save the file on the user's device"
            ]
        }
    }


@mcp.tool()
def json_to_csv(
    data: Optional[list[dict]] = None,
    url: Optional[str] = None,
    delimiter: Optional[str] = ",",
    include_header: Optional[bool] = True,
    columns: Optional[list[str]] = None,
    output: Optional[str] = "string"
) -> dict:
    """
    JSON → CSV Transformation Tool

    PURPOSE
    -------
    Converts JSON structured data into CSV format.

    Accepts either:
    - A direct list of dicts via `data`
    - A URL pointing to a JSON array via `url`

    INPUT
    -----
    data : list[dict], optional
        Pre-loaded JSON array.

    url : str, optional
        HTTP URL to a JSON array resource.
        Example: https://example.com/data.json

    delimiter : str, optional
        CSV column delimiter. Default: ","

    include_header : bool, optional
        Whether to include the header row. Default: True

    columns : list[str], optional
        Subset of columns to include.
        Example: ["name", "age", "city"]

    output : str, optional
        Output mode. "string" returns CSV as string. Default: "string"

    OUTPUT
    ------
    dict
        {
            "format": "csv",
            "transformed_data": "<csv_string>",
            "file_recommendation": {...}
        }
    """
    records = _resolve_data(url, data)

    if not records:
        raise ValueError("Input data is empty.")

    # Filter columns if specified
    if columns:
        records = [{k: row.get(k, "") for k in columns} for row in records]

    output_io = StringIO()
    fieldnames = list(records[0].keys())
    writer = csv.DictWriter(
        output_io,
        fieldnames=fieldnames,
        delimiter=delimiter or ","
    )

    if include_header:
        writer.writeheader()

    writer.writerows(records)
    csv_string = output_io.getvalue()

    return {
        "format": "csv",
        "transformed_data": csv_string,
        "file_recommendation": {
            "suggested_filename": "output.csv",
            "file_extension": ".csv",
            "instructions": [
                "Create a file named 'output.csv'",
                "Write the transformed_data string into the file",
                "Use UTF-8 encoding",
                "Save the file on the user's device"
            ]
        }
    }


@mcp.tool()
def json_to_xml(
    data: Optional[list[dict]] = None,
    url: Optional[str] = None,
    root_element: Optional[str] = "items",
    item_element: Optional[str] = "item"
) -> dict:
    """
    JSON → XML Transformation Tool

    PURPOSE
    -------
    Converts JSON structured data into XML format.

    Accepts either:
    - A direct list of dicts via `data`
    - A URL pointing to a JSON array via `url`

    INPUT
    -----
    data : list[dict], optional
        Pre-loaded JSON array.

    url : str, optional
        HTTP URL to a JSON array resource.
        Example: https://example.com/data.json

    root_element : str, optional
        Root XML tag name. Default: "items"

    item_element : str, optional
        Per-item XML tag name. Default: "item"

    OUTPUT
    ------
    dict
        {
            "format": "xml",
            "transformed_data": "<xml_string>",
            "file_recommendation": {...}
        }
    """
    records = _resolve_data(url, data)

    root = ET.Element(root_element or "items")

    for row in records:
        item = ET.SubElement(root, item_element or "item")
        for key, value in row.items():
            field = ET.SubElement(item, str(key))
            field.text = str(value) if value is not None else ""

    xml_string = ET.tostring(root, encoding="unicode", xml_declaration=False)

    return {
        "format": "xml",
        "transformed_data": xml_string,
        "file_recommendation": {
            "suggested_filename": "output.xml",
            "file_extension": ".xml",
            "instructions": [
                "Create a file named 'output.xml'",
                "Write the transformed_data XML string into the file",
                "Use UTF-8 encoding",
                "Save the file on the user's device"
            ]
        }
    }
