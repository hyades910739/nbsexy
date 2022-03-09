import json
import os
import tempfile
from itertools import chain
from json.decoder import JSONDecodeError
from operator import le, lt
from typing import Any, Dict, List, Tuple

import papermill
import papermill as pm
from nbformat.notebooknode import NotebookNode
from papermill import PapermillExecutionError
from papermill.inspection import _open_notebook


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


def check_execution_count_is_ascending(nb_json: Dict[str, Any], **kwargs: Any) -> bool:
    execution_counts = (cell["execution_count"] for cell in nb_json["cells"] if cell["cell_type"] == "code")
    execution_counts = [i for i in execution_counts if i is not None]
    if len(execution_counts) == 0:
        return True
    return is_ascending(execution_counts)


def check_cell_count_not_exceed_max_count(nb_json: Dict[str, Any], max_cell_count: int, **kwargs: Any) -> bool:
    count = len([1 for cell in nb_json["cells"] if cell["cell_type"] == "code"])
    return count < max_cell_count


def check_nb_contains_markdown_cell(nb_json: Dict[str, Any], **kwargs: Any) -> bool:
    return len([1 for c in nb_json["cells"] if c["cell_type"] == "markdown"]) > 0


def check_all_code_cell_not_exceed_max_count(nb_json: Dict[str, Any], max_line_in_cell: int, **kwargs: Any):
    counts = [len(c["source"]) for c in nb_json["cells"] if c["cell_type"] == "code"]
    return all(count < max_line_in_cell for count in counts)


def check_total_line_from_code_cell_not_exceed_max_count(
    nb_json: Dict[str, Any], max_total_line_in_nb: int, **kwargs: Any
):
    counts = [len(c["source"]) for c in nb_json["cells"] if c["cell_type"] == "code"]
    return sum(counts) < max_total_line_in_nb


def check_nb_can_be_run_without_error_raised(nb_json: Dict[str, Any], filename: str, **kwargs: Any):
    parent = _find_file_parent(filename)
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_nb_path = os.path.join(tmpdirname, "job_execute_nb.ipynb")
        try:
            # !!!! try to specify kernel_name wont work since
            # L104 at pm.execute_notebook will load kernelname mannuly
            # from notebook.
            pm.execute_notebook(filename, tmp_nb_path, parameters=dict(), cwd=parent)
        except PapermillExecutionError as ppe:
            raise
            # success = False
        else:
            success = True
    return success


def check_nb_can_be_run_parameterizd_without_error_raised(
    nb_json: Dict[str, Any], filename: str, **kwargs: Any
) -> bool:
    # TODO: fix kernel name issue
    parent = _find_file_parent(filename)
    params = get_nb_params(filename)
    if params:
        print(f"Found parameter: {params}")
    else:
        print(f"{filename}: No parameter found, execute directly.")

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_nb_path = os.path.join(tmpdirname, "job_execute_nb.ipynb")
        try:
            pm.execute_notebook(filename, tmp_nb_path, parameters=params, cwd=parent)
        except PapermillExecutionError as e:
            raise
            # success = False
        else:
            success = True
    return success


def _find_file_parent(filename: str) -> str:
    parent, _ = os.path.split(filename)
    if len(parent) < 1:
        raise ValueError(f"can not find parent for file: {filename}")
    return parent


def _get_nb_params_indice(nb: NotebookNode) -> List[int]:
    '''find 0 or one or many cells with tag "nbsexy-parameters"'''
    nb_parmas_indice = [idx for idx, cell in enumerate(nb.cells) if "nbsexy-parameters" in cell.metadata.tags]
    params_indice = [idx for idx, cell in enumerate(nb.cells) if "parameters" in cell.metadata.tags]
    # if nb_parmas_indice is not None, there should be one and only one parms cell
    if len(nb_parmas_indice) > 0:
        assert len(params_indice) == 1, 'No cell with "parameters" tag found!'
    return nb_parmas_indice


def get_nb_params(filename) -> Dict[str, Any]:
    """
    Get the nbsexy-parameter key:value pair dict
    """
    nb: NotebookNode = _open_notebook(filename, None)
    kernel_name = nb.metadata.kernelspec.name
    language = nb.metadata.kernelspec.language
    translator = papermill.translators.papermill_translators.find_translator(kernel_name, language)
    indice = _get_nb_params_indice(nb)
    params = chain(*(translator.inspect(nb.cells[i]) for i in indice))
    params = {p.name: _try_to_eval(p.name, p.default) for p in params}
    return params


def _try_to_eval(name: str, val: str) -> Any:
    try:
        new = eval(val)
    except Exception:
        raise ValueError(f"failed to eval parameter {name} with value: '{val}'")
    return new
