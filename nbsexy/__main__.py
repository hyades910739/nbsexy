import math
import shutil
import sys
import time
from argparse import Namespace
from collections import Counter
from operator import attrgetter
from typing import Dict, List, Optional

from colorama import Back, Fore, Style, init

from nbsexy.args import ParserGetter
from nbsexy.checks import CheckFactory, CheckResult, CheckRunner, available_checks
from nbsexy.path_helper import (
    collect_files_contain_given_suffix_from_paths,
    exclude_path_by_glob_patterns,
)


class Launcher:
    "entry point of nbsexy"

    def __init__(self) -> None:
        self.start_time = time.time()
        self.terminal_size = shutil.get_terminal_size()
        self.args_ = ParserGetter.get_args()
        self.verbose = self.args_.verbose

    def run(self) -> int:
        args_ = self.args_
        files = _get_ipynb_filenames(args_)
        selected_check_names = [
            check_name
            for check_name in available_checks
            if attrgetter(check_name)(args_)
        ]

        self._print_header_and_info(n_check=len(selected_check_names), n_nb=len(files))
        check_result_dict: Dict[str, Dict[str, CheckResult]] = dict()
        runner = CheckRunner(args_)

        if len(files) == 0:
            print("FOUND 0 NOTEBOOKS! EXIT.")
            self._print_footer(0, 0, 0)
            return 0

        for check_name in selected_check_names:
            check = CheckFactory.get_check(check_name, args_)
            results = runner.run(files, check)
            check_result_dict[check_name] = results

        # print results:
        self._print_results_for_all_check(runner, check_result_dict)

        # print errors:
        counter = self._count_running_stats(check_result_dict)

        if counter["n_error"] > 0:
            self._print_errors(check_result_dict)

        # print footer
        n_pass, n_failed, n_error = (
            counter["n_pass"],
            counter["n_failed"],
            counter["n_error"],
        )
        self._print_footer(n_pass, n_failed, n_error)

        if n_failed > 0 or n_error > 0:
            return 1
        else:
            return 0

    def _print_results_for_all_check(
        self, runner: CheckRunner, check_result_dict: Dict[str, Dict[str, CheckResult]]
    ) -> None:
        print("")
        print(self._add_separator_to_line(" summary "))
        print("")
        for check_name, results in check_result_dict.items():
            check = CheckFactory.get_check(check_name, self.args_)
            runner.print_check_results(check, results, self.verbose)

    def _print_errors(
        self, check_result_dict: Dict[str, Dict[str, CheckResult]]
    ) -> Dict[str, int]:
        header = self._add_separator_to_line(" errors ")
        print("")
        print(header)
        sep = "-" * self.terminal_size.columns
        for check_name, check_results in check_result_dict.items():
            for filename, check_result in check_results.items():
                if check_result.status == "Error":
                    print("")
                    print(
                        Style.BRIGHT + f"[{check_name}]: {filename}:" + Style.RESET_ALL
                    )
                    print(check_result.info)
                    print(sep)
                    print("")

    def _print_header_and_info(self, n_check: int, n_nb: int) -> None:
        header = self._get_header_line()
        info = f"Found {n_nb} notebooks, and select {n_check} checks."
        print(header)
        print(info)
        print("")

    def _get_header_line(self) -> str:
        title = " nbsexy starts! "
        title = self._add_separator_to_line(title)
        return title

    def _add_separator_to_line(self, line: str, line_len: Optional[int] = None) -> str:
        """
        from: ' This is a Message '
        to: '================== This is a Message =================='
        """
        if line_len is None:
            line_len = len(line)
        n_pad = self.terminal_size.columns - line_len
        pad_left, pad_right = math.ceil(n_pad / 2), math.floor(n_pad / 2)
        new_line = "=" * pad_left + line + "=" * pad_right
        new_line = Fore.YELLOW + new_line + Style.RESET_ALL
        return new_line

    def _count_running_stats(
        self, check_result_dict: Dict[str, Dict[str, CheckResult]]
    ) -> Dict[str, int]:
        """
        Args:
            check_result_dict (Dict[str, Dict[str, CheckResult]]): key 1 is check_name and key2 is filename.
                                                                   i.e. Dict[check_name, Dict[filename, CheckResult]]
        Returns:
            Dict[str, int]: example {'n_pass': 10, 'n_failed': 3, 'n_error':3}
        """
        counter = Counter(
            [
                check_result.status
                for results in check_result_dict.values()
                for check_result in results.values()
            ]
        )

        return {
            "n_pass": counter.get(True, 0),
            "n_failed": counter.get(False, 0),
            "n_error": counter.get("Error", 0),
        }

    def _print_footer(self, n_pass: int, n_failed: int, n_error: int) -> None:
        time_spent = time.time() - self.start_time
        msg = self._get_footer_message(n_pass, n_failed, n_error, time_spent)
        print("")
        print(msg)

    def _get_footer_message(
        self, n_pass: int, n_failed: int, n_error: int, time_spent: float
    ) -> str:
        """
        looks like this:
        ==== 5 passed, 2 failed, 7 error, in 34.12s ====
        """
        passed = f" {n_pass} passed, " if n_pass > 0 else ""
        failed = f"{n_failed} failed, " if n_failed > 0 else ""
        errored = f"{n_error} error, " if n_error > 0 else ""
        spent = f"in {time_spent:.2f}s "

        title_len = len(passed) + len(failed) + len(errored) + len(spent)
        title = (
            Fore.GREEN
            + passed
            + Fore.MAGENTA
            + failed
            + Fore.RED
            + errored
            + Fore.YELLOW
            + spent
        )
        new_title = self._add_separator_to_line(title, line_len=title_len)
        return new_title


def _get_ipynb_filenames(args_: Namespace) -> List[str]:
    files = collect_files_contain_given_suffix_from_paths(args_.root_dirs, ".ipynb")
    if len(args_.exclude_patterns) > 0:
        files = exclude_path_by_glob_patterns(files, args_.exclude_patterns)
    return list(files)


def main():
    return Launcher().run()


if __name__ == "__main__":
    init(autoreset=True)
    res = main()
    sys.exit(res)
