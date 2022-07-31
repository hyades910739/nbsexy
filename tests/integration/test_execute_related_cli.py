import os
import subprocess
from subprocess import PIPE

import pytest
from papermill import PapermillExecutionError

import nbsexy

root_path, _ = os.path.split(os.path.split(nbsexy.__file__)[0])
notebook_base_path = os.path.join(root_path, "tests", "integration", "notebooks")


def test_unknown_kernelspec_should_fail():
    path = os.path.join(notebook_base_path, "failed", "nb_with_unknown_kernel_name.ipynb")
    output = subprocess.run(
        ["nbsexy", path, "--execute", "--execute_without_parameters"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )

    assert output.returncode == 1
    assert "jupyter_client.kernelspec.NoSuchKernel" in output.stdout


def test_empty_kernelspec_should_fail():
    path = os.path.join(notebook_base_path, "failed", "nb_without_kernel_name.ipynb")
    output = subprocess.run(
        ["nbsexy", path, "--execute", "--execute_without_parameters"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.returncode == 1
    assert "No kernel name found in notebook and no override provided" in output.stdout


def test_execute_without_parameter_success():
    path = os.path.join(notebook_base_path, "successed", "valid_nb_1.ipynb")
    output = subprocess.run(
        ["nbsexy", path, "--execute"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.returncode == 0

def test_execute_with_notebook_that_read_files_success():
    path = os.path.join(notebook_base_path, "successed", "notebook_that_read_file.ipynb")
    output = subprocess.run(
        ["nbsexy", path, "--execute"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.returncode == 0

def test_execute_with_parameter_but_no_parameter_in_nb_success():
    path = os.path.join(notebook_base_path, "successed", "valid_nb_1.ipynb")
    output = subprocess.run(
        ["nbsexy", path, "--execute", "--execute_without_parameters"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.returncode == 0


def test_execute_with_parameter_success():
    path = os.path.join(notebook_base_path, "successed", "parameterd_notebook_example.ipynb")
    output = subprocess.run(
        ["nbsexy", path, "--execute"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.returncode == 0


def test_execute_without_parameter_while_theres_parameter_success():
    # TODO: how to know that parameter is not used.
    path = os.path.join(notebook_base_path, "successed", "parameterd_notebook_example.ipynb")
    output = subprocess.run(
        ["nbsexy", path, "--execute", "--execute_without_parameters"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.returncode == 0


def test_execute_nb_with_params_and_parameters_tag_exist_but_parameters_tag_doesnot_will_assert():
    path = os.path.join(notebook_base_path, "failed", "nb_with_nbsexy_param_but_without_parm.ipynb")
    output = subprocess.run(
        ["nbsexy", path, "--execute"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    msg = 'No cell with "parameters" tag found!'
    assert msg in output.stdout
    assert "AssertionError" in output.stdout
    assert output.returncode == 1


def test_execute_nb_without_params_and_parameters_tag_exist_but_parameters_tag_doesnot_will_success():
    path = os.path.join(notebook_base_path, "failed", "nb_with_nbsexy_param_but_without_parm.ipynb")
    output = subprocess.run(
        ["nbsexy", path, "--execute", "--execute_without_parameters"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.returncode == 0


def test_execute_with_parameter_but_parameter_not_valid_should_raise():

    path = os.path.join(notebook_base_path, "failed", "nb_with_invalid_parameters.ipynb")
    output = subprocess.run(
        ["nbsexy", path, "--execute"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    msg = "failed to eval parameter fun with value"
    assert msg in output.stdout
    assert "ValueError" in output.stdout
    assert output.returncode == 1


def test_execute_without_parameter_but_parameter_not_valid_should_suceess():
    path = os.path.join(notebook_base_path, "failed", "nb_with_invalid_parameters.ipynb")
    output = subprocess.run(
        ["nbsexy", path, "--execute", "--execute_without_parameters"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert output.returncode == 0

def test_check_run_and_nb_raise_error_during_run_should_raise():
    path = os.path.join(notebook_base_path, "failed", "nb_that_raise_error.ipynb")
    output = subprocess.run(
        ["nbsexy", path, "--execute"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )
    assert "PapermillExecutionError" in output.stdout
    assert "ZeroDivisionError" in output.stdout
    assert output.returncode == 1
