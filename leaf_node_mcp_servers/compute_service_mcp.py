from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("compute-service-mcp")


@mcp.tool()
def calculator(a: float, b: float, operation: str) -> dict:
    """
    Basic Calculator Tool

    PURPOSE
    -------
    Performs a basic arithmetic operation between two numbers.

    SUPPORTED OPERATIONS
    --------------------
    add
    subtract
    multiply
    divide

    INPUT FORMAT
    ------------
    a : float
        First number

    b : float
        Second number

    operation : str
        Arithmetic operation to perform.

    Example Inputs
    --------------
    {
        "a": 10,
        "b": 5,
        "operation": "add"
    }

    OUTPUT FORMAT
    -------------
    dict

    {
        "operation": str,
        "inputs": {"a": float, "b": float},
        "result": float,
        "file_recommendation": {...}
    }

    CLIENT FILE CREATION INSTRUCTIONS
    ---------------------------------

    If the user wants to store the computation result:

    1. Create a file named "calculation_result.json".
    2. Serialize the entire returned object as JSON.
    3. Write the JSON into the file.
    4. Save it locally.

    Example:

        with open("calculation_result.json", "w") as f:
            json.dump(result, f, indent=2)
    """

    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        result = a / b
    else:
        raise ValueError("Unsupported operation")

    return {
        "operation": operation,
        "inputs": {"a": a, "b": b},
        "result": result,
        "file_recommendation": {
            "suggested_filename": "calculation_result.json",
            "file_extension": ".json",
            "instructions": [
                "Create a file named 'calculation_result.json'",
                "Serialize the entire result object as JSON",
                "Write JSON to the file",
                "Save the file locally"
            ]
        }
    }


@mcp.tool()
def average_calculator(numbers: list[float]) -> dict:
    """
    Average Calculator Tool

    PURPOSE
    -------
    Computes the arithmetic mean of a list of numbers.

    INPUT FORMAT
    ------------
    numbers : list[float]

    Example:

    [10, 20, 30, 40]

    OUTPUT FORMAT
    -------------
    dict

    {
        "operation": "average",
        "count": int,
        "numbers": list[float],
        "average": float,
        "file_recommendation": {...}
    }

    CLIENT FILE CREATION INSTRUCTIONS
    ---------------------------------

    To store the results:

    1. Create a file named "average_result.json".
    2. Serialize the returned dictionary as JSON.
    3. Write the JSON to the file.
    4. Save locally.
    """

    if not numbers:
        raise ValueError("Numbers list cannot be empty.")

    avg = sum(numbers) / len(numbers)

    return {
        "operation": "average",
        "count": len(numbers),
        "numbers": numbers,
        "average": avg,
        "file_recommendation": {
            "suggested_filename": "average_result.json",
            "file_extension": ".json",
            "instructions": [
                "Create a file named 'average_result.json'",
                "Serialize the returned result as JSON",
                "Write JSON to the file",
                "Save the file locally"
            ]
        }
    }


@mcp.tool()
def matrix_sum(matrix_a: list[list[float]], matrix_b: list[list[float]]) -> dict:
    """
    Matrix Sum Tool

    PURPOSE
    -------
    Computes the element-wise sum of two matrices.

    INPUT FORMAT
    ------------
    matrix_a : list[list[float]]
    matrix_b : list[list[float]]

    Example:

    matrix_a = [
        [1, 2],
        [3, 4]
    ]

    matrix_b = [
        [5, 6],
        [7, 8]
    ]

    OUTPUT FORMAT
    -------------
    dict

    {
        "operation": "matrix_sum",
        "result_matrix": [[...]],
        "file_recommendation": {...}
    }

    RESULT EXAMPLE
    --------------

    [
        [6, 8],
        [10, 12]
    ]

    CLIENT FILE CREATION INSTRUCTIONS
    ---------------------------------

    If the user wishes to save the matrix:

    1. Create a file named "matrix_sum.json".
    2. Serialize the result matrix as JSON.
    3. Write the JSON to the file.
    4. Save locally.
    """

    if len(matrix_a) != len(matrix_b):
        raise ValueError("Matrices must have the same dimensions.")

    result = []

    for row_a, row_b in zip(matrix_a, matrix_b):
        if len(row_a) != len(row_b):
            raise ValueError("Matrix rows must have the same length.")

        result_row = []
        for a, b in zip(row_a, row_b):
            result_row.append(a + b)

        result.append(result_row)

    return {
        "operation": "matrix_sum",
        "result_matrix": result,
        "file_recommendation": {
            "suggested_filename": "matrix_sum.json",
            "file_extension": ".json",
            "instructions": [
                "Create a file named 'matrix_sum.json'",
                "Serialize the result_matrix as JSON",
                "Write JSON to the file",
                "Save the file locally"
            ]
        }
    }