import json
from json.decoder import JSONDecodeError
from operator import le, lt
from typing import Any, Dict, List


def load_json(file: str) -> Dict:
    with open(file, "rt") as f:
        text = f.read()
    try:
        vals = json.loads(text)
    except JSONDecodeError:
        # print(f'fail to decode file to JSON: {file}')
        raise
    return vals


def is_ascending(vals: List[Any], strict=True) -> bool:
    "check if val is ascending"
    if len(vals) == 1:
        return True

    op = le if strict else lt
    prev = vals[0]
    for val in vals[1:]:
        if op(val, prev):
            return False
        else:
            prev = val
    return True


def get_cells_count(ipynb_filename: str) -> int:
    nb = load_json(ipynb_filename)
    count = len([1 for cell in nb["cells"] if cell["cell_type"] == "code"])
    return count


def check_execution_count_is_ascending(nb_json: Dict[str, Any]) -> bool:
    execution_counts = (
        cell["execution_count"]
        for cell in nb_json["cells"]
        if cell["cell_type"] == "code"
    )
    execution_counts = [i for i in execution_counts if i is not None]
    if len(execution_counts) == 0:
        return True
    return is_ascending(execution_counts)


def check_cell_count_not_exceed_max_count(
    nb_json: Dict[str, Any], max_cell_count: int
) -> bool:
    count = len([1 for cell in nb_json["cells"] if cell["cell_type"] == "code"])
    return count < max_cell_count


def check_nb_contains_markdown_cell(nb_json: Dict[str, Any]) -> bool:
    return len([1 for c in nb_json["cells"] if c["cell_type"] == "markdown"]) > 0


def check_all_code_cell_not_exceed_max_count(
    nb_json: Dict[str, Any], max_line_in_cell: int
):
    counts = [len(c["source"]) for c in nb_json["cells"] if c["cell_type"] == "code"]
    return all(count < max_line_in_cell for count in counts)


def check_total_line_from_code_cell_not_exceed_max_count(
    nb_json: Dict[str, Any], max_total_line_in_nb: int
):
    counts = [len(c["source"]) for c in nb_json["cells"] if c["cell_type"] == "code"]
    return sum(counts) < max_total_line_in_nb
