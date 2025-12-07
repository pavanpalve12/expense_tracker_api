from pathlib import Path as path
import json

def _compute_column_widths(data) -> dict:
    """
    Compute the maximum width of each column in a list of dictionaries.

    Args:
        - data (list[dict]): List of dictionaries containing tabular data.
                             Each key represents a column name.

    Returns:
        dict: A dictionary mapping each column name to its maximum width,
              calculated based on both the header name and the longest value.
    """

    widths = {}
    for key in data[0].keys():
        lengths = []
        max_len = 0
        for idx, item in enumerate(data):
            value = str(data[idx][key])
            lengths.append(len(value))

        widths[key] = max(max(lengths), len(key))
    return widths


def _build_border(columns, widths, style) -> str:
    """
    Build a horizontal border line for the table according to the chosen style.

    Args:
        - columns (iterable): Column names in display order.
        - widths (dict): Mapping of column names to their computed widths.
        - style (str, optional): Border style.
            One of the following:
                - "simple"       → uses only dashes ('-') -> -------
                - "grid"         → uses '+' at intersections -> +----+----+
                - "simple_grid"  → hybrid with '+' at ends only -> +------+
            Defaults to "simple_grid".

    Returns:
        str: The formatted border string.
    """

    if style == "simple":
        return "-" + "-".join("-" * (widths[k] + 2) for k in columns) + "-"
    if style == "grid":
        return "+" + "+".join("-" * (widths[k] + 2) for k in columns) + "+"
    if style == "simple_grid":
        return "+" + "-".join("-" * (widths[k] + 2) for k in columns) + "+"


def _build_row(row_dict, widths) -> list:
    """
    Construct a formatted table row and its corresponding border.

    Args:
        - row_dict (dict): Dictionary representing a single table row.
                           Keys correspond to column names.
        - widths (dict): Mapping of column names to their computed widths.

    Returns:
        tuple[str, str]: A tuple containing:
            - The formatted table row string with padded cells.
            - The border line string for visual separation.
    """
    cells = []
    for key, value in row_dict.items():
        val = str(value)
        padding = " " * (widths[key] - len(str(value)))
        cells.append(f" {val}{padding} ")

    curr_row = "|" + "|".join(cells) + "|"
    return curr_row


def display_data_table(data, style="simple_grid") -> bool:
    """
    Render tabular data in a clean, fixed-width text table.

    Args:
        - data (list[dict]): List of dictionaries where each dict represents
                             a table row (key = column name, value = cell value).

    Returns:
        - bool: True if the table was rendered successfully, False if the input
                data was empty.

    Notes:
        - Automatically computes column widths based on content.
        - Prints header row followed by each data row.
        - Supports multiple border styles via `_build_border`.
    """
    if not data:
        print("Data is empty")
        return False
    widths = _compute_column_widths(data)

    # header row: pass dict as {widths[key] = widths[key]} treat key as cell value for header
    # header_row = _build_row(dict(zip(widths.keys(), widths.keys())), widths)

    border = _build_border(widths.keys(), widths, style)
    header_dict = dict(zip(widths.keys(), widths.keys()))
    rows_list = [header_dict] + data
    for idx, dict_item in enumerate(rows_list):
        curr_row = _build_row(dict_item, widths)

        # print top row only for first row (header row)
        if idx == 0:
            print(border)
        print(curr_row)
        print(border)