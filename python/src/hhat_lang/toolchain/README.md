# Toolchain

Command-line interface and project management utilities for creating and running H-hat projects.

## Overview

The toolchain provides the `hat` CLI command, built with [Typer](https://typer.tiangolo.com/) and styled with [Rich](https://rich.readthedocs.io/). It supports creating new H-hat projects with the required directory structure, creating new source and type files, and running projects.

## Directory Structure

```
toolchain/
  __init__.py
  cli/
    __init__.py
    cli.py            # Typer CLI app with hat commands (new, run, help)
  project/
    __init__.py
    new.py            # Project and file creation
    run.py            # Project execution (not yet implemented)
    update.py         # Project updates (not yet implemented)
    utils.py          # str_to_path utility
  notebooks/          # Jupyter integration (placeholder)
    __init__.py
```

## Module Details

### cli/cli.py

Defines the `hat` CLI application:

**`hat --version` / `hat -v`** -- Prints the version (0.1.0) and exits.

**`hat new <project_name>`** -- Creates a new H-hat project with the standard directory template:
```
project_name/
  src/
    main.hat            # Entry point
    hat_types/          # Type definition files
    hat_docs/
      main.hat.md       # Documentation for main.hat
      hat_types/        # Documentation for type files
  tests/
```

**`hat new -f <file_name>`** -- Creates a new `.hat` file and its corresponding documentation file within an existing project. Must be run from within a project directory (one containing `src/main.hat`).

**`hat new -t <type_file>`** -- Creates a new type definition file in `src/hat_types/` with a matching documentation file.

**`hat run`** -- Runs the current project (locates `src/main.hat` via `get_proj_dir()`). Currently calls `run_project()`, which is not yet implemented.

**`hat help [command]`** -- Shows available commands or detailed help for a specific command.

**`get_proj_dir()`** -- Searches upward from the current directory for a folder containing `src/main.hat` to locate the project root. Raises `ValueError` if not found.

### project/new.py

- **`create_new_project(project_name)`** -- Creates the full project directory template (folders and files). Note: there is a commented-out `proofs/` directory in the template -- once formal verification is incorporated into H-hat, this will be re-enabled.
- **`create_new_file(project_name, file_name)`** -- Creates a `.hat` file and its `hat_docs/` documentation counterpart
- **`create_new_type_file(project_name, file_name)`** -- Creates a type file in `hat_types/` and its documentation

### project/run.py

**`run_project()`** -- Stub. Raises `NotImplementedError`. Intended to parse `main.hat`, build IR, and execute via the dialect's interpreter.

### project/update.py

**`update_project(project_name)`** -- Stub. Intended for updating/regenerating documentation files for existing project files.

### project/utils.py

**`str_to_path(obj)`** -- Converts a `str` or `Path` to a resolved `Path` object.

## Connections

- **[`../dialects/heather/parsing/`](../dialects/heather/parsing/)**: `run_project()` will use the dialect's parser to process `.hat` files
- **[`../dialects/heather/interpreter/`](../dialects/heather/interpreter/)**: `run_project()` will use the dialect's evaluator for execution

## Design Notes

**Project discovery**: `get_proj_dir()` searches upward from the current working directory for a folder containing `src/main.hat`. This means all `hat` commands that operate on a project (like `hat run`) can be invoked from any subdirectory within the project, similar to how `git` finds the `.git` directory.

**Documentation pairing**: Every `.hat` source file gets a corresponding `.hat.md` documentation file under `hat_docs/`. The `hat new -f` and `hat new -t` commands automatically create both, enforcing this convention from the start.

## Current Status

Project creation (`hat new`) is fully functional. The CLI framework is in place with proper error handling and styled output. `hat run` and project updates are not yet implemented.
