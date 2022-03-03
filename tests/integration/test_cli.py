import os
import subprocess
from subprocess import PIPE

import nbsexy

root_path, _ = os.path.split(os.path.split(nbsexy.__file__)[0])
notebook_base_path = os.path.join(root_path, "tests", "integration", "notebooks")


def test_zero_notebook_found_will_exit_0_with_warning():
    path = os.path.join(notebook_base_path, "empty_dir")
    output = subprocess.run(
        ["nbsexy", path, "--cell_count"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.stdout == "WARNING: FOUND 0 NOTEBOOKS!!!\n"
    assert output.returncode == 0


def test_no_root_dir_provided_will_exit():
    output = subprocess.run(
        ["nbsexy", "--cell_count"], stdout=PIPE, stderr=PIPE, universal_newlines=True
    )
    last_line = output.stderr.strip().split("\n")[-1]
    expected = "nbsexy: error: the following arguments are required: root_dirs"
    assert last_line == expected


def test_no_check_flag_provided_will_exit():
    output = subprocess.run(
        ["nbsexy", "."], stdout=PIPE, stderr=PIPE, universal_newlines=True
    )
    last_line = output.stderr.strip().split("\n")[-1]
    expected = "nbsexy: error: Please select at least one check!"
    assert last_line == expected


def test_one_check_success_will_exit_with_0():
    path = os.path.join(notebook_base_path, "successed")
    output = subprocess.run(
        ["nbsexy", path, "--cell_count"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.stdout != "WARNING: FOUND 0 NOTEBOOKS!!!\n"
    assert output.returncode == 0


def test_several_check_success_will_exit_with_0():
    path = os.path.join(notebook_base_path, "successed")
    output = subprocess.run(
        ["nbsexy", path, "--cell_count", "--has_md"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.stdout != "WARNING: FOUND 0 NOTEBOOKS!!!\n"
    assert output.returncode == 0


def test_wrong_order_should_exit_1():
    path = os.path.join(notebook_base_path, "failed", "nb_with_wrong_order.ipynb")
    output = subprocess.run(
        ["nbsexy", path, "--is_ascending"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.returncode == 1


def test_one_of_check_for_one_file_failed_should_exit_1():
    path = os.path.join(notebook_base_path, "failed", "nb_with_wrong_order.ipynb")
    output = subprocess.run(
        ["nbsexy", path, "--is_ascending", "--has_md"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.returncode == 1


def test_one_of_check_for_several_file_failed_should_exit_1():
    path1 = os.path.join(notebook_base_path, "failed", "nb_with_wrong_order.ipynb")
    path2 = os.path.join(notebook_base_path, "successed", "valid_nb_1.ipynb")
    output = subprocess.run(
        ["nbsexy", path1, path2, "--is_ascending", "--cell_count"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.returncode == 1


def test_exclude_patterns_do_exclude():
    path1 = os.path.join(notebook_base_path, "failed", "nb_with_wrong_order.ipynb")
    path2 = os.path.join(notebook_base_path, "successed", "valid_nb_1.ipynb")
    output = subprocess.run(
        [
            "nbsexy",
            path1,
            path2,
            "--is_ascending",
            "--cell_count",
            "--exclude_patterns",
            "failed/*",
        ],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.returncode == 0


def test_exclude_patterns_that_match_no_one_should_not_exclude_anything():
    path1 = os.path.join(notebook_base_path, "failed", "nb_with_wrong_order.ipynb")
    path2 = os.path.join(notebook_base_path, "successed", "valid_nb_1.ipynb")
    output = subprocess.run(
        [
            "nbsexy",
            path1,
            path2,
            "--is_ascending",
            "--cell_count",
            "--exclude_patterns",
            "some_weird_pattern/*",
        ],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.returncode == 1
