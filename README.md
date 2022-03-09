# nbsexy:

nbsexy is a little tool to check whether your notebook is clean and readable (and also, sexy). You can use it either as a CLI tool or pre-commit hook.

## Install (for now):
```
pip install nbsexy
```

## Checks:

Currently, there are five check flags available:
*  `--cell_count`:
Check number of cell in notebook doesnot exceed certain number (default 20). Too many cells means you proability do too many thing in a single notebook, you can consider split it to several files.

*  `--is_ascending`:
Check the cell number(execution_counts) is in ascending order. Notebook should be able to restart and run again without any error. If the cell number is not in ascending order, error may happend when you try to run it.
*  `--has_md`:
Check notebook has at least one markdown cell. You should use markdown cell to tell everyone the story about this notebook. Otherwise, it just a bunch of unoriginazed codes.

*  `--line_in_cell`:
Check all code cell in notebook have lines less than certain number. Cells with too many lines, just like script with too many lines, make me sick :confounded: .
*  `--total_line_in_nb`
check sum of lines in all code cells doesnot exceed certain number. Like I said, too many line make me sick.

## experimental: execute notebook with (or without) parameter.
### Usage:
With flag `--execute`, you can execute your notebook, if there's any error raised in any cell, nbsexy will exit with return code 1, and label as `failed`.

By default, nbsexy will try to find parameters in notebook (explain below), and execute notebook with these parameters. If you want to execute without using these parameter, you can set flag: `--execute_without_parameters`.

### Parameter Execution:
#### * Why Parameter Execution:

Often, your notebook may have some cells, that will take you hours or even days to execute. It may not be practical to simply re-run these cells when you use nbsexy to execute notebooks.

In this case, you can set some parameters, which can ease or control the cost of computation in your notebook.

Take deep learning training loop as an example, below is a code snippet:

```
N_EPOCH = 50
for epoch in range(N_EPOCH):
    train_a_epoch() # cost a lot of time!!
```
By setting `N_EPOCH=1`, you can limit this training loop run only once when execute. Or you can also set other parameter to control the size of model or amount of training data you load.

#### * How to set parameter:
with the help of [papermill](https://github.com/nteract/papermill), we can parameterize jupyter notebook and then execute it.

To parameterize your notebook, you need to create at least two cell, one with tag `parameters` and one with tag `nbsexy-parameters`. The `nbsexy-parameters` cell should be on top of `parameters` cell.

<img src="https://i.imgur.com/G96q2gX.png" alt="tag" style="max-height:400px;"/>


You can specify parameters you want to use in the `nbsexy-parameters` cell. When nbsexy is called with flag `--execute`, it will replace the "parameters in `parameters` cell" with "parameters in `nbsexy-parameters`", and then execute.

#### * How to Add Tags:
You can find the tag function in the toolbar, it maybe on the left or right base on your jupyterlab's version.

<img src="https://i.imgur.com/JtZcWaK.png" alt="tag" style="max-height:400px;"/>


### Limitation:
* The parameters must be basic types like int, float, str, list, dict, tuple, set. To pass function or object as parameters, you can create a dict mapping and use key as a parameter to select your object. Like this:
<img src="https://i.imgur.com/JThASnq.png" alt="tag" style="max-height:400px;"/>

* You can create as many cells with `nbsexy-parameters` tag as you like, but you can create only one `parameters` cell. And all the `nbsexy-parameters` cell should be on top of `parameters` cells.



## Use nbsexy as pre-commit hook:

1. install pre-commit

```
pip install pre-commit
```

2. edit your `.pre-commit-config.yaml` file, something like...
```
default_language_version:
  python: python3.6
repos:
  - repo: https://github.com/hyades910739/nbsexy
    rev: 0.0.3
    hooks:
      - id: nbsexy-cell-count
        verbose: true
        args: [--max_cell_count=15]
      - id: nbsexy-is-ascending
        verbose: true
      - id: nbsexy-has-md
        verbose: true
      - id: nbsexy-line-in-cell
        verbose: true
      - id: nbsexy-total-line-in-nb
        verbose: true
```

3. install hooks:
```
pre-commit install
```

4. try to run your hook with:
```
pre-commit run --all-files
```
