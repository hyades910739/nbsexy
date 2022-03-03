import sys
from argparse import Namespace
from operator import attrgetter
from typing import List

from colorama import init

from nbsexy.args import ParserGetter
from nbsexy.checks import CheckFactory, CheckRunner, available_checks
from nbsexy.path_helper import (
    collect_files_contain_given_suffix_from_paths,
    exclude_path_by_glob_patterns,
)


def main() -> int:

    args_ = ParserGetter.get_args()
    files = _get_ipynb_filenames(args_)
    if len(files) == 0:
        print("WARNING: FOUND 0 NOTEBOOKS!!!")
        return 0
    else:
        runner = CheckRunner(args_)
        run_flags = []

        # iter checks and run check for all files one of a time.
        for check_name in available_checks:
            if attrgetter(check_name)(args_):
                check = CheckFactory.get_check(check_name)
                flag = runner.run(files, check)
                run_flags.append(flag)

        # if any flag is 1 (one of file failed check), then return 1
        return int(any(run_flags))


def _get_ipynb_filenames(args_: Namespace) -> List[str]:
    files = collect_files_contain_given_suffix_from_paths(args_.root_dirs, ".ipynb")
    if len(args_.exclude_patterns) > 0:
        files = exclude_path_by_glob_patterns(files, args_.exclude_patterns)
    return list(files)


if __name__ == "__main__":
    init(autoreset=True)
    res = main()
    sys.exit(res)
