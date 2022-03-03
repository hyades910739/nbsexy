import pathlib
import re
from pathlib import Path
from typing import Iterable, List, Set

# reference: https://github.com/nbQA-dev/nbQA/blob/master/nbqa/__main__.py#L45

EXCLUDES = (
    r"/("
    r"\.direnv|\.eggs|\.git|\.hg|\.ipynb_checkpoints|\.mypy_cache|\.nox|\.svn|\.tox|\.venv|"
    r"_build|buck-out|build|dist|venv"
    r")/"
)


def collect_files_contain_given_suffix_from_paths(
    paths: Iterable[str], suffix: str = ".ipynb"
) -> Set[str]:
    result = set()
    if not suffix.startswith("."):
        suffix = "." + suffix
    for p in paths:
        path = Path(p)
        if path.is_dir():
            cur = _iter_dir_and_get_all_files_with_given_suffix(path, suffix)
            cur = _filter_exclude_patterns(cur)
            result.update(cur)
        else:
            if path.suffix == suffix:
                result.add(str(path.resolve()))
    return result


def exclude_path_by_glob_patterns(
    paths: Iterable[str], exclude_patterns: List[str], base_path=None
) -> List[str]:
    """
    base_path: if you want to aviod matching pattern from absolute path, you can specify a base_path to make paths become relative.
    """
    if isinstance(exclude_patterns, str):
        exclude_patterns = [exclude_patterns]
    res = []
    for path in paths:
        posix_path = (
            Path(path).relative_to(base_path) if base_path is not None else Path(path)
        )
        have_pattern = any(posix_path.match(p) for p in exclude_patterns)
        if not have_pattern:
            res.append(path)
    return res


def _iter_dir_and_get_all_files_with_given_suffix(
    path: pathlib.PosixPath, suffix: str
) -> Iterable[str]:

    assert path.is_dir(), f"given path is not a dir: {str(path)}"
    return (str(i.resolve()) for i in path.rglob("*" + suffix))


def _filter_exclude_patterns(paths: Iterable[str]) -> Iterable[str]:
    return filter(lambda path: not re.search(EXCLUDES, path), paths)
