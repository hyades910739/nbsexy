from argparse import Namespace
from operator import attrgetter
from textwrap import dedent
from typing import Any, Callable, Dict, List, Set, TypeVar, Union

from colorama import Back, Fore, Style

from nbsexy.utils import (
    check_all_code_cell_not_exceed_max_count,
    check_cell_count_not_exceed_max_count,
    check_execution_count_is_ascending,
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
}


class Check:
    """Define a notebook check, and pass to CheckRunner for runing check."""

    def __init__(
        self,
        name: str,
        fun: Callable[[NB_JSON, KWARGS], bool],
        kwargs_list: List[str],
        header_msg: str,
        failed_msg: str,
    ) -> None:
        """
        Args:
            name (str): check name.
            fun (Callable[[NB_JSON, KWARGS], bool]): the function to run. It should return bool, with true
                means that check is passed.
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
    def get_check(name: str) -> Check:
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
        else:
            raise ValueError(f"check not found: {name}")


class CheckRunner:
    "Define general procedure about how to run a check."

    def __init__(self, args: Namespace):
        self._args = args
        self._errored_dict = dict()
        self._flags = list()

    def run(
        self, ipynb_filenames: Union[List[str], Set[str]], check: Check
    ) -> int:
        """Run one check on several notebooks"""

        self._errored_dict = dict()
        self._flags = list()
        kwargs = self._create_kwargs_for_check(check)
        self._print_header_msg(check, kwargs)
        for filename in ipynb_filenames:
            flag = self._run_one_file(filename, check, kwargs)
            self._flags.append(flag)

        run_success_flag = self._fail_handler(check)
        self._error_handler()
        return run_success_flag

    def _print_header_msg(self, check: Check, kwargs: KWARGS) -> None:
        msg = (
            Style.BRIGHT
            + Fore.BLUE
            + f"{check.name}:  {check.header_msg.format(**kwargs)}"
        )
        msg = msg + Style.RESET_ALL + Fore.RESET
        print(msg, end="\n\n")

    def _create_kwargs_for_check(self, check: Check) -> KWARGS:
        "pair the kwargs specified by check instance and argparse.Namespace"
        return {kw: attrgetter(kw)(self._args) for kw in check.kwargs_list}

    def _run_one_file(
        self, filename: str, check: Check, kwargs: KWARGS
    ) -> Union[bool, str]:
        """run check on one file.

        Returns:
            Union[bool, None]: True if sucess, False if check not pass. 'Failed' if error occured.
        """
        try:
            nb_json: NB_JSON = load_json(filename)
            flag = check.fun(nb_json, **kwargs)
        except Exception as e:
            self._record_exception(filename, e)
            flag = "Failed"
        finally:
            self._print_status(filename, flag)
            return flag

    def _record_exception(self, filename: str, e: Exception) -> None:
        self._errored_dict[filename] = f"{type(e)}: {str(e)}"

    def _print_status(self, filename: str, flag: Union[bool, None]) -> None:
        if flag is True:
            color = Fore.GREEN
        elif flag is False:
            color = Fore.RED
        else:
            color = Fore.RED + Back.YELLOW
        print(
            f"  * {filename}: ",
            Style.BRIGHT + color + str(flag) + Fore.RESET + Back.RESET,
        )

    def _fail_handler(self, check: Check) -> int:
        # TODO: run callback function here for more detail.
        """Any one check failed (not error), return 1"""
        for flag in self._flags:
            if flag is False or flag == "Failed":
                print(check.failed_msg)
                return 1
        return 0

    def _error_handler(self):
        for k, v in self._errored_dict.items():
            print(k, v)


cell_count = Check(
    name="cell_count",
    fun=check_cell_count_not_exceed_max_count,
    kwargs_list=["max_cell_count"],
    header_msg="check cell count does not exceed {max_cell_count}: ",
    failed_msg=dedent(
        f"""
        {Fore.RED}
        Some of your notebook have too many cells.
        Try to split these notebooks to multiple notebooks.
        {Fore.RESET}
    """
    ),
)

is_ascending_ = Check(
    name="is_ascending",
    fun=check_execution_count_is_ascending,
    kwargs_list=[],
    header_msg="check the cell number(execution_counts) is in ascending order: ",
    failed_msg=dedent(
        f"""
        {Fore.RED}
        Some of your notebook is in wrong order.
        Try to 'restart and run all' or rearrange your cells.
        {Fore.RESET}
    """
    ),
)

has_md = Check(
    name="has_md",
    fun=check_nb_contains_markdown_cell,
    kwargs_list=[],
    header_msg="check notebook has at least one markdown cell: ",
    failed_msg=dedent(
        f"""
        {Fore.RED}
        Some of your notebook dont have any markdown cell.
        Try to add some markdown cell and write some information about your notebook.
        {Fore.RESET}
    """
    ),
)

line_in_cell = Check(
    name="line_in_cell",
    fun=check_all_code_cell_not_exceed_max_count,
    kwargs_list=["max_line_in_cell"],
    header_msg="check all code cell in notebook have lines less than {max_line_in_cell}: ",
    failed_msg=dedent(
        f"""
        {Fore.RED}
        Some of your notebook have too many lines.
        {Fore.RESET}
    """
    ),
)

total_line_in_nb = Check(
    name="total_line_in_nb",
    fun=check_total_line_from_code_cell_not_exceed_max_count,
    kwargs_list=["max_total_line_in_nb"],
    header_msg="check sum of lines in all code cells doesnot exceed  {max_total_line_in_nb}: ",
    failed_msg=dedent(
        f"""
        {Fore.RED}
        Some of your notebook have too many lines.
        You should consider split your notebook to several notebook with different purpose.
        {Fore.RESET}
    """
    ),
)
