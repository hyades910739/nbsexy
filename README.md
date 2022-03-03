# nbsexy:

*  nbsexy is a little tool to check whether your notebook is clean and readable (and also, sexy). You can use it either as a CLI tool or pre-commit hook.

### Install (for now):
```
pip install nbsexy
```

### Checks:

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

### Use pre-commit hook:

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
    rev: 0.0.7
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
