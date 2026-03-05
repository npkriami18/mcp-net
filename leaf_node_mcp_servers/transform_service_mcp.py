from mcp.server.fastmcp import FastMCP
import csv
import json
import xml.etree.ElementTree as ET
from io import StringIO

mcp = FastMCP("transform-service-mcp")


@mcp.tool()
def csv_to_json(data: list[dict]) -> dict:
    """
    CSV → JSON Transformation Tool

    PURPOSE
    -------
    Converts tabular CSV-style data into JSON format.

    This tool expects the **structured output of a CSV Loader tool**,
    where rows are represented as a list of dictionaries.

    INPUT FORMAT
    ------------
    data : list[dict]

    Example input:

    [
        {"name": "Alice", "age": "30", "city": "Bangalore"},
        {"name": "Bob", "age": "25", "city": "Delhi"}
    ]

    OUTPUT FORMAT
    -------------
    dict

    {
        "format": "json",
        "transformed_data": <JSON object>,
        "file_recommendation": {
            "suggested_filename": "output.json",
            "file_extension": ".json",
            "instructions": "Steps for client to save file"
        }
    }

    CLIENT INSTRUCTIONS
    -------------------
    The client should:

    1. Create a new file named "output.json".
    2. Serialize the `transformed_data` field as JSON.
    3. Write the serialized JSON string to the file.
    4. Save it on the user’s device.

    EXAMPLE CLIENT IMPLEMENTATION
    -----------------------------

    Python example:

        with open("output.json", "w") as f:
            json.dump(transformed_data, f, indent=2)

    RESULT
    ------
    Returns the JSON representation and clear file creation instructions.
    """

    return {
        "format": "json",
        "transformed_data": data,
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
def json_to_csv(data: list[dict]) -> dict:
    """
    JSON → CSV Transformation Tool

    PURPOSE
    -------
    Converts JSON structured data into CSV format.

    INPUT FORMAT
    ------------
    data : list[dict]

    Example input:

    [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]

    OUTPUT FORMAT
    -------------
    dict

    {
        "format": "csv",
        "transformed_data": "<csv_string>",
        "file_recommendation": {...}
    }

    CSV OUTPUT EXAMPLE
    ------------------

    name,age
    Alice,30
    Bob,25

    CLIENT FILE CREATION INSTRUCTIONS
    ---------------------------------

    1. Create a file named "output.csv".
    2. Write the `transformed_data` string into the file.
    3. Ensure UTF-8 encoding.
    4. Save the file.

    Python example:

        with open("output.csv", "w") as f:
            f.write(csv_string)
    """

    if not data:
        raise ValueError("Input JSON list is empty.")

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

    csv_string = output.getvalue()

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
def json_to_xml(data: list[dict], root_element: str = "items") -> dict:
    """
    JSON → XML Transformation Tool

    PURPOSE
    -------
    Converts JSON structured data into XML format.

    INPUT FORMAT
    ------------
    data : list[dict]

    Example:

    [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]

    root_element : str (optional)

    Defines the root XML tag.

    OUTPUT FORMAT
    -------------
    dict

    {
        "format": "xml",
        "transformed_data": "<xml_string>",
        "file_recommendation": {...}
    }

    XML OUTPUT EXAMPLE
    ------------------

    <items>
        <item>
            <name>Alice</name>
            <age>30</age>
        </item>
        <item>
            <name>Bob</name>
            <age>25</age>
        </item>
    </items>

    CLIENT FILE CREATION INSTRUCTIONS
    ---------------------------------

    1. Create a file named "output.xml".
    2. Write the transformed_data XML string.
    3. Save using UTF-8 encoding.

    Example:

        with open("output.xml", "w") as f:
            f.write(xml_string)
    """

    root = ET.Element(root_element)

    for row in data:
        item = ET.SubElement(root, "item")
        for key, value in row.items():
            field = ET.SubElement(item, key)
            field.text = str(value)

    xml_string = ET.tostring(root, encoding="unicode")

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