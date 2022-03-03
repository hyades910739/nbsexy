import os
from pathlib import Path

import pytest

import nbsexy
from nbsexy.path_helper import (
    _filter_exclude_patterns,
    _iter_dir_and_get_all_files_with_given_suffix,
    collect_files_contain_given_suffix_from_paths,
    exclude_path_by_glob_patterns,
)

root_path, _ = os.path.split(os.path.split(nbsexy.__file__)[0])


@pytest.mark.parametrize(
    "patterns,expect_count",
    [
        (["*valid*"], 0),
        (["*/path_for_test/*"], 0),
        (["*some_pattern*"], 1),
        (["*valid"], 1),
        (["*valid", "*some_pattern*"], 1),
        (["*valid*", "*some_pattern*"], 0),
        (["*valid*", "**some_pattern*"], 0),
    ],
)
def test_exclude_path_by_glob_patterns_correct(patterns, expect_count):
    target_path = os.path.join(root_path, "tests", "integration", "path_for_test")
    res = collect_files_contain_given_suffix_from_paths([target_path])
    # when:

    count = len(exclude_path_by_glob_patterns(res, patterns))
    assert count == expect_count


def test_collect_files_contain_given_suffix_from_paths_correct():

    target_path = os.path.join(root_path, "tests", "integration", "path_for_test")
    res = collect_files_contain_given_suffix_from_paths([target_path])
    assert len(res) == 1
    assert list(res)[0] == os.path.join(target_path, "valid_nb_1.ipynb")


def test_input_non_dir_to_iter_dir_and_get_all_files_with_given_suffix_should_raise():
    with pytest.raises(AssertionError):
        _ = _iter_dir_and_get_all_files_with_given_suffix(
            Path("some_weird_path.qq"), ".qq"
        )
