import argparse
from operator import attrgetter
from textwrap import dedent
from typing import Dict, List, Tuple

from nbsexy.checks import available_checks

USAGE = dedent(
    f"""\

    nbsexy - check your notebook format. You can specify path and check_flag to conduct checks on certain notebook files.

    Checks:
        Currently, there are five check flags available:
            *  --cell_count
            *  --is_ascending
            *  --has_md
            *  --line_in_cell
            *  --total_line_in_nb
    Examples:
        nbsexy . --cell_count --is_ascending
        nbsexy a.ipynb b.ipynb --has_md
        nbsexy a.ipynb b.ipynb --line_in_cell --max_line_in_cell 100
    """
)


class ParserGetter:
    flag_and_required_args_dict: Dict[str, Tuple[str]] = {
        "cell_count": ("max_cell_count",),
        "is_ascending": [],
        "has_md": [],
        "line_in_cell": (),
        "total_line_in_nb": [],
    }

    def __init__(self):
        raise NotImplementedError("not for create instance")

    @staticmethod
    def get_args() -> argparse.Namespace:
        parser, namespace, _ = ParserGetter._create_argparser()
        ParserGetter._assert_at_least_one_check_is_called(parser, namespace)
        return namespace

    @staticmethod
    def _assert_at_least_one_check_is_called(
        parser: argparse.ArgumentParser, namespace: argparse.Namespace
    ) -> None:
        if not any(attrgetter(check)(namespace) for check in available_checks):
            parser.error("Please select at least one check!")

    @staticmethod
    def _create_argparser() -> Tuple[
        argparse.ArgumentParser, argparse.Namespace, List[str]
    ]:
        parser = argparse.ArgumentParser(
            description="Check tool on a Jupyter notebook.", usage=USAGE
        )
        # parser.add_argument("command", help="Command to run, e.g. `cell_count`.")
        parser.add_argument(
            "root_dirs", nargs="+", help="Notebooks or directories to run command on."
        )
        parser.add_argument(
            "--cell_count",
            action="store_true",
            help="check number of cell in notebook doesnot exceed provided number, default 20.",
        )
        parser.add_argument(
            "--is_ascending",
            action="store_true",
            help="check the cell number(execution_counts) is in ascending order.",
        )
        parser.add_argument(
            "--has_md",
            action="store_true",
            help="check notebook has at least one markdown cell",
        )
        parser.add_argument(
            "--line_in_cell",
            action="store_true",
            help="check all code cell in notebook have lines less than `--max_line_in_cell`",
        )
        parser.add_argument(
            "--total_line_in_nb",
            action="store_true",
            help="check sum of lines in all code cells doesnot exceed `max_total_line_in_nb`",
        )
        parser.add_argument(
            "--max_line_in_cell",
            nargs="?",
            help="the maximum lines acceptable for all code cell in notebook, default 300.",
            default=300,
            type=int,
        )
        parser.add_argument(
            "--max_total_line_in_nb",
            nargs="?",
            help="the maximum lines acceptable for all lines in notebook's code cell combined, default 1000.",
            default=1000,
            type=int,
        )
        parser.add_argument(
            "--max_cell_count",
            nargs="?",
            help="the maximum number of code cell acceptable in a notebook, default 20.",
            default=20,
            type=int,
        )
        parser.add_argument(
            "--exclude_patterns",
            nargs="+",
            help="Exclude notebook with certain filename patterns, note that some pattern is already filtered, like nb in .git/ and .ipynb_checkpoints/",
            default=list(),
        )

        namespace, other_args = parser.parse_known_args()
        return parser, namespace, other_args
