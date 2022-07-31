from argparse import Namespace
from operator import attrgetter
from textwrap import dedent
from typing import Any, Callable, Dict, List, Set, TypeVar, Union

from colorama import Back, Fore, Style

from nbsexy._checks_fun import (
    CheckResult,
    check_all_code_cell_not_exceed_max_count,
    check_cell_count_not_exceed_max_count,
    check_execution_count_is_ascending,
    check_nb_can_be_run_parameterizd_without_error_raised,
    check_nb_can_be_run_without_error_raised,
    check_nb_contains_markdown_cell,
    check_total_line_from_code_cell_not_exceed_max_count,
    load_json,
)

NB_JSON = Dict[str, Any]  # parsed ipynb content in json format.
# KWARGS: additional keyword arguments for check function.
KWARGS = TypeVar("KWARGS", bound=Dict[str, Any])


available_checks = {
    "cell_count",
    "is_ascending",
    "has_md",
    "line_in_cell",
    "total_line_in_nb",
    "execute",
}


class Check:
    """Define a notebook check, and pass to CheckRunner for runing check."""

    def __init__(
        self,
        name: str,
        fun: Callable[[NB_JSON, KWARGS], CheckResult],
        kwargs_list: List[str],
        header_msg: str,
        failed_msg: str,
    ) -> None:
        """
        Args:
            name (str): check name.
            fun (Callable[[NB_JSON, KWARGS], bool]): the function to run. It should return CheckResult.
            kwargs_list (List[str]): addtional keyword argument names for `fun`.
            header_msg (str): the header message. this message will be printed every time CheckRunner called run.
                Also, kwargs will be sent to message by `format` method, which allow you to get value from argparse.
            failed_msg (str): message printed when at least one file failed to finish check (error raised).
        """
        self.name = name
        self.fun = fun
        self.kwargs_list = kwargs_list
        self.header_msg = header_msg
        self.failed_msg = failed_msg


class CheckFactory:
    "Just a boring factory."

    @staticmethod
    def get_check(name: str, namespace: Namespace) -> Check:
        if name == "cell_count":
            return cell_count
        elif name == "is_ascending":
            return is_ascending_
        elif name == "has_md":
            return has_md
        elif name == "line_in_cell":
            return line_in_cell
        elif name == "total_line_in_nb":
            return total_line_in_nb
        elif name == "execute":
            if namespace.execute_without_parameters is True:
                return execute
            else:
                return execute_with_parameter
        else:
            raise ValueError(f"check not found: {name}")


class CheckRunner:
    "Define general procedure about how to run a check."

    def __init__(self, args: Namespace):
        self._args = args

    def run(
        self, ipynb_filenames: Union[List[str], Set[str]], check: Check
    ) -> Dict[str, CheckResult]:
        """Run one check on several notebooks"""

        kwargs = self._create_kwargs_for_check(check)
        results: Dict[str, CheckResult] = dict()
        for filename in ipynb_filenames:
            # add name to kwargs:
            kwargs["filename"] = filename
            result = self._run_one_file(filename, check, kwargs)
            results[filename] = result
        return results

    def _create_kwargs_for_check(self, check: Check) -> KWARGS:
        "pair the kwargs specified by check instance and argparse.Namespace"
        return {kw: attrgetter(kw)(self._args) for kw in check.kwargs_list}

    def _run_one_file(self, filename: str, check: Check, kwargs: KWARGS) -> CheckResult:
        """run check on one file.

        Returns:
            Union[bool, None]: True if sucess, False if check not pass. 'Error' if error occured.
        """
        try:
            nb_json: NB_JSON = load_json(filename)
            check_result = check.fun(nb_json, **kwargs)
        except Exception as e:
            check_result = self._create_check_result_for_check_that_raised(e)

        return check_result

    def _create_check_result_for_check_that_raised(self, e: Exception):
        return CheckResult(
            status="Error",
            info=f"{type(e)}: {str(e)}",
        )

    def print_check_results(
        self, check: Check, check_results: Dict[str, CheckResult], verbose: bool
    ) -> None:

        self._print_check_results_header(check, check_results)
        if len([c for c in check_results.values() if c.status is False]) > 0:
            print(check.failed_msg)
        for filename, check_result in check_results.items():
            if check_result.status is True and verbose is False:
                pass  # do not print
            else:
                self._print_check_result_for_one_file(filename, check_result)
        print("")

    def _print_check_results_header(
        self, check: Check, check_results: Dict[str, CheckResult]
    ) -> None:
        n_results = len(check_results)
        n_success = len([c for c in check_results.values() if c.status is True])
        kwargs = self._create_kwargs_for_check(check)
        status_style = Fore.RED if n_success != n_results else Fore.GREEN
        status_style = status_style + Style.BRIGHT  # + Back.LIGHTWHITE_EX
        status_msg = (
            " [" + status_style + f"{n_success}" + Style.RESET_ALL + f"/{n_results}]"
        )
        header_msg = (
            Style.BRIGHT
            + f"[CHECKS: {check.name}]:  {check.header_msg.format(**kwargs)}"
            + Style.RESET_ALL
        )
        header_msg = header_msg + status_msg
        print(header_msg)

    def _print_check_result_for_one_file(
        self, filename: str, check_result: CheckResult
    ) -> None:

        if check_result.status is True:
            color = Fore.GREEN
        elif check_result.status is False:
            color = Fore.RED
        else:
            color = Fore.RED + Back.YELLOW
        print(
            f"  * {filename}: ",
            Style.BRIGHT
            + color
            + str(check_result.status)
            + Fore.RESET
            + Back.RESET
            + Style.RESET_ALL,
        )
        if check_result.status is False and len(check_result.info) > 0:
            # prin info:
            print(f"    * {check_result.info}")

    def _print_header_msg(self, check: Check, kwargs: KWARGS) -> None:
        msg = (
            Style.BRIGHT
            + Fore.BLUE
            + f"[CHECKS: {check.name}]:  {check.header_msg.format(**kwargs)}"
        )
        msg = msg + Style.RESET_ALL + Fore.RESET
        print(msg, end="\n\n")


cell_count = Check(
    name="cell_count",
    fun=check_cell_count_not_exceed_max_count,
    kwargs_list=["max_cell_count"],
    header_msg="check cell count does not exceed {max_cell_count}: ",
    failed_msg=dedent(
        f"""{Fore.RED}
        Some of your notebook have too many cells.
        Try to split these notebooks to multiple notebooks.
        {Fore.RESET}"""
    ),
)

is_ascending_ = Check(
    name="is_ascending",
    fun=check_execution_count_is_ascending,
    kwargs_list=[],
    header_msg="check the cell number(execution_counts) is in ascending order: ",
    failed_msg=dedent(
        f"""{Fore.RED}
        Some of your notebook is in wrong order.
        Try to 'restart and run all' or rearrange your cells.
        {Fore.RESET}"""
    ),
)

has_md = Check(
    name="has_md",
    fun=check_nb_contains_markdown_cell,
    kwargs_list=[],
    header_msg="check notebook has at least one markdown cell: ",
    failed_msg=dedent(
        f"""{Fore.RED}
        Some of your notebook dont have any markdown cell.
        Try to add some markdown cell and write some information about your notebook.
        {Fore.RESET}"""
    ),
)

line_in_cell = Check(
    name="line_in_cell",
    fun=check_all_code_cell_not_exceed_max_count,
    kwargs_list=["max_line_in_cell"],
    header_msg="check all code cell in notebook have lines less than {max_line_in_cell}: ",
    failed_msg=dedent(
        f"""{Fore.RED}
        Some of your notebook have too many lines.
        {Fore.RESET}"""
    ),
)

total_line_in_nb = Check(
    name="total_line_in_nb",
    fun=check_total_line_from_code_cell_not_exceed_max_count,
    kwargs_list=["max_total_line_in_nb"],
    header_msg="check sum of lines in all code cells doesnot exceed  {max_total_line_in_nb}: ",
    failed_msg=dedent(
        f"""{Fore.RED}
        Some of your notebook have too many lines.
        You should consider split your notebook to several notebook with different purpose.
        {Fore.RESET}"""
    ),
)

execute = Check(
    name="execute",
    fun=check_nb_can_be_run_without_error_raised,
    kwargs_list=[],
    header_msg="check notebook can be executed and no error raised: ",
    failed_msg=dedent(
        f"""{Fore.RED}
        Some of your notebook failed to execute.
        You should re-run your notebook and make sure no error raised.
        {Fore.RESET}"""
    ),
)
execute_with_parameter = Check(
    name="execute",
    fun=check_nb_can_be_run_parameterizd_without_error_raised,
    kwargs_list=[],
    header_msg="check notebook can be (parametered) executed and no error raised: ",
    failed_msg=dedent(
        f"""{Fore.RED}
        Some of your notebook failed to execute.
        You should re-run your notebook and make sure no error raised.
        {Fore.RESET}"""
    ),
)
